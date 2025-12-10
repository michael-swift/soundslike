"""Simple audio synthesis module using numpy and scipy."""

from .tone import SineWave
from .signal import Signal, MixSignal
from .envelope import ADSR

__all__ = ['SineWave', 'Signal', 'MixSignal', 'ADSR']
