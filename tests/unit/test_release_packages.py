"""Release archive checks reject stale content and unsafe members."""
import importlib.util
from pathlib import Path
import tarfile
import tempfile
import unittest
from unittest.mock import patch
import zipfile


ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location("verify_packages", ROOT / "scripts/verify_packages.py")
PACKAGES = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(PACKAGES)


class ReleasePackageTests(unittest.TestCase):
    def test_path_traversal_member_is_rejected_without_extraction(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "bad.whl"
            with zipfile.ZipFile(path, "w") as archive:
                archive.writestr("../outside", "do not extract")
            with self.assertRaisesRegex(ValueError, "Unsafe/duplicate"):
                PACKAGES.load_archive(path)
            self.assertFalse((Path(directory).parent / "outside").exists())

    def test_tar_symlink_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "bad.tgz"
            with tarfile.open(path, "w:gz") as archive:
                member = tarfile.TarInfo("package/link")
                member.type = tarfile.SYMTYPE
                member.linkname = "/etc/passwd"
                archive.addfile(member)
            with self.assertRaisesRegex(ValueError, "Non-regular"):
                PACKAGES.load_archive(path)

    def test_wheel_symlink_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "bad.whl"
            with zipfile.ZipFile(path, "w") as archive:
                member = zipfile.ZipInfo("forgeflow/link")
                member.create_system = 3
                member.external_attr = 0o120777 << 16
                archive.writestr(member, "/etc/passwd")
            with self.assertRaisesRegex(ValueError, "Non-regular"):
                PACKAGES.load_archive(path)

    def test_project_evidence_and_environment_files_are_rejected(self):
        for name in ("package/.forgeflow/artifacts/planning.md",
                     "package/.forgeflow/reports/security.md", "package/.env.local"):
            with self.subTest(name=name), tempfile.TemporaryDirectory() as directory:
                path = Path(directory) / "bad.whl"
                with zipfile.ZipFile(path, "w") as archive:
                    archive.writestr(name, "private")
                with self.assertRaises(ValueError):
                    PACKAGES.load_archive(path)

    def test_stale_template_is_rejected(self):
        with patch.object(PACKAGES, "load_archive", return_value={
            "forgeflow/_template/forgeflow.json": b"{}"
        }):
            with self.assertRaisesRegex(ValueError, "Missing/stale bundled file"):
                PACKAGES.verify(Path("candidate.whl"), "wheel", "0.1.0")


if __name__ == "__main__":
    unittest.main()
