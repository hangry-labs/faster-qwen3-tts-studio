"""Official checkpoint identities shared by inference and image prefetching."""

REVISIONS = {
    '0.6B-Base': '5d83992436eae1d760afd27aff78a71d676296fc',
    '1.7B-Base': 'fd4b254389122332181a7c3db7f27e918eec64e3',
    '0.6B-CustomVoice': '85e237c12c027371202489a0ec509ded67b5e4b5',
    '1.7B-CustomVoice': '0c0e3051f131929182e2c023b9537f8b1c68adfe',
    '1.7B-VoiceDesign': '5ecdb67327fd37bb2e042aab12ff7391903235d3',
}
MODELS = {
    f'Qwen/Qwen3-TTS-12Hz-{name}': {
        'id': f'Qwen/Qwen3-TTS-12Hz-{name}', 'label': name, 'revision': revision,
        'mode': 'clone' if name.endswith('Base') else 'design' if name.endswith('VoiceDesign') else 'custom',
        'instructions': name.endswith('Base') or name.startswith('1.7B'),
        'instruction_support': 'experimental' if name.endswith('Base') else 'supported' if name.startswith('1.7B') else 'none',
        'license': 'Apache-2.0',
    } for name, revision in REVISIONS.items()
}
