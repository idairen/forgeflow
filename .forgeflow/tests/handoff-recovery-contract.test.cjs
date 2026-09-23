// Static contract regressions only; these do not execute an IDE or an Artifact resolver.
// Run: node --test tests/*.test.cjs
const {test} = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const root = path.resolve(__dirname, '..');
const read = name => fs.readFileSync(path.join(root, name), 'utf8');
const transition = read('protocol/transition.md');
const handoff = read('protocol/handoff.md');
const framework = read('forgeflow.md');
const section = (text, start, end) => {
  const a = text.indexOf(start);
  const b = text.indexOf(end, a + start.length);
  assert.ok(a >= 0 && b > a, `Missing contract section: ${start}`);
  return text.slice(a, b).replace(/\s+/g, ' ');
};
const correction = section(transition, '### Read-only routing correction',
  '### Subsequent Plan and Lane validation');

test('missing or rejected Handoff has a correction path, not a sixth productive Entry', () => {
  const entry = section(transition, '## Entry authorization', '### Read-only routing correction');
  const names = [...entry.matchAll(/\| (Bootstrap|Subsequent Plan|Handoff|Lane|Recovery) \|/g)]
    .map(match => match[1]);
  assert.deepEqual(names, ['Bootstrap', 'Subsequent Plan', 'Handoff', 'Lane', 'Recovery']);
  assert.match(correction, /Handoff is missing or fails receiving validation and no other valid Entry applies/);
  assert.match(correction, /not a sixth Entry, a new Workflow, or authority to repair Artifacts/);
  assert.match(correction, /before application inspection, tests, plugins, or any mutation/);
  assert.match(framework, /Valid Entries proceed normally without\s+an additional correction step/);
});

test('correction cannot execute a matching target or fabricate projection evidence', () => {
  assert.match(correction, /existing variant and ordered projection with Source Scope `Project`, then stop/);
  assert.match(correction, /selected target equals the requested Workflow\/Scope: execution requires a later invocation/);
  assert.match(correction, /never consumes its own output, allocates an Attempt, or performs target-scope work/);
  assert.match(handoff, /rather than\s+requiring the user to restart the prior emitter/);
  assert.match(handoff, /MUST NOT infer its\s+missing fields, normalize malformed content, or replace version values/);
  assert.doesNotMatch(handoff, /An invalid Handoff is returned to its source for exact correction/);
});

test('invalid graphs halt before stale-evidence routing; correction preserves waits', () => {
  assert.ok(transition.indexOf('### Rule 2') < transition.indexOf('### Rule 10'));
  assert.match(correction, /Rule 2 emits HALTED rather than a guessed forward target/);
  assert.match(correction, /Rule 1 no-Handoff result or Rule 5 join-pending result/);
  assert.match(correction, /without a synthetic Handoff or a Lane claim/);
  assert.match(correction, /Preserve valid Bootstrap, Subsequent Plan, Lane, Recovery, and same-authorization waiting/);
  assert.match(correction, /global blocker selection without an executing Lane/);
  assert.match(handoff, /has no emitting Workflow/);
});

test('upstream revisions invalidate cached completion, not immutable evidence', () => {
  const routing = section(transition, '## Transition Resolution Procedure', '### Rule 1');
  assert.match(routing, /saved versions and recompute downstream currentness and the completion prefix/);
  assert.match(routing, /Do not reuse the pre-revision completion decision or default to the Slice/);
  assert.match(routing, /Retain old Implement\/Review evidence unchanged/);
  assert.match(routing, /existing Rule 1–11 precedence still applies/);
  const prefix = section(transition, '- **Completion prefix**', '- **Artifact currentness chain**');
  assert.match(prefix, /current Implement Record followed by its matching current PASS/);
  assert.match(prefix, /Rules 9 and 10 can select that target only when this prefix is complete/);
});

test('Solution and Slice use saved baselines without changing version granularity', () => {
  const solution = read('workflow/solution.md').replace(/\s+/g, ' ');
  const slice = read('workflow/slice.md').replace(/\s+/g, ' ');
  assert.match(solution, /saved Feature Engineering Versions under its upstream-persistence rule/);
  assert.match(solution, /retain compatible Feature Engineering Versions/);
  assert.match(slice, /saved Slice Plan version under its upstream-persistence rule/);
  assert.match(slice, /Do not return directly to the requesting Slice or retain an old completion prefix/);
  assert.match(slice, /Evidence tied to the older version remains immutable history but is stale/);
});

test('correction reuses fresh invocation checks without trusting earlier invocations', () => {
  assert.match(correction, /Reuse this invocation's fresh graph validation and resolution when the graph has not changed/);
  assert.match(correction, /no unconditional second full-graph scan/);
  assert.match(correction, /unverified result from a previous invocation/);
  assert.match(correction, /graph changes are observed before rendering, revalidate and resolve the new graph/);
});

test('existing launchers inherit correction without extra commands or Workflow reads', () => {
  const workflows = ['plan', 'grill', 'solution', 'slice', 'implement', 'review'];
  for (const platform of ['codex', 'copilot']) {
    const dir = `adapter/${platform}`;
    assert.deepEqual(fs.readdirSync(path.join(root, dir)).sort(),
      workflows.map(name => `forge-${name}.prompt.md`).sort());
    for (const name of workflows) {
      const refs = [...read(`${dir}/forge-${name}.prompt.md`)
        .matchAll(/^\d\. `\.forgeflow\/([^`]+)`$/gm)].map(match => match[1]);
      assert.deepEqual(refs, ['forgeflow.md', 'protocol/artifact.md',
        'protocol/transition.md', 'protocol/handoff.md', `workflow/${name}.md`]);
    }
  }
});
