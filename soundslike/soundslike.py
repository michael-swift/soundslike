import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import logging
from pathlib import Path
from datetime import datetime
from .sound.tone import SineWave
from .sound.signal import Signal, MixSignal
from .sound.envelope import ADSR

__all__ = ['ProbabilitySounds']

# Audible frequency range
MIN_FREQ = 20
MAX_FREQ = 20000

# Module logger - users can configure via logging.getLogger('soundslike')
logger = logging.getLogger(__name__)

class ProbabilitySounds:
    def __init__(self, sample_rate=44100, output_dir='output', seed=None):
        """Initialize ProbabilitySounds with sample rate and output directory.

        Args:
            sample_rate (int): Audio sample rate in Hz
            output_dir (str): Directory to save output files
            seed (int, optional): Random seed for reproducibility
        """
        self.sample_rate = sample_rate
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.rng = np.random.default_rng(seed)
        logger.info(f"Initialized ProbabilitySounds with sample_rate={sample_rate}")
        
    def _generate_filename(self, prefix):
        """Generate a unique filename with timestamp."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return self.output_dir / f"{prefix}_{timestamp}.wav"
    
    def play_distribution(self, dist_samples, duration=2.0, save=True, prefix='dist', title=None):
        """Play and visualize a distribution.
        
        Args:
            dist_samples (np.ndarray): Array of frequencies in Hz
            duration (float): Duration in seconds
            save (bool): Whether to save the sound file
            prefix (str): Prefix for the output filename
            title (str, optional): Title for the plot
        """
        logger.info(f"Playing distribution with {len(dist_samples)} samples")
        
        # Ensure frequencies are in audible range
        freq_array = np.clip(dist_samples, MIN_FREQ, MAX_FREQ)
        logger.info(f"Frequency range: {freq_array.min():.1f}Hz - {freq_array.max():.1f}Hz")
        
        # Create sine waves for each frequency
        signals = []
        for freq in freq_array:
            wave = SineWave(freq)
            signals.append(wave)
        
        # Mix signals and apply envelope
        mixed = MixSignal(*signals)
        env = ADSR(
            attack=0.1,
            decay=0.1,
            sustain=0.6,
            sustain_level=0.7,
            release=0.2
        )
        signal = mixed * env
        
        if save:
            filename = self._generate_filename(prefix)
            signal.write(str(filename))
            logger.info(f"Saved sound to {filename}")
        
        # Play and visualize
        signal.play(duration)
        self.plot_distribution(dist_samples, title=title)
        
    def plot_distribution(self, dist_array, title=None, save=True):
        """Plot and optionally save a distribution histogram."""
        plt.figure(figsize=(10, 6))
        sns.histplot(dist_array, bins=30, kde=True)
        
        if title:
            plt.title(title)
        plt.xlabel('Frequency (Hz)')
        plt.ylabel('Count')
        
        if save:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = self.output_dir / f"dist_plot_{timestamp}.png"
            plt.savefig(filename)
            logger.info(f"Saved plot to {filename}")
            
        plt.show()

    def play_normal(self, mean=440, std=10, num_samples=100):
        """Play and visualize a normal distribution of frequencies.
        
        Args:
            mean (float): Mean frequency in Hz
            std (float): Standard deviation in Hz
            num_samples (int): Number of samples to generate
        """
        logger.info(f"Generating normal distribution: mean={mean}Hz, std={std}Hz")
        samples = self.rng.normal(mean, std, num_samples)
        self.play_distribution(
            samples, 
            prefix='normal',
            title=f'Normal Distribution (μ={mean:.1f}Hz, σ={std:.1f}Hz)'
        )

    def play_beta(self, a=1, b=1, freq_range=(220, 880), num_samples=100):
        """Play and visualize a beta distribution scaled to a frequency range.
        
        Args:
            a (float): Alpha parameter of beta distribution
            b (float): Beta parameter of beta distribution
            freq_range (tuple): (min_freq, max_freq) in Hz
            num_samples (int): Number of samples to generate
        """
        logger.info(f"Generating beta distribution: a={a}, b={b}")
        samples = self.rng.beta(a, b, num_samples)
        # Scale beta (0-1) to frequency range
        min_freq, max_freq = freq_range
        samples = samples * (max_freq - min_freq) + min_freq
        
        self.play_distribution(
            samples,
            prefix='beta',
            title=f'Beta Distribution (α={a}, β={b}, range={min_freq}-{max_freq}Hz)'
        )

    def play_uniform(self, low=220, high=880, num_samples=100):
        """Play and visualize a uniform distribution of frequencies.

        Args:
            low (float): Minimum frequency in Hz
            high (float): Maximum frequency in Hz
            num_samples (int): Number of samples to generate
        """
        logger.info(f"Generating uniform distribution: range={low}-{high}Hz")
        samples = self.rng.uniform(low, high, num_samples)
        self.play_distribution(
            samples,
            prefix='uniform',
            title=f'Uniform Distribution ({low}-{high}Hz)'
        )

    # ==================== Notebook-friendly methods ====================

    def sonify(self, freq_samples, duration=1.0):
        """Convert frequency samples to an audio Signal.

        Args:
            freq_samples (np.ndarray): Array of frequencies in Hz
            duration (float): Duration in seconds (default 1.0)

        Returns:
            Signal: Audio signal that can be played or converted to IPython Audio
        """
        # Ensure frequencies are in audible range
        freq_array = np.clip(freq_samples, MIN_FREQ, MAX_FREQ)

        # Create sine waves for each frequency
        signals = [SineWave(freq, self.sample_rate) for freq in freq_array]

        # Mix signals and apply envelope
        mixed = MixSignal(*signals, sample_rate=self.sample_rate)
        env = ADSR(
            attack=0.05,
            decay=0.1,
            sustain=duration - 0.25,
            sustain_level=0.7,
            release=0.1,
            sample_rate=self.sample_rate
        )
        return mixed * env

    def sonify_normal(self, mean=440, std=50, num_samples=100, duration=1.0):
        """Create audio from a normal distribution.

        Args:
            mean (float): Mean frequency in Hz (default 440, A4 note)
            std (float): Standard deviation in Hz
            num_samples (int): Number of frequency samples
            duration (float): Duration in seconds

        Returns:
            Signal: Audio signal
        """
        samples = self.rng.normal(mean, std, num_samples)
        return self.sonify(samples, duration)

    def sonify_beta(self, a=2, b=2, freq_range=(220, 880), num_samples=100, duration=1.0):
        """Create audio from a beta distribution.

        Args:
            a (float): Alpha parameter
            b (float): Beta parameter
            freq_range (tuple): (min_freq, max_freq) in Hz
            num_samples (int): Number of frequency samples
            duration (float): Duration in seconds

        Returns:
            Signal: Audio signal
        """
        samples = self.rng.beta(a, b, num_samples)
        min_freq, max_freq = freq_range
        samples = samples * (max_freq - min_freq) + min_freq
        return self.sonify(samples, duration)

    def sonify_uniform(self, low=220, high=880, num_samples=100, duration=1.0):
        """Create audio from a uniform distribution.

        Args:
            low (float): Minimum frequency in Hz
            high (float): Maximum frequency in Hz
            num_samples (int): Number of frequency samples
            duration (float): Duration in seconds

        Returns:
            Signal: Audio signal
        """
        samples = self.rng.uniform(low, high, num_samples)
        return self.sonify(samples, duration)

    def sonify_exponential(self, scale=100, base_freq=200, num_samples=100, duration=1.0):
        """Create audio from an exponential distribution.

        Args:
            scale (float): Scale parameter (1/lambda)
            base_freq (float): Base frequency to add to samples
            num_samples (int): Number of frequency samples
            duration (float): Duration in seconds

        Returns:
            Signal: Audio signal
        """
        samples = self.rng.exponential(scale, num_samples) + base_freq
        return self.sonify(samples, duration)

    def sonify_poisson(self, lam=440, num_samples=100, duration=1.0):
        """Create audio from a Poisson distribution.

        Args:
            lam (float): Expected value (lambda), used as center frequency
            num_samples (int): Number of frequency samples
            duration (float): Duration in seconds

        Returns:
            Signal: Audio signal
        """
        samples = self.rng.poisson(lam, num_samples).astype(float)
        return self.sonify(samples, duration)

    def sonify_gamma(self, shape=2.0, scale=100, base_freq=200, num_samples=100, duration=1.0):
        """Create audio from a gamma distribution.

        Args:
            shape (float): Shape parameter (k)
            scale (float): Scale parameter (theta)
            base_freq (float): Base frequency to add to samples
            num_samples (int): Number of frequency samples
            duration (float): Duration in seconds

        Returns:
            Signal: Audio signal
        """
        samples = self.rng.gamma(shape, scale, num_samples) + base_freq
        return self.sonify(samples, duration)