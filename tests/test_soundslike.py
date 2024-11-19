import pytest
import numpy as np
from soundslike import ProbabilitySounds
import tempfile
from pathlib import Path

@pytest.fixture
def ps():
    with tempfile.TemporaryDirectory() as tmpdir:
        yield ProbabilitySounds(output_dir=tmpdir)

def test_initialization(ps):
    assert ps.sample_rate == 44100
    assert isinstance(ps.output_dir, Path)

def test_generate_filename(ps):
    filename = ps._generate_filename("test")
    assert filename.parent == ps.output_dir
    assert filename.name.startswith("test_")
    assert filename.suffix == ".wav"

def test_play_normal(ps):
    mean, std = 300, 50
    num_samples = 100
    ps.play_normal(mean, std, num_samples)
    # Check that files were created
    wav_files = list(ps.output_dir.glob("*.wav"))
    png_files = list(ps.output_dir.glob("*.png"))
    assert len(wav_files) > 0
    assert len(png_files) > 0

def test_frequency_scaling(ps):
    # Test that frequencies are properly scaled to audible range
    freq_array = np.array([1, 10, 25000])
    num_samples = 3
    ps.play_sound(freq_array, num_samples)
    # Should not raise any errors 