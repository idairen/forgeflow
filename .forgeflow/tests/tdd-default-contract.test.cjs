// Static policy regressions; these do not prove a host follows the instructions.
const {test} = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const read = name => fs.readFileSync(path.join(__dirname, '..', name), 'utf8').replace(/\s+/g, ' ');
const artifact = read('protocol/artifact.md');

test('behavioral work defaults to TDD, including fixes and mixed Slices', () => {
  for (const name of ['forgeflow.md', 'protocol/artifact.md']) {
    assert.match(read(name), /TDD is required by default for new or changed executable behavior, including bug fixes/);
  }
  assert.match(artifact, /Mixed Slices retain TDD for their behavioral portion/);
  assert.match(artifact, /migrations that implement new data behavior are not automatically exempt/);
  assert.match(read('workflow/slice.md'), /Include TDD for each new or changed executable behavior/);
});

test('non-behavioral work needs a rationale without a fabricated failing test', () => {
  assert.match(artifact, /record why TDD is not applicable and which checks verify the work/);
  assert.match(artifact, /No special user approval is required for that factual classification/);
  assert.match(artifact, /Behavior-preserving refactoring needs preservation\/regression evidence, not an invented failure/);
});

test('behavioral exceptions are approved in Solution and traced through Slice and Review', () => {
  assert.match(artifact, /obtain explicit user approval before making a non-TDD exception READY/);
  assert.match(artifact, /equivalent behavioral coverage, passing criteria and evidence sources/);
  assert.match(artifact, /Record the answer and its scope with the obligation in Verification Requirements/);
  assert.match(read('workflow/slice.md'), /Slice never grants its own waiver/);
  assert.match(read('workflow/implement.md'), /explicitly user-approved Solution exception/);
  assert.match(read('workflow/review.md'), /exception traced through Slice and Implement/);
});

test('missing RED and older plans cannot silently authorize a weaker strategy', () => {
  assert.match(artifact, /implementation is already written does not itself approve an exception/);
  assert.match(artifact, /Never fabricate or backdate RED/);
  assert.match(artifact, /Existing Artifacts remain readable and history is not rewritten/);
  assert.match(artifact, /missing policy returns to Solution/);
  assert.match(read('workflow/implement.md'), /returns SLICE_VIOLATION before implementation/);
});

test('supplementary strategies justify additional evidence instead of a fixed bundle', () => {
  assert.match(read('forgeflow.md'), /No default bundle or all-strategy checklist is required/);
  assert.match(artifact, /For each supplementary strategy, state its governing obligation, evidence and why the existing checks are insufficient/);
  assert.match(read('workflow/solution.md'), /Explain the additional evidence supplied by each other strategy/);
  assert.match(read('workflow/review.md'), /not by their count/);
});
