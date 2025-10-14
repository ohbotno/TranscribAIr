"""
Python 3.13 compatibility fix for pydub.
The audioop module was removed in Python 3.13.
This module provides a minimal compatibility layer.
"""
import sys

if sys.version_info >= (3, 13):
    # Install stub audioop module for Python 3.13+
    try:
        import audioop
    except ModuleNotFoundError:
        # Create a minimal audioop stub
        # pydub will fall back to ffmpeg for operations
        import types
        audioop = types.ModuleType('audioop')
        sys.modules['audioop'] = audioop
