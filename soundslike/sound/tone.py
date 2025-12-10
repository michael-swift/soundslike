"""Tone generation using numpy."""

import numpy as np


class SineWave:
    """Generate a sine wave at a given frequency."""

    def __init__(self, frequency: float, sample_rate: int = 44100):
        """
        Initialize a sine wave generator.

        Args:
            frequency: Frequency in Hz
            sample_rate: Sample rate in Hz (default 44100)
        """
        self.frequency = frequency
        self.sample_rate = sample_rate

    def generate(self, duration: float) -> np.ndarray:
        """
        Generate samples for the given duration.

        Args:
            duration: Duration in seconds

        Returns:
            numpy array of audio samples
        """
        t = np.linspace(0, duration, int(self.sample_rate * duration), endpoint=False)
        return np.sin(2 * np.pi * self.frequency * t)
