# CLAUDE.md - SoundsLike Repository Guide

## Project Overview

**SoundsLike** is a Python library for sonifying probability distributions and statistical concepts. It converts mathematical distributions into audible sound, allowing users to "hear" probability distributions as audio signals where frequencies map to distribution values.

**Author:** Michael Swift
**License:** MIT
**Version:** 0.1.0

## Repository Structure

```
soundslike/
├── soundslike/              # Main package
│   ├── __init__.py          # Exports ProbabilitySounds class
│   └── soundslike.py        # Core implementation
├── tests/
│   └── test_soundslike.py   # Pytest test suite
├── examples/
│   ├── demo.ipynb           # Interactive demo notebook
│   ├── POC_nb/cs109.ipynb   # Proof of concept notebook
│   ├── 2024-08-04-sound_prob.md  # Blog post explaining concepts
│   └── sound_output/        # Generated audio/image files
├── environment.yml          # Conda environment specification
├── setup.py                 # Package installation config
├── README.md                # Project readme
├── LICENSE                  # MIT license
└── .gitignore               # Git ignore rules
```

## Core Architecture

### Main Class: `ProbabilitySounds`

Located in `soundslike/soundslike.py`, this is the primary interface:

```python
from soundslike import ProbabilitySounds

ps = ProbabilitySounds(sample_rate=44100, output_dir='output')
```

**Key Methods:**
- `play_normal(mean, std, num_samples)` - Sonify a normal/Gaussian distribution
- `play_beta(a, b, freq_range, num_samples)` - Sonify a beta distribution
- `play_uniform(low, high, num_samples)` - Sonify a uniform distribution
- `play_distribution(dist_samples, duration, save, prefix, title)` - Play any array of frequencies
- `plot_distribution(dist_array, title, save)` - Visualize distribution as histogram

**Audio Pipeline:**
1. Generate frequency samples from distribution (numpy)
2. Clip frequencies to audible range (20Hz - 20kHz)
3. Create sine waves for each frequency (sound-machine library)
4. Mix signals and apply ADSR envelope
5. Play audio and save to WAV file

## Development Setup

### Environment Setup (Conda)

```bash
conda env create -f environment.yml
conda activate sounds
```

### Dependencies

**Runtime:**
- `numpy>=1.20.0` - Numerical operations
- `matplotlib>=3.5.0` - Plotting
- `seaborn>=0.11.0` - Statistical visualization
- `sound-machine>=0.1.0` - Audio synthesis (SineWave, Signal, ADSR)

**Development:**
- `pytest>=7.0.0` - Testing framework
- `pytest-cov>=3.0.0` - Coverage reporting
- `black>=22.0.0` - Code formatting
- `jupyter` - Notebook support

### Install Package Locally

```bash
pip install -e .
```

## Development Workflows

### Running Tests

```bash
pytest tests/
pytest tests/ -v                    # Verbose output
pytest tests/ --cov=soundslike      # With coverage
```

### Code Formatting

```bash
black soundslike/ tests/
```

### Running Examples

```bash
jupyter notebook examples/demo.ipynb
```

## Key Conventions

### Code Style
- Follow PEP 8 conventions
- Use `black` for auto-formatting
- Use type hints where practical
- Include docstrings for public methods

### Logging
- The library uses Python's `logging` module
- Logs are written to `soundslike.log` and stdout
- Log format: `%(asctime)s - %(name)s - %(levelname)s - %(message)s`

### File Output
- Audio files saved as WAV format
- Plots saved as PNG format
- Files are timestamped: `{prefix}_{YYYYMMDD_HHMMSS}.{ext}`
- Default output directory: `output/`

### Frequency Handling
- Frequencies are clipped to audible range: 20Hz - 20,000Hz
- Default sample rate: 44100 Hz
- Musical reference: A440 (440Hz) is commonly used as the default mean

## Testing Guidelines

- Tests use `pytest` with fixtures for temporary directories
- Use `tempfile.TemporaryDirectory` for test output isolation
- Test files should be prefixed with `test_`
- Current test file: `tests/test_soundslike.py`

## Common Tasks

### Adding a New Distribution

1. Add method to `ProbabilitySounds` class in `soundslike/soundslike.py`
2. Generate samples using `numpy.random` or `scipy.stats`
3. Call `self.play_distribution()` with the samples
4. Add corresponding test in `tests/test_soundslike.py`

### Modifying Audio Parameters

The `ADSR` envelope in `play_distribution()` controls the sound shape:
- `attack`: Time for sound to reach full volume (0.1s default)
- `decay`: Time to reach sustain level (0.1s default)
- `sustain`: Duration of sustain phase (0.6s default)
- `sustain_level`: Volume during sustain (0.7 = 70%)
- `release`: Fade-out time (0.2s default)

## Known Issues / Notes

1. The test `test_frequency_scaling` references a method `ps.play_sound()` that doesn't exist in the current implementation (should be `play_distribution`)
2. The `setup.py` lists `pippi` as a dependency but `environment.yml` uses `sound-machine` - these may be related libraries
3. Audio playback requires a working audio output device

## External Resources

- NumPy random distributions: https://numpy.org/doc/stable/reference/random/
- Sound-machine library for audio synthesis
- Seaborn for statistical visualizations
