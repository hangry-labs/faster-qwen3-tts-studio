"""Catalog coverage protects translated workflows as the UI evolves."""
from html.parser import HTMLParser
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
STATIC = ROOT / 'src/faster_qwen3_tts/standalone_ui/static'


def test_static_messages_exist_and_never_replace_nested_controls():
    catalog = json.loads((STATIC / 'locales/en.json').read_text(encoding='utf-8'))

    class Inspect(HTMLParser):
        def __init__(self):
            super().__init__()
            self.stack = []
            self.ids = []

        def handle_starttag(self, tag, attributes):
            attrs = dict(attributes)
            assert not any('data-i18n' in entry for _, entry in self.stack), ('translated parent contains markup', tag)
            if 'id' in attrs:
                self.ids.append(attrs['id'])
            for name, value in attrs.items():
                if name == 'data-i18n' or name.startswith('data-i18n-'):
                    assert value in catalog, (name, value)
            if tag not in {'input', 'img', 'br', 'hr', 'meta', 'link', 'source', 'wbr', 'path'}:
                self.stack.append((tag, attrs))

        def handle_endtag(self, tag):
            for index in range(len(self.stack) - 1, -1, -1):
                if self.stack[index][0] == tag:
                    del self.stack[index:]
                    break

    parser = Inspect()
    parser.feed((STATIC / 'index.html').read_text(encoding='utf-8'))
    assert len(parser.ids) == len(set(parser.ids)), 'HTML IDs must remain unique'


def test_catalogs_have_equal_keys_valid_utf8_and_matching_placeholders():
    catalogs = {locale: json.loads((STATIC / f'locales/{locale}.json').read_text(encoding='utf-8'))
                for locale in ['en', 'nb', 'pl', 'ja', 'zh', 'es']}
    for locale, catalog in catalogs.items():
        assert catalog.keys() == catalogs['en'].keys(), locale
        for key, value in catalog.items():
            assert isinstance(value, str) and value.strip(), (locale, key)
            assert '\ufffd' not in value, (locale, key)
            assert sorted(re.findall(r'\{([a-zA-Z0-9_]+)\}', value)) == sorted(
                re.findall(r'\{([a-zA-Z0-9_]+)\}', catalogs['en'][key])), (locale, key)
            if key != '_attribution':
                assert 'VoxCPM' not in value, (locale, key)


def test_readme_translations_keep_runnable_commands_and_required_notices():
    command = 'docker run -d --name faster-qwen3-tts-studio'
    for locale in ['nb', 'pl', 'ja', 'zh', 'es']:
        text = (ROOT / f'README.{locale}.md').read_text(encoding='utf-8')
        assert command in text
        assert '127.0.0.1:7860:7860' in text and '--gpus all' in text
        assert '(THIRD_PARTY_NOTICES.md)' in text and '(docs/LICENSING.md)' in text
        assert '(README.md#version-history)' in text
        assert '\ufffd' not in text
