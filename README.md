# SoundsLike

A Python library for **sonifying probability distributions** - hear what your data sounds like!

**[Try the Live Demo](https://michael-swift.github.io/soundslike/)** - No installation required!

SoundsLike converts probability distributions into audio, mapping statistical values to frequencies. This provides an intuitive, auditory way to understand distributions: tight distributions sound focused, wide distributions sound diffuse, and skewed distributions emphasize certain frequency ranges.

## Installation

```bash
# Clone the repository
git clone https://github.com/michael-swift/soundslike.git
cd soundslike

# Install with pip
pip install -e .
```

### Dependencies

- Python 3.8+
- numpy
- scipy
- matplotlib
- seaborn

## Quick Start

```python
from soundslike import ProbabilitySounds

# Create a sonifier
ps = ProbabilitySounds()

# Create audio from a normal distribution centered on A440
signal = ps.sonify_normal(mean=440, std=50, num_samples=100)

# In a Jupyter notebook, play directly:
signal.to_audio()

# Or save to a WAV file:
signal.write("normal_distribution.wav")
```

## Available Distributions

```python
# Normal (Gaussian) distribution
ps.sonify_normal(mean=440, std=50, num_samples=100)

# Uniform distribution
ps.sonify_uniform(low=220, high=880, num_samples=100)

# Beta distribution (scaled to frequency range)
ps.sonify_beta(a=2, b=5, freq_range=(220, 880), num_samples=100)

# Exponential distribution
ps.sonify_exponential(scale=100, base_freq=200, num_samples=100)

# Poisson distribution
ps.sonify_poisson(lam=440, num_samples=100)

# Any custom frequency array
ps.sonify(my_frequency_array, duration=1.0)
```

## Interactive Demos

### Web Demo (Recommended)

The easiest way to experience SoundsLike is through the **[live web demo](https://michael-swift.github.io/soundslike/)** - works in any browser, no installation required!

Features:
- Select from Normal, Uniform, Beta, and Exponential distributions
- Adjust parameters with sliders and hear the results instantly
- See the frequency histogram update in real-time

### Jupyter Notebook

For a more in-depth exploration with Python:

```bash
jupyter notebook examples/demo.ipynb
```

The notebook demo includes:
- Comparing tight vs wide normal distributions
- Hearing how beta distribution shape affects sound
- Understanding sample size effects
- Creating musical chords from distributions

## How It Works

1. **Generate frequencies**: Sample values from a probability distribution
2. **Map to audio range**: Clip frequencies to the audible range (20Hz - 20kHz)
3. **Create sine waves**: Generate a sine wave for each frequency
4. **Mix and envelope**: Combine signals and apply an ADSR envelope for smooth sound
5. **Output**: Play in notebook or save as WAV file

## API Reference

### ProbabilitySounds

The main class for sonifying distributions.

```python
ps = ProbabilitySounds(sample_rate=44100, output_dir='output')
```

**Sonification methods** (return `Signal` objects):
- `sonify(freq_samples, duration)` - Sonify any frequency array
- `sonify_normal(mean, std, num_samples, duration)` - Normal distribution
- `sonify_uniform(low, high, num_samples, duration)` - Uniform distribution
- `sonify_beta(a, b, freq_range, num_samples, duration)` - Beta distribution
- `sonify_exponential(scale, base_freq, num_samples, duration)` - Exponential
- `sonify_poisson(lam, num_samples, duration)` - Poisson distribution

### Signal

Audio container returned by sonification methods.

```python
signal = ps.sonify_normal(440, 50, 100)
signal.to_audio()      # IPython Audio widget for notebooks
signal.write("out.wav") # Save to WAV file
signal.to_numpy()      # Get raw audio samples as numpy array
```

## License

MIT License - see [LICENSE](LICENSE) for details.

## Author

Michael Swift
