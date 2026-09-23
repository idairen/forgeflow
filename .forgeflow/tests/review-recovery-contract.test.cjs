// Static Markdown contracts, not an executable recovery engine or IDE acceptance test.
const {test} = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const read = p => fs.readFileSync(path.join(__dirname, '..', p), 'utf8').replace(/\s+/g, ' ');
const review = read('workflow/review.md');
const recovery = read('protocol/review-recovery.md');
const artifact = read('protocol/artifact.md');
const transition = read('protocol/transition.md');
const implement = read('workflow/implement.md');

test('Review validates candidate shape and direct references before immutable publication', () => {
  const gate = review.indexOf('Validate the complete candidate Review locally');
  assert.ok(gate >= 0 && gate < review.indexOf('Persist one immutable'));
  for (const requirement of ['exactly one Metadata', 'common and Review-specific fields',
    'filename/identity matches', 'exactly one Findings table', 'counts, Decision and Return',
    'frozen Feature Engineering Version', 'frozen Slice Plan']) assert.ok(review.includes(requirement));
  assert.match(review, /not another full-graph scan or test\/plugin run/);
  assert.match(review, /do not change findings, evidence or Decision merely to pass a format check/);
});

test('recovery is optional maintenance, not ordinary Review or a seventh Workflow', () => {
  assert.match(read('forgeflow.md'), /Normal Workflows do not load this optional procedure/);
  assert.match(recovery, /Framework maintenance authorization does not authorize disposition of project Artifacts/);
  assert.match(recovery, /prepare the concrete disposition before requesting authorization/);
  assert.match(review, /only Handoff Entry—never Recovery/);
  assert.match(transition, /Ordinary Entry and read-only correction never move the report/);
});

test('eligible formatting recovery cannot erase a valid or blocking Review', () => {
  assert.match(recovery, /Merely stale evidence is not eligible/);
  assert.match(recovery, /ambiguous or contradictory identity is not repaired/);
  assert.match(recovery, /no declared FAIL, positive Blocking Findings count, BLOCKING finding/);
  assert.match(recovery, /A conforming PASS or FAIL is never eligible/);
  assert.match(recovery, /Other invalid Artifact types and broken references are outside/);
});

test('original and receipt preserve identity and consumed Attempt without PASS credit', () => {
  for (const field of ['Source Filename', 'SHA256', 'Feature ID', 'Slice ID', 'Attempt',
    'Implement Version', 'Authorization', 'Reason']) assert.ok(artifact.includes(field));
  assert.match(artifact, /history\/invalid-review\/<original-review-filename>/);
  assert.match(artifact, /pair permanently occupies its Attempt/);
  assert.match(artifact, /Never infer PASS, FAIL, readiness or completion from it/);
  assert.match(artifact, /matching invalid Review history pairs/);
  assert.match(artifact, /NewAttempt = max\(UsedAttempts, default=0\) \+ 1/);
});

test('current READY_FOR_REVIEW with disposed Review reroutes to new Attempt', () => {
  assert.match(transition, /Attempt ineligible for Review or completion, even if READY_FOR_REVIEW/);
  assert.match(transition, /Rule 10 may select it for a new Implement Attempt after the ordinary earlier barriers/);
  assert.match(implement, /except when its Attempt is occupied by a valid invalid-Review history pair/);
  assert.match(artifact, /Current Attempt occupied by a valid invalid-Review history pair/);
  assert.match(recovery, /Only a later valid Implement Entry allocates above all used Attempts/);
});

test('conflicts and partial disposition fail closed with bounded evidence checks', () => {
  assert.match(transition, /check only its exact Attempt's invalid Review history pair/);
  assert.match(transition, /Invalid pairs or a canonical Review coexisting with its pair trigger Rule 2/);
  assert.match(artifact, /A missing half, malformed receipt, digest mismatch/);
  assert.match(recovery, /sequential unprotected writes are insufficient/);
  assert.match(recovery, /If rollback is impossible, report retained paths and HALT/);
  assert.match(recovery, /same explicit disposition authorization, frozen digest, and Implement identity/);
  assert.match(recovery, /idempotent no-op after validation/);
});

test('recovery routes remaining errors and never executes or decides the new Review', () => {
  assert.match(recovery, /ordinary Rule precedence and projection/);
  assert.match(recovery, /A remaining contradiction emits HALTED/);
  assert.match(recovery, /Do not start the selected Workflow/);
  assert.match(recovery, /Review subsequently evaluates that new Attempt independently/);
  assert.match(recovery, /Do not edit Implement, upstream plans, source, tests or plugin reports/);
});
