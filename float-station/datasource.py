"""Data source abstraction and controlled source implementation."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field

from controller import MissionSequencer, PIDController, Phase
from hardware import FloatHardware, SimulatedFloat


@dataclass
class FloatState:
    """Snapshot of float state at a point in time."""

    time: float = 0.0
    depth: float = 0.0
    pressure: float = 101.325
    buoyancy_cmd: float = 0.0
    pid_output: float = 0.0
    phase: Phase = Phase.DEPLOY
    packet_count: int = 0
    hold_progress: float = 0.0
    score: int = 0
    violations: list[str] = field(default_factory=list)


class DataSource(ABC):
    """Abstract interface for float data."""

    @abstractmethod
    def tick(self, dt: float) -> FloatState:
        """Advance simulation and return current state."""

    @abstractmethod
    def get_history(self) -> tuple[list[float], list[float], list[float]]:
        """Return (times, depths, pressures) history lists."""


class ControlledSource(DataSource):
    """Connects SimulatedFloat + Controller into a data source."""

    def __init__(
        self,
        hardware: FloatHardware,
        pid: PIDController,
        sequencer: MissionSequencer,
    ) -> None:
        self.hw = hardware
        self.pid = pid
        self.seq = sequencer
        self.times: list[float] = []
        self.depths: list[float] = []
        self.pressures: list[float] = []
        self._state = FloatState()

    def tick(self, dt: float) -> FloatState:
        # 1. Read sensors
        depth, pressure = self.hw.read_sensors()

        # 2. PID compute
        error = self.seq.target_depth - depth
        cmd = self.pid.compute(error, dt, depth=depth)

        # 3. Send command
        self.hw.send_command(cmd)

        # 4. Step physics
        if isinstance(self.hw, SimulatedFloat):
            self.hw.step(dt)

        # 5. Update mission
        self.seq.update(depth, pressure, dt)

        # 6. Record history
        t = self.seq.mission_time
        self.times.append(t)
        self.depths.append(depth)
        self.pressures.append(pressure)

        # 7. Build state
        self._state = FloatState(
            time=t,
            depth=depth,
            pressure=pressure,
            buoyancy_cmd=cmd,
            pid_output=cmd,
            phase=self.seq.phase,
            packet_count=len(self.seq.packets),
            hold_progress=self.seq.hold_progress,
            score=self.seq.score,
            violations=list(self.seq.violations),
        )
        return self._state

    def get_history(self) -> tuple[list[float], list[float], list[float]]:
        return self.times, self.depths, self.pressures
