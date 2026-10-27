"""Offline legal-artifact regression checks; no model/runtime dependencies."""
import io
from pathlib import Path
import tempfile
import tarfile
import unittest
import zipfile

from scripts.check_licensing import ROOT, check_artifact, check_notice_text, check_source
from scripts.collect_runtime_licenses import native_file, native_name, notice_name, supplemental_notice


class LicensingTests(unittest.TestCase):
    def test_source_notices(self):
        self.assertEqual([], check_source(ROOT))

    def test_consolidation_preserves_original_license_texts(self):
        notices = (ROOT / "THIRD_PARTY_NOTICES.md").read_text(encoding="utf-8")
        self.assertEqual([], check_notice_text(notices.replace("\n", "\r\n")))
        for original in ("Copyright (c) 2026 Thanh Sang", "3. Grant of Patent License."):
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

    def test_private_upstream_ledgers_are_rejected_in_artifacts(self):
        for name in ('UPSTREAM_ISSUES.md', 'UPSTREAM_PULL_REQUESTS.md'):
            with self.subTest(name=name), tempfile.TemporaryDirectory() as folder:
                wheel = Path(folder) / 'bad.whl'
                with zipfile.ZipFile(wheel, 'w') as archive:
                    archive.writestr('package-1.dist-info/METADATA', 'License-Expression: MIT AND Apache-2.0\n')
                    for notice in ('LICENSE', 'NOTICE', 'THIRD_PARTY_NOTICES.md'):
                        archive.writestr('package-1.dist-info/licenses/'+notice, (ROOT/notice).read_bytes())
                    archive.writestr(name, 'Private triage')
                self.assertEqual(['Private material in distribution: '+name], check_artifact(wheel))

    def test_internal_document_is_rejected_in_otherwise_valid_artifacts(self):
        with tempfile.TemporaryDirectory() as folder:
            wheel = Path(folder) / 'package.whl'
            with zipfile.ZipFile(wheel, 'w') as archive:
                archive.writestr('package-1.dist-info/METADATA', 'License-Expression: MIT AND Apache-2.0\n')
                for name in ('LICENSE', 'NOTICE', 'THIRD_PARTY_NOTICES.md'):
                    archive.writestr('package-1.dist-info/licenses/' + name, (ROOT / name).read_bytes())
                archive.writestr('docs/internal/review.md', 'Internal review')
            self.assertEqual(['Private material in distribution: docs/internal/review.md'], check_artifact(wheel))

            source = Path(folder) / 'package.tar.gz'
            with tarfile.open(source, 'w:gz') as archive:
                for name in ('LICENSE', 'NOTICE', 'THIRD_PARTY_NOTICES.md', 'docs/LICENSING.md',
                             'docs/internal/review.md'):
                    content = b'Internal review' if name.endswith('review.md') else (ROOT / name).read_bytes()
                    member = tarfile.TarInfo('package-1/' + name)
                    member.size = len(content)
                    archive.addfile(member, io.BytesIO(content))
            self.assertEqual(['Private material in distribution: package-1/docs/internal/review.md'], check_artifact(source))

    def test_runtime_collector_recognizes_vendored_notice_paths(self):
        self.assertTrue(notice_name("pkg.dist-info/licenses/third_party/terms.txt"))
        self.assertTrue(notice_name("pkg/LICENCE"))
        self.assertTrue(notice_name("pkg/COPYING.LGPL"))
        self.assertFalse(notice_name("pkg/model.safetensors"))

    def test_runtime_collector_includes_bundled_versioned_libraries(self):
        for name in ('torch/lib/libgomp.so.1', 'numpy.libs/libgfortran-hash.so.5.0.0',
                     'nvidia/cublas/lib/libcublas.so.12', 'pkg/extension.so',
                     r'pkg\extension.PYD', 'pkg/libdevice.a', 'pkg/kernel.cubin'):
            with self.subTest(name=name):
                self.assertTrue(native_name(name))
        for name in ('pkg/foo.so.py', 'pkg/README.so.txt', 'pkg/model.safetensors'):
            with self.subTest(name=name):
                self.assertFalse(native_name(name))

    def test_runtime_collector_identifies_extensionless_elf_tools(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'ptxas'
            path.write_bytes(b'\x7fELF' + b'\0' * 32)
            self.assertTrue(native_file(path, 'triton/backends/nvidia/bin/ptxas'))
            path.write_text('ordinary source text', encoding='utf-8')
            self.assertFalse(native_file(path, 'package/module.py'))

    def test_supplemental_notice_is_limited_to_verified_version_and_present_document(self):
        document = ROOT / 'THIRD_PARTY_NOTICES.md'
        self.assertTrue(supplemental_notice('tokenizers', '0.22.2', document))
        self.assertFalse(supplemental_notice('tokenizers', '0.22.3', document))
        self.assertTrue(supplemental_notice('torch', '2.10.0+cu128', document))
        self.assertFalse(supplemental_notice('torch', '2.11.0+cu128', document))
        self.assertFalse(supplemental_notice('unrelated', '0.22.2', document))
        self.assertFalse(supplemental_notice('tokenizers', '0.22.2', document / 'absent'))
        with tempfile.TemporaryDirectory() as folder:
            unrelated = Path(folder) / 'NOTICE.md'
            unrelated.write_text('An unrelated notice', encoding='utf-8')
            self.assertFalse(supplemental_notice('tokenizers', '0.22.2', unrelated))

    def test_vendor_license_does_not_replace_or_duplicate_root_license(self):
        with tempfile.TemporaryDirectory() as folder:
            for root_license in (True, False):
                with self.subTest(root_license=root_license):
                    package = Path(folder) / 'package.tar.gz'
                    with tarfile.open(package, 'w:gz') as archive:
                        for name in ('LICENSE', 'NOTICE', 'THIRD_PARTY_NOTICES.md', 'docs/LICENSING.md', 'vendor/LICENSE'):
                            if name == 'LICENSE' and not root_license:
                                continue
                            content = b'Vendor notice' if name == 'vendor/LICENSE' else (ROOT / name).read_bytes()
                            member = tarfile.TarInfo('package-1/' + name)
                            member.size = len(content)
                            archive.addfile(member, io.BytesIO(content))
                    errors = check_artifact(package)
                    if root_license:
                        self.assertEqual([], errors)
                    else:
                        self.assertTrue(any('LICENSE' in error for error in errors))


if __name__ == "__main__":
    unittest.main()
