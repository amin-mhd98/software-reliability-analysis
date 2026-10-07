"""
Software reliability models.

Implemented models:
1. Jelinski-Moranda
2. Schuman
3. Nelson-Corcoran
"""

import math
from typing import List, Tuple

import matplotlib.pyplot as plt
import numpy as np


class JelinskiMorandaModel:
    """
    Jelinski-Moranda software reliability model.

    Failure intensity is proportional to the number
    of remaining software faults.
    """

    def __init__(self, N0: int, phi: float):
        """
        Args:
            N0: Initial number of faults.
            phi: Fault detection intensity coefficient.
        """
        self.N0 = N0
        self.phi = phi

    def failure_intensity(self, i: int) -> float:
        """
        Calculate failure intensity after correcting i faults.
        """
        remaining = self.N0 - i

        if remaining < 0:
            raise ValueError(
                "The number of corrected faults cannot exceed "
                "the initial number of faults."
            )

        return self.phi * remaining

    def reliability(self, t: float, i: int = 0) -> float:
        """
        Calculate reliability for operating time t.
        """
        lam = self.failure_intensity(i)
        return math.exp(-lam * t)

    def mttf(self, i: int = 0) -> float:
        """
        Calculate Mean Time To Failure (MTTF).
        """
        lam = self.failure_intensity(i)

        if lam > 0:
            return 1.0 / lam

        return float("inf")


class SchumanModel:
    """
    Schuman software reliability model.

    Failure intensity is proportional to the residual
    fault density per machine instruction.
    """

    def __init__(self, I: int, E0: int, Ks: float):
        """
        Args:
            I: Total number of machine instructions.
            E0: Initial number of faults.
            Ks: Proportionality coefficient.
        """
        self.I = I
        self.E0 = E0
        self.Ks = Ks

    def residual_error_density(self, Ec: int) -> float:
        """
        Calculate residual fault density after correcting Ec faults.
        """
        return (self.E0 - Ec) / self.I

    def failure_intensity(self, Ec: int) -> float:
        """
        Calculate failure intensity.
        """
        return self.Ks * self.residual_error_density(Ec)

    def reliability(self, t: float, Ec: int = 0) -> float:
        """
        Calculate reliability for operating time t.
        """
        lam = self.failure_intensity(Ec)
        return math.exp(-lam * t)

    def mttf(self, Ec: int = 0) -> float:
        """
        Calculate Mean Time To Failure (MTTF).
        """
        lam = self.failure_intensity(Ec)

        if lam > 0:
            return 1.0 / lam

        return float("inf")

    @classmethod
    def estimate_parameters(
        cls,
        I: int,
        t1: float,
        t2: float,
        n1: int,
        n2: int,
        Ec1: int,
        Ec2: int,
    ) -> Tuple[float, float]:
        """
        Estimate E0 and Ks using the method of moments.
        """

        gamma = (t1 * n2) / (t2 * n1) if n1 > 0 else 1.0

        if gamma != 1:
            E0 = I * (gamma * Ec1 - Ec2) / (gamma - 1)
        else:
            E0 = 0

        denominator = t1 * (E0 / I - Ec1 / I)

        if denominator != 0:
            Ks = n1 / denominator
        else:
            Ks = 0

        return E0, Ks


class NelsonCorcoranModel:
    """
    Combined Nelson-Corcoran software reliability model.

    This is a static reliability model based on
    software test run results.
    """

    def __init__(
        self,
        P: List[float],
        n: List[int],
        N: List[int],
        N0: int = None,
        Ni: List[int] = None,
        ai: List[float] = None,
    ):
        """
        Args:
            P: Probabilities of selecting input subdomains.
            n: Number of failures in each subdomain.
            N: Number of runs in each subdomain.
            N0: Number of successful overall runs.
            Ni: Number of failures/errors of each type.
            ai: Probabilities associated with each fault type.
        """

        if abs(sum(P) - 1.0) > 1e-6:
            raise ValueError(
                "The sum of probabilities P must be equal to 1."
            )

        if len(P) != len(n) or len(P) != len(N):
            raise ValueError(
                "Lists P, n, and N must have the same length."
            )

        self.P = P
        self.n = n
        self.N = N
        self.N0 = N0 if N0 is not None else sum(N) - sum(n)
        self.Ni = Ni
        self.ai = ai if ai else ([0.5] * len(Ni) if Ni else [])

    def reliability_nelson(self) -> float:
        """
        Calculate reliability using the Nelson approach.
        """

        failure_probability = sum(
            (ni / Ni) * Pi
            for ni, Ni, Pi in zip(
                self.n,
                self.N,
                self.P,
            )
        )

        return 1.0 - failure_probability

    def reliability_corcoran(self) -> float:
        """
        Calculate reliability using the Corcoran extension.
        """

        if not self.Ni:
            return self.reliability_simple()

        sum_term = sum(
            self.ai[i] * (self.Ni[i] - 1)
            for i in range(len(self.Ni))
            if self.Ni[i] > 0
        )

        total_runs = self.N0 + sum(self.Ni)

        return (self.N0 + sum_term) / total_runs

    def reliability_simple(self) -> float:
        """
        Calculate reliability using the simplified form:

        R = 1 - failures / total_runs

        For the practical-work dataset:
        successful runs = 970
        failures = 30
        total runs = 1000
        therefore R = 0.97
        """

        if self.Ni:
            total_failures = sum(self.Ni)
            total_runs = self.N0 + total_failures

            return 1.0 - total_failures / total_runs

        total_failures = sum(self.n)
        total_runs = sum(self.N)

        return 1.0 - total_failures / total_runs

    def reliability(self) -> float:
        """
        Return the main Nelson reliability estimate.
        """
        return self.reliability_nelson()


