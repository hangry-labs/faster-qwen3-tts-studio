"""Offline legal-artifact regression checks; no model/runtime dependencies."""
import ast
from pathlib import Path
import tempfile
import types
import unittest
import zipfile

from scripts.check_licensing import ROOT, check_artifact, check_notice_text, check_source
from scripts.collect_runtime_licenses import notice_name


class LicensingTests(unittest.TestCase):
    def test_source_notices_and_media_download_policy(self):
        self.assertEqual([], check_source(ROOT))

    def test_consolidation_preserves_original_license_texts(self):
        notices = (ROOT / "THIRD_PARTY_NOTICES.md").read_text(encoding="utf-8")
        self.assertEqual([], check_notice_text(notices.replace("\n", "\r\n")))
        for original in ("Copyright (c) 2026 Andrés Marafioti", "3. Grant of Patent License."):
            with self.subTest(text=original):
                self.assertTrue(check_notice_text(notices.replace(original, "removed")))

    def test_wheel_cannot_drop_notices_or_include_private_payload(self):
        with tempfile.TemporaryDirectory() as folder:
            wheel = Path(folder) / "bad.whl"
            with zipfile.ZipFile(wheel, "w") as archive:
                archive.writestr("package-1.dist-info/METADATA", "License-Expression: MIT\n")
                archive.writestr(".ai/context/AGENTS.md", "private")
                archive.writestr("ref_audio.wav", b"audio")
            errors = check_artifact(wheel)
            self.assertTrue(any("mixed-source" in error for error in errors))
            self.assertTrue(any("missing license" in error for error in errors))
            self.assertTrue(any("Private material" in error for error in errors))
            self.assertTrue(any("media/model" in error for error in errors))

    def test_complete_notice_only_wheel_passes(self):
        with tempfile.TemporaryDirectory() as folder:
            wheel = Path(folder) / "good.whl"
            with zipfile.ZipFile(wheel, "w") as archive:
                archive.writestr("package-1.dist-info/METADATA", "License-Expression: MIT AND Apache-2.0\n")
                for name in ("LICENSE", "NOTICE", "THIRD_PARTY_NOTICES.md"):
                    archive.writestr("package-1.dist-info/licenses/" + name, (ROOT / name).read_text(encoding="utf-8"))
            self.assertEqual([], check_artifact(wheel))

    def test_runtime_collector_recognizes_vendored_notice_paths(self):
        self.assertTrue(notice_name("pkg.dist-info/licenses/third_party/terms.txt"))
        self.assertTrue(notice_name("pkg/LICENCE"))
        self.assertTrue(notice_name("pkg/COPYING.LGPL"))
        self.assertFalse(notice_name("pkg/model.safetensors"))

    def test_presets_do_not_read_unapproved_local_audio_by_default(self):
        tree = ast.parse((ROOT / "demo/server.py").read_text(encoding="utf-8"))
        function = next(node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == "_load_preset_refs")
        module = ast.Module(body=[function], type_ignores=[])
        presets = {"stale": {}}
        def unexpected_read():
            self.fail("Default startup must not read preset references")
        namespace = {"os": types.SimpleNamespace(environ={}), "_preset_refs": presets,
                     "_load_preset_transcripts": unexpected_read}
        exec(compile(module, "demo/server.py", "exec"), namespace)
        namespace["_load_preset_refs"]()
        self.assertEqual({}, presets)


if __name__ == "__main__":
    unittest.main()
