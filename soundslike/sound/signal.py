"""Signal mixing and output."""

import numpy as np
from scipy.io import wavfile
from typing import Union, List

from .tone import SineWave
from .envelope import ADSR


class Signal:
    """Audio signal container with playback and file output."""

    def __init__(self, samples: np.ndarray, sample_rate: int = 44100):
        """
        Initialize signal with audio samples.

        Args:
            samples: numpy array of audio samples
            sample_rate: Sample rate in Hz
        """
        self.samples = samples
        self.sample_rate = sample_rate

    def __repr__(self) -> str:
        duration = len(self.samples) / self.sample_rate
        return f"Signal(duration={duration:.2f}s, sample_rate={self.sample_rate})"

    def __mul__(self, other: Union['Signal', ADSR, np.ndarray]) -> 'Signal':
        """Multiply signal by another signal, envelope, or array."""
        if isinstance(other, Signal):
            # Match lengths
            min_len = min(len(self.samples), len(other.samples))
            new_samples = self.samples[:min_len] * other.samples[:min_len]
        elif isinstance(other, ADSR):
            duration = len(self.samples) / self.sample_rate
            envelope = other.generate(duration)
            min_len = min(len(self.samples), len(envelope))
            new_samples = self.samples[:min_len] * envelope[:min_len]
        elif isinstance(other, np.ndarray):
            min_len = min(len(self.samples), len(other))
            new_samples = self.samples[:min_len] * other[:min_len]
        else:
            new_samples = self.samples * other

        return Signal(new_samples, self.sample_rate)

    def write(self, filename: str):
        """
        Write signal to WAV file.

        Args:
            filename: Output file path
        """
        # Normalize to 16-bit range
        normalized = self.samples / (np.max(np.abs(self.samples)) + 1e-10)
        audio_data = (normalized * 32767).astype(np.int16)
        wavfile.write(filename, self.sample_rate, audio_data)

    def play(self, duration: float = None):
        """
        Play the signal (no-op in headless environments).

        Args:
            duration: Duration to play (ignored, plays full signal)
        """
        # In a headless environment, we just skip playback
        # Could integrate with simpleaudio or pyaudio if available
        pass

    def to_audio(self):
        """
        Return an IPython Audio widget for notebook playback.

        Returns:
            IPython.display.Audio object that can be displayed in notebooks
        """
        try:
            from IPython.display import Audio
        except ImportError:
            raise ImportError("IPython is required for notebook audio playback. "
                            "Install with: pip install ipython")

        # Normalize samples to [-1, 1] range for Audio widget
        normalized = self.samples / (np.max(np.abs(self.samples)) + 1e-10)
        return Audio(normalized, rate=self.sample_rate)

    def to_numpy(self) -> np.ndarray:
        """
        Return normalized audio samples as numpy array.

        Returns:
            numpy array of audio samples normalized to [-1, 1]
        """
        return self.samples / (np.max(np.abs(self.samples)) + 1e-10)


class MixSignal(Signal):
    """Mix multiple signals together."""

    def __init__(self, *sources: Union[SineWave, Signal], sample_rate: int = 44100):
        """
        Mix multiple sound sources together.

        Args:
            *sources: SineWave or Signal objects to mix
            sample_rate: Sample rate in Hz
        """
        self.sources = sources
        self.sample_rate = sample_rate
        self._samples = None

    @property
    def samples(self) -> np.ndarray:
        """Lazily generate mixed samples."""
        if self._samples is None:
            raise ValueError("Must call generate() or apply envelope first")
        return self._samples

    @samples.setter
    def samples(self, value):
        self._samples = value

    def generate(self, duration: float) -> np.ndarray:
        """
        Generate mixed audio for given duration.

        Args:
            duration: Duration in seconds

        Returns:
            numpy array of mixed audio samples
        """
        if not self.sources:
            return np.zeros(int(self.sample_rate * duration))

        mixed = np.zeros(int(self.sample_rate * duration))

        for source in self.sources:
            if isinstance(source, SineWave):
                samples = source.generate(duration)
            elif isinstance(source, Signal):
                samples = source.samples
            else:
                continue

            # Add to mix, handling length differences
            min_len = min(len(mixed), len(samples))
            mixed[:min_len] += samples[:min_len]

        # Normalize to prevent clipping
        if len(self.sources) > 0:
            mixed = mixed / len(self.sources)

        self._samples = mixed
        return mixed

    def __mul__(self, other: Union[Signal, ADSR, np.ndarray]) -> Signal:
        """Multiply mixed signal by envelope or other signal."""
        if isinstance(other, ADSR):
            duration = other.total_duration
            self.generate(duration)

        return super().__mul__(other)
