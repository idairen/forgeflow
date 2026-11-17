// Markdown policy regressions; live IDE compliance needs separate acceptance.
const {test} = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const read = name => fs.readFileSync(path.join(__dirname, '..', name), 'utf8').replace(/\s+/g, ' ');

test('engineering owners accept fresh forward and Review return separately from gap recovery', () => {
  for (const [name, rule, gap] of [
    ['solution', 6, 'ENGINEERING_GAP'], ['slice', 7, 'SLICE_VIOLATION'],
    ['implement', 10, 'IMPLEMENTATION_GAP']
  ]) {
    const contract = read(`workflow/${name}.md`).split('## ')[1];
    assert.ok(contract.includes(`Rule ${rule} FORWARD`), name);
    assert.ok(contract.includes('Rule 8 RETURN for `REVIEW_BLOCKER`'), name);
    assert.ok(contract.includes(`Rule 3 RETURN for \`${gap}\``), name);
    assert.match(contract, /no-Handoff Recovery only/);
    assert.doesNotMatch(contract, /Handoff or Recovery selected from current/);
  }
});

test('current FAIL authorizes a new attempt directly without erasing its decision', () => {
  const implement = read('workflow/implement.md');
  assert.match(implement, /Rule 8 Handoff authorizes a new Implement execution directly/);
  assert.match(implement, /do not wait for Rule 10/);
  assert.match(implement, /READY_FOR_REVIEW without Review awaits Review/);
  assert.match(implement, /matching current FAIL returned by Rule 8.*permits a new Attempt/);
  assert.match(implement, /retain the immutable FAIL/);
  assert.match(read('protocol/transition.md'), /while Rule 8 still selects it/);
});

test('Implement validates initial and final candidates before canonical publication', () => {
  const implement = read('workflow/implement.md');
  assert.match(implement, /Before every canonical write, including entry allocation/);
  for (const clause of ['first line is its level-one title', 'exactly one Metadata',
    'exactly one Strategy', 'one Source and Result', 'No prose or Changed Files',
    'A total test count, successful suite, or generic coverage claim cannot establish']) {
    assert.ok(implement.includes(clause), clause);
  }
  assert.match(read('protocol/artifact.md'), /independent of this specification's `Version` header/);
});

test('format repair preserves originals outside counter history and cannot erase FAIL', () => {
  const recovery = read('protocol/implement-recovery.md');
  const artifact = read('protocol/artifact.md');
  assert.match(read('forgeflow.md'), /explicit request to repair an invalid Implement Record's format/);
  assert.match(recovery, /reuse|Reuse explicit user authorization/);
  assert.match(recovery, /matching PASS is not eligible/);
  assert.match(recovery, /With a current FAIL, preserve Status/);
  assert.match(recovery, /never resolves its findings/);
  assert.match(recovery, /procedure grants no PASS or completion and allocates no Attempt/);
  assert.match(recovery, /idempotent no-op/);
  assert.match(recovery, /before atomically installing the validated candidate/);
  assert.match(artifact, /history\/invalid-implement\/<SHA256>\/<canonical-implement-filename>/);
  assert.match(artifact, /not an Artifact, Attempt archive, counter source, or readiness evidence/);
  assert.match(artifact, /later authorized reimplementation archives the repaired record/);
  assert.match(artifact, /No revision-suffixed standard Attempt archives are introduced/);
});
