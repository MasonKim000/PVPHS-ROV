"""PID controller and mission sequencer."""

from enum import Enum, auto

import numpy as np


class Phase(Enum):
    DEPLOY = auto()
    DESCEND_1 = auto()
    HOLD_DEEP_1 = auto()
    ASCEND_1 = auto()
    HOLD_SHALLOW_1 = auto()
    DESCEND_2 = auto()
    HOLD_DEEP_2 = auto()
    ASCEND_2 = auto()
    HOLD_SHALLOW_2 = auto()
    SURFACE = auto()
    COMPLETE = auto()


# Phase configuration: (target_depth, hold_duration, arrival_tolerance, next_phase)
PHASE_CONFIG: dict[Phase, tuple[float, float, float, Phase]] = {
    Phase.DEPLOY: (0.0, 3.0, 0.5, Phase.DESCEND_1),
    Phase.DESCEND_1: (2.5, 0.0, 0.2, Phase.HOLD_DEEP_1),
    Phase.HOLD_DEEP_1: (2.5, 30.0, 0.33, Phase.ASCEND_1),
    Phase.ASCEND_1: (0.4, 0.0, 0.2, Phase.HOLD_SHALLOW_1),
    Phase.HOLD_SHALLOW_1: (0.4, 30.0, 0.33, Phase.DESCEND_2),
    Phase.DESCEND_2: (2.5, 0.0, 0.2, Phase.HOLD_DEEP_2),
    Phase.HOLD_DEEP_2: (2.5, 30.0, 0.33, Phase.ASCEND_2),
    Phase.ASCEND_2: (0.4, 0.0, 0.2, Phase.HOLD_SHALLOW_2),
    Phase.HOLD_SHALLOW_2: (0.4, 30.0, 0.33, Phase.SURFACE),
    Phase.SURFACE: (0.0, 0.0, 0.2, Phase.COMPLETE),
}


class PIDController:
    """PID controller with anti-windup and boundary protection."""

    # Boundary protection: virtual walls near surface and floor
    SURFACE_SAFE = 0.15  # m — start pushing down when shallower than this
    FLOOR_SAFE = 0.3  # m — start pushing up when closer than this to floor
    BOUNDARY_GAIN = 80.0  # strength of boundary repulsion

    def __init__(
        self,
        kp: float = 40.0,
        ki: float = 5.0,
        kd: float = 20.0,
        pool_depth: float = 4.0,
    ) -> None:
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.pool_depth = pool_depth
        self._integral = 0.0
        self._prev_error = 0.0
        self._first = True

    def compute(self, error: float, dt: float, depth: float = 0.0) -> float:
        """Compute PID output from error. Returns buoyancy command [-100, 100]."""
        self._integral += error * dt
        self._integral = np.clip(self._integral, -50.0, 50.0)  # anti-windup

        if self._first:
            derivative = 0.0
            self._first = False
        else:
            derivative = (error - self._prev_error) / dt if dt > 0 else 0.0
        self._prev_error = error

        # Positive error = need to go deeper -> negative command (reduce buoyancy)
        output = -(self.kp * error + self.ki * self._integral + self.kd * derivative)

        # Boundary protection: push away from surface and floor
        if depth < self.SURFACE_SAFE:
            # Too close to surface — force sink (negative command)
            repulsion = -self.BOUNDARY_GAIN * (1.0 - depth / self.SURFACE_SAFE)
            output = min(output, repulsion)
        elif depth > self.pool_depth - self.FLOOR_SAFE:
            # Too close to floor — force rise (positive command)
            closeness = 1.0 - (self.pool_depth - depth) / self.FLOOR_SAFE
            repulsion = self.BOUNDARY_GAIN * closeness
            output = max(output, repulsion)

        return float(np.clip(output, -100.0, 100.0))

    def reset(self) -> None:
        self._integral = 0.0
        self._prev_error = 0.0
        self._first = True


