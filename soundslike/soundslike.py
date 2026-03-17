import numpy as np
import logging
from pathlib import Path
from datetime import datetime
from .sound.tone import SineWave
from .sound.signal import Signal, MixSignal
from .sound.envelope import ADSR

# Lazy imports for plotting (speeds up import time)
plt = None
sns = None

def _ensure_plotting():
    """Lazy-load matplotlib and seaborn."""
    global plt, sns
    if plt is None:
        import matplotlib.pyplot as _plt
        import seaborn as _sns
        plt = _plt
        sns = _sns

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
        _ensure_plotting()
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

    def sonify(self, freq_samples, duration=1.0, gain=1.0):
        """Convert frequency samples to an audio Signal.

        Args:
            freq_samples (np.ndarray): Array of frequencies in Hz
            duration (float): Duration in seconds (default 1.0)
            gain (float): Volume multiplier (default 1.0)

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
            sustain_level=0.7 * gain,
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

    def sonify_binomial(self, n=100, p=0.5, base_freq=200, num_samples=100, duration=1.0):
        """Create audio from a binomial distribution.

        Args:
            n (int): Number of trials
            p (float): Probability of success per trial
            base_freq (float): Base frequency to add to samples
            num_samples (int): Number of frequency samples
            duration (float): Duration in seconds

        Returns:
            Signal: Audio signal
        """
        samples = self.rng.binomial(n, p, num_samples).astype(float) + base_freq
        return self.sonify(samples, duration)

    def sonify_scipy(self, dist, freq_range=(220, 880), num_samples=100, duration=1.0):
        """Create audio from any scipy.stats distribution.

        Args:
            dist: A scipy.stats distribution object (frozen or unfrozen)
            freq_range (tuple): (min_freq, max_freq) to map distribution to
            num_samples (int): Number of frequency samples
            duration (float): Duration in seconds

        Returns:
            Signal: Audio signal

        Example:
            from scipy import stats
            ps.sonify_scipy(stats.norm(loc=0, scale=1))
            ps.sonify_scipy(stats.chi2(df=3))
        """
        # Sample from distribution and map to frequency range
        samples = dist.rvs(size=num_samples, random_state=self.rng)
        # Normalize to [0, 1] using distribution's CDF, then scale to freq range
        normalized = dist.cdf(samples)
        min_freq, max_freq = freq_range
        freq_samples = normalized * (max_freq - min_freq) + min_freq
        return self.sonify(freq_samples, duration)

    def sonify_mixture(self, distributions, weights=None, num_samples=100, duration=1.0):
        """Create audio from a mixture of distributions.

        Args:
            distributions (list): List of (dist_name, params) tuples
                e.g., [('normal', {'mean': 300, 'std': 30}),
                       ('normal', {'mean': 600, 'std': 30})]
            weights (list): Mixing weights (default: equal weights)
            num_samples (int): Total number of frequency samples
            duration (float): Duration in seconds

        Returns:
            Signal: Audio signal

        Example:
            # Bimodal distribution
            ps.sonify_mixture([
                ('normal', {'mean': 300, 'std': 20}),
                ('normal', {'mean': 600, 'std': 20})
            ])
        """
        if weights is None:
            weights = [1.0 / len(distributions)] * len(distributions)
        weights = np.array(weights) / sum(weights)  # Normalize

        all_samples = []
        for (dist_name, params), weight in zip(distributions, weights):
            n = int(num_samples * weight)
            if dist_name == 'normal':
                samples = self.rng.normal(params.get('mean', 440), params.get('std', 50), n)
            elif dist_name == 'uniform':
                samples = self.rng.uniform(params.get('low', 220), params.get('high', 880), n)
            elif dist_name == 'beta':
                s = self.rng.beta(params.get('a', 2), params.get('b', 2), n)
                low, high = params.get('freq_range', (220, 880))
                samples = s * (high - low) + low
            elif dist_name == 'exponential':
                samples = self.rng.exponential(params.get('scale', 100), n) + params.get('base_freq', 200)
            else:
                raise ValueError(f"Unknown distribution: {dist_name}")
            all_samples.extend(samples)

        return self.sonify(np.array(all_samples), duration)

    def compare(self, signal1, signal2, gap=0.3):
        """Play two signals sequentially for comparison.

        Args:
            signal1 (Signal): First signal
            signal2 (Signal): Second signal
            gap (float): Silence gap between signals in seconds

        Returns:
            Signal: Combined signal with gap

        Example:
            tight = ps.sonify_normal(440, 20, num_samples=50)
            wide = ps.sonify_normal(440, 100, num_samples=50)
            ps.compare(tight, wide)  # Hear the difference!
        """
        gap_samples = int(gap * self.sample_rate)
        silence = Signal(np.zeros(gap_samples), self.sample_rate)
        return signal1 + silence + signal2

    def sonify_clt(self, n_dice=1, rolls_per_sample=100, num_samples=100, duration=1.0):
        """Demonstrate the Central Limit Theorem through sound.

        Sum of n_dice uniform random variables approaches normal distribution.
        With n_dice=1, sounds chaotic/uniform. As n_dice increases, sounds
        more focused/normal around the mean.

        Args:
            n_dice (int): Number of dice to sum (higher = more normal)
            rolls_per_sample (int): Samples per frequency point
            num_samples (int): Number of frequency samples
            duration (float): Duration in seconds

        Returns:
            Signal: Audio signal

        Example:
            ps.sonify_clt(n_dice=1)   # Uniform - chaotic
            ps.sonify_clt(n_dice=10)  # More normal - focused
            ps.sonify_clt(n_dice=30)  # Very normal - tight
        """
        # Each "frequency" is the mean of n_dice uniform [0,1] values
        # Scaled to audible range
        samples = []
        for _ in range(num_samples):
            dice_sum = self.rng.uniform(0, 1, n_dice).mean()
            samples.append(dice_sum)

        # Scale to frequency range (wider range for low n_dice)
        samples = np.array(samples)
        # Map [0, 1] to frequency range
        min_freq, max_freq = 220, 880
        freq_samples = samples * (max_freq - min_freq) + min_freq
        return self.sonify(freq_samples, duration)

    def sonify_clt_progression(self, stages=(1, 2, 5, 10, 30), duration_each=1.0, gap=0.2):
        """Play CLT progression: hear uniform converge to normal.

        Creates a sequence demonstrating how the sum of uniform random
        variables converges to a normal distribution as n increases.

        Args:
            stages (tuple): Values of n_dice to demonstrate
            duration_each (float): Duration of each stage in seconds
            gap (float): Silence between stages in seconds

        Returns:
            Signal: Combined audio of all stages

        Example:
            # Default progression: n=1,2,5,10,30
            signal = ps.sonify_clt_progression()
            signal.to_audio()  # Hear uniform -> normal!
        """
        signals = []
        silence = Signal(np.zeros(int(gap * self.sample_rate)), self.sample_rate)

        for i, n in enumerate(stages):
            sig = self.sonify_clt(n_dice=n, num_samples=80, duration=duration_each)
            signals.append(sig)
            if i < len(stages) - 1:
                signals.append(silence)

        # Concatenate all
        result = signals[0]
        for sig in signals[1:]:
            result = result + sig
        return result

    def sonify_lln(self, true_mean=440, sample_sizes=(5, 20, 100, 500), duration_each=0.8):
        """Demonstrate the Law of Large Numbers through sound.

        As sample size increases, the sample mean converges to the true mean.
        Early samples sound scattered; larger samples converge to a pure tone.

        Args:
            true_mean (float): The true population mean (frequency in Hz)
            sample_sizes (tuple): Sample sizes to demonstrate
            duration_each (float): Duration of each stage

        Returns:
            Signal: Combined audio demonstrating convergence

        Example:
            # Hear sample mean converge to 440Hz
            ps.sonify_lln(true_mean=440)
        """
        signals = []
        gap = Signal(np.zeros(int(0.15 * self.sample_rate)), self.sample_rate)

        for i, n in enumerate(sample_sizes):
            # Generate n samples, compute running means
            raw_samples = self.rng.normal(true_mean, 100, n)
            # Use the sample means as frequencies (shows convergence)
            running_means = np.cumsum(raw_samples) / np.arange(1, n + 1)
            # Take subset to avoid too many frequencies
            freq_samples = running_means[::max(1, n // 50)]
            sig = self.sonify(freq_samples, duration_each)
            signals.append(sig)
            if i < len(sample_sizes) - 1:
                signals.append(gap)

        result = signals[0]
        for sig in signals[1:]:
            result = result + sig
        return result