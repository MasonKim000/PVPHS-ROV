"""Real-time matplotlib dashboard for float mission visualization."""

import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.patches import Circle, Rectangle
from matplotlib.widgets import Slider, Button

from datasource import DataSource, ControlledSource


class Dashboard:
    """2x2 matplotlib dashboard with FuncAnimation and interactive sliders."""

    def __init__(self, source: DataSource, speed: float = 1.0) -> None:
        self.source = source
        self.speed = speed
        self.physics_dt = 0.01
        self._paused = False

        self.fig, self.axes = plt.subplots(2, 2, figsize=(14, 9))
        self.fig.canvas.manager.set_window_title("Float Mission Station")

        self._setup_depth_plot()
        self._setup_pool_view()
        self._setup_pressure_plot()
        self._setup_status_panel()
        self._setup_sliders()

        self.fig.subplots_adjust(bottom=0.22, hspace=0.35, wspace=0.3)

    def _setup_depth_plot(self) -> None:
        ax = self.axes[0, 0]
        ax.set_title("Depth vs Time")
        ax.set_xlabel("Time (s)")
        ax.set_ylabel("Depth (m)")
        ax.invert_yaxis()
        ax.set_xlim(0, 30)
        ax.set_ylim(4.0, -0.5)
        ax.grid(True, alpha=0.3)

        # Target depth bands
        ax.axhspan(2.5 - 0.33, 2.5 + 0.33, alpha=0.15, color="blue", label="2.5m band")
        ax.axhspan(0.4 - 0.33, 0.4 + 0.33, alpha=0.15, color="green", label="0.4m band")
        ax.legend(loc="lower right", fontsize=8)

        (self._depth_line,) = ax.plot([], [], "r-", linewidth=1.5)
        (self._target_line,) = ax.plot([], [], "k--", linewidth=0.8, alpha=0.5)

    def _setup_pool_view(self) -> None:
        ax = self.axes[0, 1]
        ax.set_title("Pool Cross-Section")
        ax.set_xlim(-1, 1)
        ax.set_ylim(4.5, -0.5)
        ax.set_aspect("equal")
        ax.set_ylabel("Depth (m)")
        ax.set_xticks([])

        # Pool walls
        wall_color = "#8B7355"
        ax.add_patch(Rectangle((-0.6, -0.1), 1.2, 0.1, color=wall_color))  # rim
        ax.add_patch(Rectangle((-0.6, -0.1), 0.05, 4.2, color=wall_color))  # left wall
        ax.add_patch(Rectangle((0.55, -0.1), 0.05, 4.2, color=wall_color))  # right wall
        ax.add_patch(Rectangle((-0.6, 4.0), 1.2, 0.1, color=wall_color))  # floor

        # Water
        ax.add_patch(Rectangle((-0.55, 0.0), 1.1, 4.0, alpha=0.2, color="cyan"))

        # Float marker
        self._float_marker = Circle((0, 0), 0.12, color="orange", ec="black", lw=1.5, zorder=5)
        ax.add_patch(self._float_marker)

        self._depth_label = ax.text(
            0.35, 0, "", fontsize=9, fontweight="bold", va="center"
        )

    def _setup_pressure_plot(self) -> None:
        ax = self.axes[1, 0]
        ax.set_title("Pressure vs Time")
        ax.set_xlabel("Time (s)")
        ax.set_ylabel("Pressure (kPa)")
        ax.set_xlim(0, 30)
        ax.grid(True, alpha=0.3)

        (self._pressure_line,) = ax.plot([], [], "b-", linewidth=1.5)

    def _setup_status_panel(self) -> None:
        ax = self.axes[1, 1]
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.axis("off")
        ax.set_title("Mission Status")

        self._status_text = ax.text(
            0.05,
            0.92,
            "",
            transform=ax.transAxes,
            fontsize=11,
            fontfamily="monospace",
            verticalalignment="top",
            bbox=dict(boxstyle="round,pad=0.5", facecolor="lightyellow", alpha=0.8),
        )

    def _setup_sliders(self) -> None:
        slider_color = "lightgoldenrodyellow"
        h = 0.02  # slider height

        # Row 1: Speed + Pause/Reset buttons
        ax_speed = self.fig.add_axes([0.12, 0.11, 0.35, h])
        self._sl_speed = Slider(ax_speed, "Speed", 0.5, 20.0, valinit=self.speed, valstep=0.5, color=slider_color)
        self._sl_speed.on_changed(self._on_speed)

        ax_pause = self.fig.add_axes([0.55, 0.105, 0.08, 0.03])
        self._btn_pause = Button(ax_pause, "Pause")
        self._btn_pause.on_clicked(self._on_pause)

        ax_reset = self.fig.add_axes([0.65, 0.105, 0.08, 0.03])
        self._btn_reset = Button(ax_reset, "Reset")
        self._btn_reset.on_clicked(self._on_reset)

        # Row 2: PID gains
        ax_kp = self.fig.add_axes([0.12, 0.065, 0.22, h])
        ax_ki = self.fig.add_axes([0.42, 0.065, 0.22, h])
        ax_kd = self.fig.add_axes([0.72, 0.065, 0.22, h])

        pid = self._get_pid()
        kp_init = pid.kp if pid else 40.0
        ki_init = pid.ki if pid else 5.0
        kd_init = pid.kd if pid else 20.0

        self._sl_kp = Slider(ax_kp, "Kp", 0, 100, valinit=kp_init, valstep=1, color=slider_color)
        self._sl_ki = Slider(ax_ki, "Ki", 0, 30, valinit=ki_init, valstep=0.5, color=slider_color)
        self._sl_kd = Slider(ax_kd, "Kd", 0, 60, valinit=kd_init, valstep=1, color=slider_color)

        self._sl_kp.on_changed(self._on_pid)
        self._sl_ki.on_changed(self._on_pid)
        self._sl_kd.on_changed(self._on_pid)

        # Row 3: Physics params (mass, syringe)
        ax_mass = self.fig.add_axes([0.12, 0.02, 0.22, h])
        ax_syringe = self.fig.add_axes([0.42, 0.02, 0.22, h])
        ax_cd = self.fig.add_axes([0.72, 0.02, 0.22, h])

        hw = self._get_hw()
        mass_init = hw.mass if hw else 3.0
        syr_init = hw.syringe_vol * 1e6 if hw else 80.0
        cd_init = hw.cd if hw else 1.2

        self._sl_mass = Slider(ax_mass, "Mass(kg)", 0.5, 10.0, valinit=mass_init, valstep=0.1, color=slider_color)
        self._sl_syringe = Slider(ax_syringe, "Syringe(mL)", 10, 200, valinit=syr_init, valstep=5, color=slider_color)
        self._sl_cd = Slider(ax_cd, "Cd", 0.2, 3.0, valinit=cd_init, valstep=0.1, color=slider_color)

        self._sl_mass.on_changed(self._on_physics)
        self._sl_syringe.on_changed(self._on_physics)
        self._sl_cd.on_changed(self._on_physics)

    def _get_pid(self):
        if isinstance(self.source, ControlledSource):
            return self.source.pid
        return None

    def _get_hw(self):
        from hardware import SimulatedFloat
        if isinstance(self.source, ControlledSource) and isinstance(self.source.hw, SimulatedFloat):
            return self.source.hw
        return None

    def _on_speed(self, val: float) -> None:
        self.speed = val

    def _on_pause(self, event) -> None:
        self._paused = not self._paused
        self._btn_pause.label.set_text("Resume" if self._paused else "Pause")

    def _on_reset(self, event) -> None:
        if not isinstance(self.source, ControlledSource):
            return
        from hardware import SimulatedFloat
        from controller import MissionSequencer, Phase

        # Reset hardware
        hw = self._get_hw()
        if hw:
            hw.depth = 0.0
            hw.velocity = 0.0
            hw._buoyancy_pct = 0.0

        # Reset sequencer
        self.source.seq.phase = Phase.DEPLOY
        self.source.seq.hold_timer = 0.0
        self.source.seq.mission_time = 0.0
        self.source.seq.packet_timer = 0.0
        self.source.seq.packets.clear()
        self.source.seq.violations.clear()
        self.source.seq.surface_hit_p1 = False
        self.source.seq.surface_hit_p2 = False
        self.source.seq.floor_hit = False
        self.source.seq._max_depth_p1 = 0.0
        self.source.seq._max_depth_p2 = 0.0
        self.source.seq.profile1_done = False
        self.source.seq.profile2_done = False
        self.source.seq.hold_deep1_done = False
        self.source.seq.hold_shallow1_done = False
        self.source.seq.hold_deep2_done = False
        self.source.seq.hold_shallow2_done = False

        # Reset PID
        self.source.pid.reset()

        # Reset history
        self.source.times.clear()
        self.source.depths.clear()
        self.source.pressures.clear()

        self._paused = False
        self._btn_pause.label.set_text("Pause")

    def _on_pid(self, val: float) -> None:
        pid = self._get_pid()
        if pid:
            pid.kp = self._sl_kp.val
            pid.ki = self._sl_ki.val
            pid.kd = self._sl_kd.val

    def _on_physics(self, val: float) -> None:
        hw = self._get_hw()
        if hw:
            hw.mass = self._sl_mass.val
            hw.syringe_vol = self._sl_syringe.val * 1e-6
            hw.cd = self._sl_cd.val
            hw.v_base = hw.mass / hw.rho_water

    def _update(self, frame: int) -> list:
        if self._paused:
            return []

        # Stop ticking once mission is complete
        from controller import Phase
        if (isinstance(self.source, ControlledSource)
                and self.source.seq.phase == Phase.COMPLETE):
            return []

        steps = max(1, int(0.1 * self.speed / self.physics_dt))

        for _ in range(steps):
            state = self.source.tick(self.physics_dt)

        times, depths, pressures = self.source.get_history()
        if not times:
            return []

        t = times[-1]

        # Depth plot
        self._depth_line.set_data(times, depths)
        self._target_line.set_data([0, t], [self._get_target(state)] * 2)
        ax_depth = self.axes[0, 0]
        if t > ax_depth.get_xlim()[1] * 0.8:
            ax_depth.set_xlim(0, t * 1.3)

        # Pool view
        self._float_marker.center = (0, state.depth)
        self._depth_label.set_position((0.35, state.depth))
        self._depth_label.set_text(f"{state.depth:.2f}m")

        # Pressure plot
        self._pressure_line.set_data(times, pressures)
        ax_pres = self.axes[1, 0]
        if t > ax_pres.get_xlim()[1] * 0.8:
            ax_pres.set_xlim(0, t * 1.3)
        if pressures:
            p_min = min(pressures) - 1
            p_max = max(pressures) + 1
            ax_pres.set_ylim(p_min, p_max)

        # Status panel
        hold_bar = self._hold_bar(state.hold_progress)
        phase_name = state.phase.name.replace("_", " ")

        # Result line
        if state.phase == Phase.COMPLETE:
            has_violations = bool(state.violations)
            result = "FAIL" if has_violations else "PASS"
            result_line = f"Result:   {result}  ({state.score}/70 pts)\n"
        else:
            result_line = f"Score:    {state.score}/70 pts\n"

        status = (
            f"Phase:    {phase_name}\n"
            f"Time:     {state.time:.1f}s\n"
            f"Depth:    {state.depth:.3f}m\n"
            f"Pressure: {state.pressure:.1f} kPa\n"
            f"Command:  {state.buoyancy_cmd:+.1f}%\n"
            f"PID Out:  {state.pid_output:+.1f}\n"
            f"Packets:  {state.packet_count}\n"
            f"Hold:     {hold_bar}\n"
            + result_line
        )

        # Show violations (last 3)
        if state.violations:
            status += "---VIOLATIONS---\n"
            for v in state.violations[-3:]:
                status += f" {v}\n"

        self._status_text.set_text(status)

        # Change status box color on violations
        if state.violations:
            self._status_text.get_bbox_patch().set_facecolor("lightsalmon")
        elif state.phase == Phase.COMPLETE:
            self._status_text.get_bbox_patch().set_facecolor("lightgreen")
        else:
            self._status_text.get_bbox_patch().set_facecolor("lightyellow")

        return []

    @staticmethod
    def _get_target(state) -> float:
        from controller import PHASE_CONFIG, Phase

        if state.phase == Phase.COMPLETE:
            return 0.0
        return PHASE_CONFIG[state.phase][0]

    @staticmethod
    def _hold_bar(progress: float) -> str:
        filled = int(progress * 20)
        return f"[{'#' * filled}{'.' * (20 - filled)}] {progress * 100:.0f}%"

    def run(self) -> None:
        self._anim = FuncAnimation(
            self.fig, self._update, interval=100, blit=False, cache_frame_data=False
        )
        plt.show()
