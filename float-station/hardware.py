"""FloatHardware ABC and SimulatedFloat physics implementation."""

from abc import ABC, abstractmethod

import numpy as np


class FloatHardware(ABC):
    """Abstract interface for float hardware."""

    @abstractmethod
    def read_sensors(self) -> tuple[float, float]:
        """Return (depth_m, pressure_kpa)."""

    @abstractmethod
    def send_command(self, buoyancy_pct: float) -> None:
        """Set buoyancy engine power. -100 = full sink, +100 = full rise."""


class SimulatedFloat(FloatHardware):
    """Physics-based float simulation with buoyancy, drag, and inertia."""

    G = 9.81  # m/s^2
    P_ATM = 101.325  # kPa
    DT = 0.01  # physics timestep (s)

    def __init__(
        self,
        mass: float = 3.0,
        radius: float = 0.08,
        cd: float = 1.2,
        syringe_ml: float = 80.0,
        pool_depth: float = 4.0,
        rho_water: float = 1025.0,
    ) -> None:
        # Configurable parameters
        self.mass = mass  # kg
        self.radius = radius  # m
        self.cd = cd  # drag coefficient
        self.syringe_vol = syringe_ml * 1e-6  # ml -> m^3
        self.pool_depth = pool_depth  # m
        self.rho_water = rho_water  # kg/m^3

        # Derived
        self.cross_area = np.pi * radius**2  # m^2
        self.v_base = mass / rho_water  # neutral buoyancy volume (m^3)

        # State
        self.depth = 0.0  # m from surface
        self.velocity = 0.0  # m/s (positive = downward)
        self._buoyancy_pct = 0.0
        self._rng = np.random.default_rng(42)

    def read_sensors(self) -> tuple[float, float]:
        noise = self._rng.normal(0, 0.005)
        depth = max(0.0, self.depth + noise)
        pressure = self.P_ATM + self.rho_water * self.G * depth / 1000.0
        return depth, pressure

    def send_command(self, buoyancy_pct: float) -> None:
        self._buoyancy_pct = np.clip(buoyancy_pct, -100.0, 100.0)

    def step(self, dt: float | None = None) -> None:
        """Advance physics by dt seconds."""
        dt = dt or self.DT

        # Displaced volume: positive buoyancy_pct -> more volume -> more buoyancy -> rise
        v_displaced = self.v_base + (self._buoyancy_pct / 100.0) * self.syringe_vol

        # Forces (positive = downward)
        f_gravity = self.mass * self.G
        f_buoyancy = -self.rho_water * self.G * v_displaced
        f_drag = (
            -0.5
            * self.rho_water
            * self.cd
            * self.cross_area
            * self.velocity
            * abs(self.velocity)
        )

        acceleration = (f_gravity + f_buoyancy + f_drag) / self.mass

        # Semi-implicit Euler
        self.velocity += acceleration * dt
        self.depth += self.velocity * dt

        # Boundary conditions
        if self.depth <= 0.0:
            self.depth = 0.0
            self.velocity = min(self.velocity, 0.0)  # can only go down
        elif self.depth >= self.pool_depth:
            self.depth = self.pool_depth
            self.velocity = max(self.velocity, 0.0)  # can only go up