class MissionSequencer:
    """Drives the float through mission phases."""

    # Phases that belong to each profile (for penalty tracking)
    PROFILE_1_PHASES = {Phase.DESCEND_1, Phase.HOLD_DEEP_1, Phase.ASCEND_1, Phase.HOLD_SHALLOW_1}
    PROFILE_2_PHASES = {Phase.DESCEND_2, Phase.HOLD_DEEP_2, Phase.ASCEND_2, Phase.HOLD_SHALLOW_2}

    SURFACE_THRESHOLD = 0.02  # m — closer than this = surface breach
    FLOOR_MARGIN = 0.02  # m — closer than this to pool floor = floor contact

    def __init__(self, company: str = "TEST01", pool_depth: float = 4.0) -> None:
        self.company = company
        self.pool_depth = pool_depth
        self.phase = Phase.DEPLOY
        self.hold_timer = 0.0
        self.mission_time = 0.0
        self.packet_timer = 0.0
        self.packets: list[str] = []

        # Violation tracking
        self.surface_hit_p1 = False  # profile 1 surface breach
        self.surface_hit_p2 = False  # profile 2 surface breach
        self.floor_hit = False
        self.violations: list[str] = []  # log messages
        self._max_depth_p1 = 0.0  # deepest point reached in profile 1
        self._max_depth_p2 = 0.0  # deepest point reached in profile 2

        # Phase completion tracking
        self.profile1_done = False
        self.profile2_done = False
        self.hold_deep1_done = False
        self.hold_shallow1_done = False
        self.hold_deep2_done = False
        self.hold_shallow2_done = False

    @property
    def target_depth(self) -> float:
        if self.phase == Phase.COMPLETE:
            return 0.0
        return PHASE_CONFIG[self.phase][0]

    @property
    def hold_duration(self) -> float:
        if self.phase == Phase.COMPLETE:
            return 0.0
        return PHASE_CONFIG[self.phase][1]

    @property
    def hold_progress(self) -> float:
        """Returns 0.0-1.0 progress through current hold."""
        dur = self.hold_duration
        if dur <= 0:
            return 0.0
        return min(self.hold_timer / dur, 1.0)

    def update(self, depth: float, pressure: float, dt: float) -> str | None:
        """Advance mission state. Returns data packet string if one was emitted."""
        if self.phase == Phase.COMPLETE:
            return None

        self.mission_time += dt

        # --- Violation checks ---
        self._check_violations(depth)

        config = PHASE_CONFIG[self.phase]
        target, hold_dur, tolerance, next_phase = config

        if hold_dur > 0:
            # Hold phase: must stay within tolerance
            if abs(depth - target) <= tolerance:
                self.hold_timer += dt
                if self.hold_timer >= hold_dur:
                    self._transition(next_phase)
            else:
                self.hold_timer = 0.0  # reset on drift
        else:
            # Transit phase: transition on arrival
            if abs(depth - target) <= tolerance:
                self._transition(next_phase)

        # Emit data packet every 5 seconds
        self.packet_timer += dt
        if self.packet_timer >= 5.0:
            self.packet_timer -= 5.0
            return self._emit_packet(depth, pressure)
        return None

    def _check_violations(self, depth: float) -> None:
        # Track max depth per profile (to distinguish "never left surface" from "came back up")
        if self.phase in self.PROFILE_1_PHASES:
            self._max_depth_p1 = max(self._max_depth_p1, depth)
        elif self.phase in self.PROFILE_2_PHASES:
            self._max_depth_p2 = max(self._max_depth_p2, depth)

        # Surface breach: only counts if float has descended past 0.5m first
        if depth <= self.SURFACE_THRESHOLD:
            if (self.phase in self.PROFILE_1_PHASES
                    and self._max_depth_p1 > 0.5
                    and not self.surface_hit_p1):
                self.surface_hit_p1 = True
                self.violations.append(f"[{self.mission_time:.1f}s] SURFACE BREACH - Profile 1 (-5pts)")
            elif (self.phase in self.PROFILE_2_PHASES
                    and self._max_depth_p2 > 0.5
                    and not self.surface_hit_p2):
                self.surface_hit_p2 = True
                self.violations.append(f"[{self.mission_time:.1f}s] SURFACE BREACH - Profile 2 (-5pts)")

        # Floor contact
        if depth >= self.pool_depth - self.FLOOR_MARGIN and not self.floor_hit:
            if self.phase not in (Phase.DEPLOY, Phase.COMPLETE):
                self.floor_hit = True
                self.violations.append(f"[{self.mission_time:.1f}s] FLOOR CONTACT")

    def _transition(self, next_phase: Phase) -> None:
        # Track completions before transitioning
        if self.phase == Phase.HOLD_DEEP_1:
            self.hold_deep1_done = True
        elif self.phase == Phase.HOLD_SHALLOW_1:
            self.hold_shallow1_done = True
            self.profile1_done = True
        elif self.phase == Phase.HOLD_DEEP_2:
            self.hold_deep2_done = True
        elif self.phase == Phase.HOLD_SHALLOW_2:
            self.hold_shallow2_done = True
            self.profile2_done = True

        self.phase = next_phase
        self.hold_timer = 0.0

    @property
    def score(self) -> int:
        """Calculate mission score based on MATE 2026 rules."""
        pts = 5  # Item 1: Float design (assumed)
        pts += 5  # Item 2: Communication (packets exist)

        # Profile 1
        if self.profile1_done:
            pts += 10  # Item 3: profile complete (buoyancy engine)
        if self.hold_deep1_done:
            pts += 5  # Item 4: 2.5m hold
        if self.hold_shallow1_done:
            pts += 5  # Item 5: 0.4m hold
        if self.surface_hit_p1:
            pts -= 5  # Item 6: surface penalty

        # Profile 2
        if self.profile2_done:
            pts += 10  # Item 7: profile complete
        if self.hold_deep2_done:
            pts += 5  # Item 8: 2.5m hold
        if self.hold_shallow2_done:
            pts += 5  # Item 9: 0.4m hold
        if self.surface_hit_p2:
            pts -= 5  # Item 10: surface penalty

        # Data transmission
        if len(self.packets) > 1:
            pts += 10  # Item 11: all data packets
        elif len(self.packets) >= 1:
            pts += 5  # Item 11a: at least 1 packet

        # Graph (always available in simulator)
        pts += 10  # Item 12

        return pts

    def _emit_packet(self, depth: float, pressure: float) -> str:
        minutes = int(self.mission_time) // 60
        seconds = int(self.mission_time) % 60
        time_str = f"{minutes}:{seconds:02d}"
        packet = f"{self.company} {time_str} {pressure:.1f}kPa {depth:.2f}m"
        self.packets.append(packet)
        return packet
