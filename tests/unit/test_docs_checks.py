"""Regression cases for the public documentation link gate."""
from pathlib import Path
import tempfile
import unittest

from scripts.check_docs import anchors, check_links


class DocumentationChecksTest(unittest.TestCase):
    def test_heading_anchors_preserve_unicode_and_number_duplicates(self):
        text = "# 配置 `field_name`\n## Repeated\n## Repeated\nTitle\n=====\n```md\n# Ignored\n```\n"
        self.assertEqual(anchors(text), {"配置-field_name", "repeated", "repeated-1", "title"})

    def test_local_links_references_and_fenced_examples(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "README.md"
            (root / "target.md").write_text("# Valid\n## Valid\n", encoding="utf-8")
            source.write_text(
                "[ok](target.md#valid-1)\n[ref][target]\n[target]: target.md#valid\n"
                "[bad](target.md#absent)\n[missing](missing.md)\n"
                "[web](https://example.org/unrequested)\n[unknown][undefined]\n"
                "```md\n[example](not-real.md)\n```\n", encoding="utf-8")
            errors, count = check_links([source], root)
            self.assertEqual(count, 4)
            self.assertEqual(len(errors), 3)
            self.assertTrue(any("missing Markdown anchor" in error for error in errors))
            self.assertTrue(any("missing target" in error for error in errors))
            self.assertTrue(any("undefined reference" in error for error in errors))

    def test_encoded_paths_and_explicit_anchors(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "README.md"
            (root / "a b.md").write_text('<a id="custom"></a>\n', encoding="utf-8")
            source.write_text("[link](a%20b.md#custom)\n", encoding="utf-8")
            self.assertEqual(check_links([source], root), ([], 1))
