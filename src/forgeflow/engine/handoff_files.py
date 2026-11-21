"""Portable, immutable Handoff documents; the current graph remains authoritative."""
import os
from pathlib import Path
import re
import tempfile
from uuid import UUID, uuid4

from .handoff_parser import HandoffParser


class HandoffFiles:
    def __init__(self, project_root):
        self.root = Path(project_root).absolute() / '.forgeflow' / 'handoffs'

    @staticmethod
    def directory(scope):
        if scope == 'Project':
            return 'project'
        return scope.replace('Feature: F-', 'feature-').replace(
            'Slice: F-', 'feature-').replace('/S-', '-slice-')

    def _check_path(self, path):
        path = Path(path).absolute()
        try:
            relative = path.relative_to(self.root)
        except ValueError as error:
            raise ValueError('Handoff must be inside .forgeflow/handoffs') from error
        if len(relative.parts) != 2 or '..' in relative.parts:
            raise ValueError('Invalid Handoff path')
        if any(p.is_symlink() for p in (self.root.parent, self.root, path.parent, path)):
            raise ValueError('Handoff paths must not be symbolic links')
        return path

    def paths(self):
        if self.root.is_symlink() or self.root.parent.is_symlink():
            raise ValueError('Handoff root must not be a symbolic link')
        if self.root.exists() and not self.root.is_dir():
            raise ValueError('Handoff root must be a directory')
        return set(self.root.glob('*/*.md'))

    def read(self, path):
        path = self._check_path(path)
        text = path.read_text(encoding='utf-8')
        pattern = (r'\A# ForgeFlow Handoff\n\n## Metadata\n\n'
                   r'\| Field \| Value \|\n\| --- \| --- \|\n'
                   r'\| Schema Version \| 1\.0 \|\n'
                   r'\| Handoff ID \| ([0-9a-f-]+) \|\n'
                   r'\| Producer \| (Workflow|Routing Correction) \|\n'
                   r'\| Source Workflow \| (Plan|Grill|Solution|Slice|Implement|Review|NONE) \|\n\n')
        match = re.match(pattern, text)
        if not match:
            raise ValueError('Invalid Handoff file metadata')
        identifier, producer, workflow = match.groups()
        if str(UUID(identifier)) != identifier or path.name != identifier + '.md':
            raise ValueError('Handoff ID does not match filename')
        source = workflow.lower() if workflow != 'NONE' else None
        if (producer == 'Workflow') != (source is not None):
            raise ValueError('Handoff producer does not match source workflow')
        block = text[match.end():]
        if not block.startswith('### Handoff\n'):
            raise ValueError('Missing canonical Handoff block')
        handoff = HandoffParser.parse(block, expected_source_workflow=source,
                                     expected_source_scope='Project' if source is None else None)
        if handoff is None or path.parent.name != self.directory(handoff['source_scope']):
            raise ValueError('Invalid Handoff block or source directory')
        return {'path': str(path), 'producer': producer, 'source_workflow': source,
                'handoff': handoff}

    def publish(self, block, source_workflow=None):
        handoff = HandoffParser.parse(block, expected_source_workflow=source_workflow,
                                     expected_source_scope='Project' if source_workflow is None else None)
        if handoff is None:
            raise ValueError('Cannot publish an invalid Handoff')
        identifier = str(uuid4())
        target = self._check_path(self.root / self.directory(handoff['source_scope']) / f'{identifier}.md')
        producer = 'Workflow' if source_workflow else 'Routing Correction'
        workflow = source_workflow.capitalize() if source_workflow else 'NONE'
        canonical = block[block.index('### Handoff'):].strip()
        text = ('# ForgeFlow Handoff\n\n## Metadata\n\n| Field | Value |\n| --- | --- |\n'
                f'| Schema Version | 1.0 |\n| Handoff ID | {identifier} |\n'
                f'| Producer | {producer} |\n| Source Workflow | {workflow} |\n\n{canonical}\n')
        target.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', dir=target.parent,
                                         prefix='.', suffix='.tmp', delete=False) as stream:
            temporary = Path(stream.name)
            try:
                stream.write(text)
                stream.flush()
                os.fsync(stream.fileno())
                os.link(temporary, target)  # Atomic publication, never replace an existing record.
            finally:
                temporary.unlink()
        return target

    def inspect(self, validate):
        records = []
        for path in sorted(self.paths()):
            try:
                record = self.read(path)
            except (ValueError, UnicodeError, OSError) as error:
                records.append({'path': str(path), 'errors': [str(error)]})
            else:
                record['errors'] = validate(record)
                records.append(record)
        return records

    def select(self, validate):
        valid = [r for r in self.inspect(validate) if not r['errors']]
        if not valid:
            return None
        first = valid[0]
        if any((r['producer'], r['source_workflow'], r['handoff']) !=
               (first['producer'], first['source_workflow'], first['handoff']) for r in valid[1:]):
            raise ValueError('ambiguous Handoff candidates; specify a file explicitly')
        return first
