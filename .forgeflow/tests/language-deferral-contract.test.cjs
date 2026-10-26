// Static policy checks; these do not establish live IDE/agent compliance.
const {test} = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const read = name => fs.readFileSync(path.join(__dirname, '..', name), 'utf8').replace(/\s+/g, ' ');

test('language survives later workflows and legacy Planning without translating protocol syntax', () => {
  const framework = read('forgeflow.md');
  assert.match(framework, /Chinese intent selects Chinese; English intent selects English/);
  assert.match(framework, /All Workflows MUST read that choice from current Planning/);
  assert.match(framework, /short reply in another language does not reset it/);
  assert.match(framework, /Keep canonical headings, field\/table labels/);
  assert.match(framework, /older Planning without a stored choice, use its substantive Project Intent language/);
  assert.match(read('workflow/plan.md'), /before asking clarifications/);
  assert.match(read('protocol/artifact.md'), /inside `## Project Intent`/);
});

test('verification failure offers a decision and preserves scoped approval across sessions', () => {
  const implement = read('workflow/implement.md');
  assert.match(implement, /MUST present the user with a choice in Planning's communication language/);
  for (const choice of ['Repair the problem', 'Temporarily defer the named checks', 'Pause and retain the blocker']) {
    assert.ok(implement.includes(choice));
  }
  assert.match(implement, /Expected TDD RED.*is not a failure requiring this choice/);
  assert.match(implement, /Wait for an explicit answer before deferring checks/);
  assert.match(implement, /do not ask again merely because a new session starts/);
});

test('deferral preserves evidence and routes future work through versioned owner contracts', () => {
  const artifact = read('protocol/artifact.md');
  assert.match(artifact, /Preserve FAILED, NOT_RUN, or INCONCLUSIVE/);
  assert.match(artifact, /leaving the record IN_PROGRESS/);
  assert.match(artifact, /ENGINEERING_GAP to Solution.*SLICE_VIOLATION to Slice/);
  assert.match(artifact, /temporary deferral cannot remove an obligation or move it beyond project completion/);
  assert.match(artifact, /normal versioning, archival, invalidation, and fresh Transition resolution/);
  assert.match(read('workflow/solution.md'), /Preserve the deferral decision and risks in the revised plan/);
  assert.match(read('workflow/slice.md'), /concrete successor Slice's Verification Plan/);
  assert.match(read('workflow/review.md'), /Open Issues entry alone cannot waive a required current check/);
  assert.match(read('workflow/review.md'), /Outstanding checks at a successor gate still block/);
});
