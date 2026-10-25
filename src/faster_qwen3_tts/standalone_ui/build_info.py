"""Public build identity, supplied by the image build rather than runtime Git."""
import os

from faster_qwen3_tts import __version__


def build_identity():
    return {'version': __version__, 'build_id': os.getenv('QWEN_STUDIO_BUILD_ID', 'unknown'),
            'build_date': os.getenv('QWEN_STUDIO_BUILD_DATE', 'unknown'),
            'image_version': os.getenv('QWEN_STUDIO_IMAGE_VERSION', 'development')}
