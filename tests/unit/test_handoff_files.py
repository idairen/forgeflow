import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from forgeflow.engine.handoff_files import HandoffFiles
from forgeflow.engine.handoff_parser import HandoffParser


class HandoffFilesTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.files = HandoffFiles(Path(self.temp.name))
        self.block = HandoffParser.render_resolution({
            'pipeline_status': 'ACTIVE', 'current_workflow': 'grill',
            'target_scope': 'Feature: F-01', 'resolution_rule': 'rule_5_requirement_required',
            'input_artifacts': [{'filename': 'planning.md', 'version': '1.0'}],
        })

    def test_return_complete_and_halted_file_variants(self):
        resolutions = [
            ({'pipeline_status': 'ACTIVE', 'current_workflow': 'implement',
              'target_scope': 'Slice: F-01/S-01', 'resolution_rule': 'rule_8_review_failure',
              'blocker_category': 'REVIEW_BLOCKER',
              'input_artifacts': [{'filename': 'review-feature-01-slice-01-attempt-01.md', 'version': '1.0'}]},
             'Slice: F-01/S-01', 'review', 'RETURN'),
            ({'pipeline_status': 'COMPLETE', 'resolution_rule': 'rule_11_complete',
              'input_artifacts': [{'filename': 'review-feature-01-slice-01-attempt-01.md', 'version': '1.0'}]},
             'Slice: F-01/S-01', 'review', 'TERMINAL'),
            ({'pipeline_status': 'HALTED', 'resolution_rule': 'rule_2_graph_contradiction',
              'reason_code': 'artifact_invalid', 'input_artifacts': []},
             'Project', None, 'TERMINAL'),
        ]
        for resolution, scope, source, transition in resolutions:
            with self.subTest(transition=transition, status=resolution['pipeline_status']):
                path = self.files.publish(HandoffParser.render_resolution(resolution, scope), source)
                self.assertEqual(self.files.read(path)['handoff']['transition'], transition)

    def test_parallel_feature_files_do_not_overwrite_each_other(self):
        resolution = {'pipeline_status': 'ACTIVE', 'current_workflow': 'solution',
                      'target_scope': 'Project', 'resolution_rule': 'rule_6_solution_required',
                      'input_artifacts': [{'filename': 'planning.md', 'version': '1.0'}]}
        first = self.files.publish(HandoffParser.render_resolution(resolution, 'Feature: F-01'), 'grill')
        original = first.read_bytes()
        second = self.files.publish(HandoffParser.render_resolution(resolution, 'Feature: F-02'), 'grill')
        self.assertNotEqual(first.parent, second.parent)
        self.assertEqual(first.read_bytes(), original)

    def test_publish_read_and_discover_without_runtime(self):
        path = self.files.publish(self.block, 'plan')
        record = self.files.read(path)
        self.assertEqual(record['source_workflow'], 'plan')
        self.assertEqual(record['handoff']['next_workflow'], 'grill')
        self.assertEqual(self.files.paths(), {path})
        self.assertFalse((Path(self.temp.name) / '.forgeflow/runtime').exists())

    def test_duplicate_equivalent_and_stale_selection(self):
        self.files.publish(self.block, 'plan')
        self.files.publish(self.block, 'plan')
        record = self.files.select(lambda record: [])
        self.assertIsNotNone(record)
        self.assertIsNone(self.files.select(lambda record: ['stale_version']))

    def test_conflicting_candidates_require_selection(self):
        self.files.publish(self.block, 'plan')
        self.files.publish(self.block.replace('rule_5_requirement_required', 'different reason'), 'plan')
        with self.assertRaisesRegex(ValueError, 'ambiguous'):
            self.files.select(lambda record: [])

    def test_wrong_id_schema_path_and_duplicate_block_are_rejected(self):
        path = self.files.publish(self.block, 'plan')
        original = path.read_text()
        for text in (original.replace('Schema Version | 1.0', 'Schema Version | 9.0'),
                     original.replace(path.stem, 'bad-id'), original + '\n' + self.block):
            path.write_text(text)
            with self.assertRaises(ValueError):
                self.files.read(path)
        path.write_text(original)
        wrong = path.parent.parent / 'feature-01' / path.name
        wrong.parent.mkdir()
        path.rename(wrong)
        with self.assertRaises(ValueError):
            self.files.read(wrong)

    def test_collision_never_overwrites_and_temp_files_are_ignored(self):
        with patch('forgeflow.engine.handoff_files.uuid4', return_value='00000000-0000-4000-8000-000000000001'):
            path = self.files.publish(self.block, 'plan')
            original = path.read_bytes()
            with self.assertRaises(FileExistsError):
                self.files.publish(self.block, 'plan')
            self.assertEqual(path.read_bytes(), original)
        (path.parent / '.partial.tmp').write_text('partial')
        self.assertEqual(self.files.paths(), {path})

    def test_correction_requires_project_scope_and_no_workflow(self):
        path = self.files.publish(self.block)
        self.assertEqual(self.files.read(path)['producer'], 'Routing Correction')
        with self.assertRaises(ValueError):
            self.files.publish(self.block.replace('Source Scope | Project', 'Source Scope | Feature: F-01'))

    def test_symlink_is_not_project_evidence(self):
        path = self.files.publish(self.block, 'plan')
        original = path.read_text()
        path.unlink()
        external = Path(self.temp.name) / 'external.md'
        external.write_text(original)
        path.symlink_to(external)
        with self.assertRaises(ValueError):
            self.files.read(path)
