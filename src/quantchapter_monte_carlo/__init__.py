"""Uniform Monte Carlo integration for reproducible teaching and inspection."""

from .core import IntegrationResult, integrate
from .experiments import ConvergencePoint, convergence_experiment

__version__ = "0.1.0"
__all__ = ["ConvergencePoint", "IntegrationResult", "convergence_experiment", "integrate"]