def demo_calculations():
    """
    Demonstrate calculations for all three reliability models.
    """

    print("=" * 70)
    print("SOFTWARE RELIABILITY MODEL CALCULATIONS")
    print("=" * 70)

    # -------------------------------------------------
    # 1. Jelinski-Moranda model
    # -------------------------------------------------

    print("\n1. JELINSKI-MORANDA MODEL")

    jm = JelinskiMorandaModel(
        N0=50,
        phi=0.0001,
    )

    print(
        f"Failure intensity: "
        f"{jm.failure_intensity(30):.6f} failures/hour"
    )

    print(
        f"R(t=100) = "
        f"{jm.reliability(100, i=30):.4f}"
    )

    print(
        f"MTTF = "
        f"{jm.mttf(i=30):.2f} hours"
    )

    # -------------------------------------------------
    # 2. Schuman model
    # -------------------------------------------------

    print("\n2. SCHUMAN MODEL")

    sch = SchumanModel(
        I=10000,
        E0=50,
        Ks=0.0001,
    )

    print(
        f"Residual fault density: "
        f"{sch.residual_error_density(30):.6f}"
    )

    print(
        f"Failure intensity: "
        f"{sch.failure_intensity(30):.8f}"
    )

    print(
        f"R(t=100) = "
        f"{sch.reliability(100, Ec=30):.8f}"
    )

    print(
        f"MTTF = "
        f"{sch.mttf(Ec=30):.0f} hours"
    )

    # -------------------------------------------------
    # 3. Nelson-Corcoran model
    # -------------------------------------------------

    print("\n3. NELSON-CORCORAN MODEL")

    nc = NelsonCorcoranModel(
        P=[0.6, 0.4],
        n=[5, 2],
        N=[100, 50],
        N0=970,
        Ni=[20, 10],
        ai=[0.7, 0.3],
    )

    print(
        f"R (Nelson) = "
        f"{nc.reliability_nelson():.4f}"
    )

    print(
        f"R (Corcoran) = "
        f"{nc.reliability_corcoran():.4f}"
    )

    print(
        f"R (simplified) = "
        f"{nc.reliability_simple():.4f}"
    )


def plot_reliability_curves():
    """
    Plot reliability as a function of operating time.
    """

    t = np.linspace(1, 500, 100)

    # Jelinski-Moranda model
    jm = JelinskiMorandaModel(
        N0=50,
        phi=0.0001,
    )

    # Schuman model
    sch = SchumanModel(
        I=10000,
        E0=50,
        Ks=0.0001,
    )

    R_jm = [
        jm.reliability(ti, i=30)
        for ti in t
    ]

    R_sch = [
        sch.reliability(ti, Ec=30)
        for ti in t
    ]

    plt.figure(figsize=(10, 6))

    plt.plot(
        t,
        R_jm,
        label="Jelinski-Moranda",
        linewidth=2,
    )

    plt.plot(
        t,
        R_sch,
        linestyle="--",
        label="Schuman",
        linewidth=2,
    )

    plt.axhline(
        y=0.95,
        linestyle=":",
        label="Target reliability R=0.95",
    )

    plt.xlabel("Operating time, hours")
    plt.ylabel("Reliability R(t)")
    plt.title("Software Reliability Model Comparison")

    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()

    plt.savefig(
        "reliability_curves.png",
        dpi=150,
    )

    plt.show()

    print("Plot saved as: reliability_curves.png")


if __name__ == "__main__":
    demo_calculations()
    plot_reliability_curves()
