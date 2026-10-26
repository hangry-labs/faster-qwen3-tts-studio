"""Shared resource limits for streaming waveform reconstruction."""

DEFAULT_DECODER_CONTEXT_FRAMES = 25
MAX_DECODER_CONTEXT_FRAMES = 200


def validate_decoder_context_frames(value: int) -> int:
    """Bound repeated decoder work without changing token generation."""
    if isinstance(value, bool) or not isinstance(value, int) or not 1 <= value <= MAX_DECODER_CONTEXT_FRAMES:
        raise ValueError(f'decoder_context_frames must be an integer from 1 to {MAX_DECODER_CONTEXT_FRAMES}')
    return value
