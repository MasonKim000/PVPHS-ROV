"""Float Mission Station -- CLI entry point."""

import argparse

from controller import MissionSequencer, PIDController
from datasource import ControlledSource
from hardware import SimulatedFloat
from ui import Dashboard


def main() -> None:
    parser = argparse.ArgumentParser(description="Float Mission Station")
    parser.add_argument("--company", default="TEST01", help="Company number")
    parser.add_argument("--speed", type=float, default=1.0, help="Simulation speed multiplier")

    pid_group = parser.add_argument_group("PID gains")
    pid_group.add_argument("--kp", type=float, default=40.0, help="Proportional gain")
    pid_group.add_argument("--ki", type=float, default=5.0, help="Integral gain")
    pid_group.add_argument("--kd", type=float, default=20.0, help="Derivative gain")

    hw_group = parser.add_argument_group("Float physics")
    hw_group.add_argument("--mass", type=float, default=3.0, help="Float mass in kg")
    hw_group.add_argument("--radius", type=float, default=0.08, help="Float radius in m")
    hw_group.add_argument("--cd", type=float, default=1.2, help="Drag coefficient")
    hw_group.add_argument("--syringe", type=float, default=80.0, help="Syringe capacity in mL")
    hw_group.add_argument("--pool-depth", type=float, default=4.0, help="Pool depth in m")
    hw_group.add_argument("--rho", type=float, default=1025.0, help="Water density in kg/m^3")

    args = parser.parse_args()

    hw = SimulatedFloat(
        mass=args.mass,
        radius=args.radius,
        cd=args.cd,
        syringe_ml=args.syringe,
        pool_depth=args.pool_depth,
        rho_water=args.rho,
    )
    pid = PIDController(kp=args.kp, ki=args.ki, kd=args.kd, pool_depth=args.pool_depth)
    seq = MissionSequencer(company=args.company, pool_depth=args.pool_depth)
    source = ControlledSource(hardware=hw, pid=pid, sequencer=seq)

    dashboard = Dashboard(source=source, speed=args.speed)
    dashboard.run()


if __name__ == "__main__":
    main()
