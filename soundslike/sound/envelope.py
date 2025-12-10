"""ADSR envelope generator."""

import numpy as np


class ADSR:
    """Attack-Decay-Sustain-Release envelope generator."""

    def __init__(
        self,
        attack: float = 0.1,
        decay: float = 0.1,
        sustain: float = 0.6,
        sustain_level: float = 0.7,
        release: float = 0.2,
        sample_rate: int = 44100
    ):
        """
        Initialize ADSR envelope.

        Args:
            attack: Attack time in seconds
            decay: Decay time in seconds
            sustain: Sustain duration in seconds
            sustain_level: Sustain amplitude (0-1)
            release: Release time in seconds
            sample_rate: Sample rate in Hz
        """
        self.attack = attack
        self.decay = decay
        self.sustain = sustain
        self.sustain_level = sustain_level
        self.release = release
        self.sample_rate = sample_rate

    def generate(self, duration: float = None) -> np.ndarray:
        """
        Generate the envelope curve.

        Args:
            duration: Total duration (if None, uses sum of ADSR times)

        Returns:
            numpy array of envelope values
        """
        if duration is None:
            duration = self.attack + self.decay + self.sustain + self.release

        total_samples = int(self.sample_rate * duration)
        envelope = np.zeros(total_samples)

        attack_samples = int(self.attack * self.sample_rate)
        decay_samples = int(self.decay * self.sample_rate)
        sustain_samples = int(self.sustain * self.sample_rate)
        release_samples = int(self.release * self.sample_rate)

        idx = 0

        # Attack: 0 to 1
        if attack_samples > 0 and idx < total_samples:
            end_idx = min(idx + attack_samples, total_samples)
            envelope[idx:end_idx] = np.linspace(0, 1, end_idx - idx)
            idx = end_idx

        # Decay: 1 to sustain_level
        if decay_samples > 0 and idx < total_samples:
            end_idx = min(idx + decay_samples, total_samples)
            envelope[idx:end_idx] = np.linspace(1, self.sustain_level, end_idx - idx)
            idx = end_idx

        # Sustain: hold at sustain_level
        if sustain_samples > 0 and idx < total_samples:
            end_idx = min(idx + sustain_samples, total_samples)
            envelope[idx:end_idx] = self.sustain_level
            idx = end_idx

        # Release: sustain_level to 0
        if idx < total_samples:
            envelope[idx:] = np.linspace(self.sustain_level, 0, total_samples - idx)

        return envelope

    @property
    def total_duration(self) -> float:
        """Get total envelope duration."""
        return self.attack + self.decay + self.sustain + self.release
