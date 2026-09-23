// Static Markdown contract regressions, not an Artifact Graph runtime validator.
// Run from any directory: node --test tests/implement-contract.test.cjs
const {test} = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const root = path.resolve(__dirname, '..');
const read = p => fs.readFileSync(path.join(root, p), 'utf8');
const exists = p => fs.existsSync(path.join(root, p));
const framework = read('forgeflow.md');
const artifact = read('protocol/artifact.md');
const transition = read('protocol/transition.md');
const handoff = read('protocol/handoff.md');
const implement = read('workflow/implement.md');
const review = read('workflow/review.md');
const section = (s, a, b) => {
  const start = s.indexOf(a);
  assert.ok(start >= 0, `Missing section: ${a}`);
  const end = b ? s.indexOf(b, start + a.length) : s.length;
  assert.ok(end > start, `Missing end: ${b}`);
  return s.slice(start, end);
};
const rows = s => s.split('\n').filter(l => l.startsWith('| '))
  .map(l => l.slice(1, -1).split('|').map(v => v.trim()));
const workflows = ['Plan', 'Grill', 'Solution', 'Slice', 'Implement', 'Review'];
const strategyIds = ['TDD', 'BEHAVIORAL_TEST', 'CHARACTERIZATION_TEST', 'MIGRATION_REHEARSAL',
  'STATIC_VALIDATION', 'CONFIGURATION_VALIDATION', 'SECURITY_SCAN', 'BENCHMARK',
  'DOCUMENTATION_VALIDATION', 'MANUAL_ACCEPTANCE'];

test('static: exactly six canonical workflows and one implementation definition', () => {
  const manifest = rows(section(framework, '| Workflow | Artifact |', '## Normative model')).slice(2);
  assert.deepEqual(manifest.map(r => r[0]), workflows);
  assert.equal(manifest[4][1], 'Implement Record');
  assert.equal(manifest[4][2], 'Slice');
  assert.equal(manifest[4][3], '`workflow/implement.md`');
  assert.equal(exists('workflow/tdd.md'), false);
  assert.deepEqual(fs.readdirSync(path.join(root,'workflow')).sort(), workflows.map(w=>w.toLowerCase()+'.md').sort());
});

test('static: indexed protocol versions equal actual headers', () => {
  const table = rows(section(framework, '| Contract | Version |', '| Workflow | Artifact |')).slice(2);
  assert.equal(table.length, 4);
  for (const [,version,p] of table) assert.equal(read(p.replaceAll('`','')).match(/^Version: (.+)$/m)[1], version);
});

test('static: all twelve adapters resolve the new workflow chain', () => {
  for (const platform of ['codex','copilot']) {
    const dir = `adapter/${platform}`;
    assert.equal(exists(`${dir}/forge-tdd.prompt.md`), false);
    assert.equal(fs.readdirSync(path.join(root,dir)).length, 6);
    for (const workflow of workflows) {
      const name=workflow.toLowerCase();
      const s=read(`${dir}/forge-${name}.prompt.md`);
      assert.equal(s.match(/^name: (.+)$/m)[1],`forge-${name}`);
      const refs=[...s.matchAll(/^\d\. `\.forgeflow\/([^`]+)`$/gm)].map(m=>m[1]);
      assert.deepEqual(refs,['forgeflow.md','protocol/artifact.md','protocol/transition.md','protocol/handoff.md',`workflow/${name}.md`]);
      refs.forEach(p=>assert.ok(exists(p),p));
    }
  }
});

test('static: Slice to Implement resolves through Rule 10 and the delivery barrier', () => {
  const r7=section(transition,'### Rule 7','### Rule 8');
  const r10=section(transition,'### Rule 10','### Rule 11');
  assert.match(r7,/Verification Plan requirement/);
  assert.match(r7,/Implement\s+remains forbidden until every Feature has a usable Slice Plan/);
  assert.match(r10,/all delivery barriers hold, FORWARD to Implement/);
  assert.match(r10,/Slice: F-<FeatureNumber>\/S-<SliceNumber>/);
});

test('static: Implement to Review requires current READY_FOR_REVIEW and no matching Review', () => {
  const r9=section(transition,'### Rule 9','### Rule 10');
  assert.match(r9,/to Review when its current Implement Record is READY_FOR_REVIEW/);
  assert.match(r9,/no\s+valid Review exists/);
  assert.match(implement,/upstream RETURN,\s+blocker waiting, and graph HALTED/);
});

test('static: workflow/type/path schema rejects TDD as a current implementation owner', () => {
  const owners=rows(section(artifact,'### Ownership and Canonical Artifact Paths','### Type-specific metadata')).slice(2);
  assert.deepEqual([...new Set(owners.map(r=>r[1]))],workflows);
  assert.equal(owners.some(r=>r[0]==='TDD Record'||r[1]==='TDD'),false);
  const row=owners.find(r=>r[0]==='Implement Record');
  assert.equal(row[3],'`implement-feature-<FeatureNumber>-slice-<SliceNumber>.md`');
  assert.match(artifact,/Newly written Artifacts cannot use TDD as Owner Workflow/);
  assert.match(handoff,/TDD is a verification strategy, not a valid Next Workflow/);
});

test('static: TDD and nine non-TDD strategies are supported, without extra workflows', () => {
  const registry=rows(section(artifact,'| Strategy | Required execution pattern and evidence |','TDD is the default candidate')).slice(2);
  assert.deepEqual(registry.map(r=>r[0]),strategyIds);
  assert.equal(workflows.includes('TDD'),false);
  assert.match(registry[0][1],/RED.*GREEN.*refactor/);
  assert.match(implement,/Other strategies follow\s+their own declared pattern and never manufacture a RED phase/);
});

test('static: plural selection, rationale and governing obligations are required', () => {
  const meta=rows(section(artifact,'### Type-specific metadata','### Feature-scoped versions')).find(r=>r[0]==='Implement Record');
  assert.match(meta[1],/Verification Strategies/);
  const selection=section(artifact,'Each Implement Record contains `## Verification Selection`','Each record also contains `## Verification Evidence`');
  assert.match(selection,/\| Strategy \| Rationale \| Governing Obligation \|/);
  assert.match(selection,/ordered unique union/);
  assert.match(selection,/Every rationale is non-empty/);
  assert.match(selection,/NONE is forbidden for\s+IN_PROGRESS and READY_FOR_REVIEW/);
});

test('static: strategy choice cannot waive mandatory checks or lower criteria', () => {
  assert.match(framework,/Solution owns verification obligations/);
  assert.match(framework,/Slice maps them/);
  assert.match(artifact,/It cannot drop a\s+mandatory check/);
  assert.match(artifact,/lower a threshold/);
  assert.match(artifact,/Multiple rows\/strategies are cumulative/);
  assert.match(read('workflow/slice.md'),/permitted alternatives/);
});

test('static: source-specific evidence is distinct from model assertion and Review Decision', () => {
  assert.match(artifact,/Source is TOOL_EXECUTION,\s+HUMAN_ACCEPTANCE, or MODEL_ASSESSMENT/);
  assert.match(artifact,/exit status/);
  assert.match(artifact,/historical RED, benchmark measurements, or a person's approval/);
  assert.match(artifact,/Result is SUCCEEDED, FAILED, NOT_RUN,\s+INCONCLUSIVE, or NOT_APPLICABLE/);
  assert.match(review,/model\s+assessment cannot substitute for required execution/);
});

test('static: Implement has only progress/blocker/review-ready statuses, never final PASS', () => {
  const statuses=rows(section(artifact,'### Status and blockers','Review Decision is')).find(r=>r[0]==='Implement Record');
  assert.equal(statuses[1],'IN_PROGRESS, BLOCKED, READY_FOR_REVIEW');
  assert.match(artifact,/There is no overall Review Decision or separate Result state in an Implement Record/);
  assert.match(implement,/issues Review PASS\/FAIL/);
  assert.match(review,/PASS has zero blocking rows/);
  assert.match(transition,/every Slice has a current READY_FOR_REVIEW\s+record and matching current PASS/);
});

test('static: missing required evidence and unresolved selection cannot reach Review', () => {
  assert.match(implement,/Required NOT_RUN or INCONCLUSIVE results prevent READY_FOR_REVIEW/);
  assert.match(implement,/For an unresolved selection, persist BLOCKED instead/);
  assert.match(artifact,/NOT_APPLICABLE needs an\s+explicit applicability condition/);
  assert.match(artifact,/cannot waive a required\s+obligation/);
});

test('static: frozen Attempt and bounded legacy counters survive the migration', () => {
  assert.match(artifact,/NewAttempt = max\(UsedAttempts, default=0\) \+ 1/);
  assert.match(artifact,/same authorized execution/);
  assert.match(artifact,/Multiple strategy runs remain in the same frozen Attempt/);
  assert.match(artifact,/history\/legacy-tdd\//);
  assert.match(artifact,/preserve the maximum\s+used counter but never establish current readiness/);
  assert.match(implement,/Never allocate another Attempt at this step/);
});

test('static: legacy active paths halt and are not silent aliases', () => {
  assert.match(artifact,/Rule 2 halts rather than ignoring it or allowing two implementation records/);
  assert.match(artifact,/framework migration alone does not authorize rewriting generated artifacts/);
  assert.match(artifact,/Unresolved legacy blockers must be handled explicitly/);
  assert.match(transition,/never becomes an active node or a non-terminal Input Artifact/);
  assert.match(handoff,/Reject an old TDD\s+Handoff rather than silently normalizing/);
});

test('static: four canonical Handoff template shapes stay unchanged', () => {
  const templates=section(handoff,'## FORWARD template','## Receiving validation');
  const blocks=[...templates.matchAll(/```markdown\n([\s\S]*?)\n```/g)].map(m=>rows(m[1]).slice(2).map(r=>r[0]));
  assert.deepEqual(blocks,[
    ['Transition','Next Workflow','Source Scope','Target Scope','Input Artifacts','Reason'],
    ['Transition','Next Workflow','Source Scope','Target Scope','Blocker Category','Input Artifacts','Reason'],
    ['Transition','Terminal Status','Source Scope','Completed Scope','Input Artifacts','Reason'],
    ['Transition','Terminal Status','Source Scope','Affected Scope','Blocker Category','Input Artifacts','Reason']
  ]);
  assert.match(artifact,/Handoff is rendered in the response/);
});

test('static: existing Lane recovery and Solution staleness safeguards remain', () => {
  assert.match(artifact,/#### Solution baseline validity and currentness/);
  assert.match(transition,/### Interrupted Lane Recovery/);
  assert.match(transition,/Every Plan Entry checks for ACTIVE Lanes again before persistence/);
  assert.match(artifact,/When retiring every\s+Feature, require Empty Feature Approval/);
});

test('static: no strategy grants unplanned configuration, migration or documentation edits', () => {
  assert.match(artifact,/only\s+when authorized by Solution\/Slice placement/);
  assert.match(read('workflow/slice.md'),/a strategy grants no additional path scope/);
  assert.match(implement,/one authorized Slice|only the authorized changes/);
});

test('static: behavioral testing is executable evidence, not fabricated TDD or human approval', () => {
  const strategies = rows(section(artifact,
    '| Strategy | Required execution pattern and evidence |', 'TDD is the default candidate')).slice(2);
  const behavioral = strategies.find(row => row[0] === 'BEHAVIORAL_TEST')[1];
  assert.match(behavioral, /Execute tests against approved observable behavior/);
  assert.match(behavioral, /expected and actual results/);
  assert.match(behavioral, /Historical RED is not required and must not be claimed/);
  assert.match(behavioral, /cannot replace mandatory TDD or required human acceptance/);
});

test('static: selection guidance cannot unlock a mandatory Slice strategy or bypass missing policy', () => {
  const selection = section(implement, '## Strategy selection', '## Implementation methods')
    .replace(/\s+/g, ' ');
  assert.match(selection, /Retain every mandatory strategy and check/);
  assert.match(selection, /only when its stated condition holds/);
  assert.match(selection, /never grants an alternative absent from the approved plan/);
  assert.match(selection, /Unresolved selection follows the existing BLOCKED allocation and RETURN rules without code changes/);
  assert.match(selection, /unavailable environment, or missed pre-change baseline is not permission to switch/);
  // The existing Slice schema still requires supported strategies, not a method or AUTO placeholder.
  const sliceContract = section(artifact, '### Slice Plan', '### Verification strategies and evidence');
  assert.match(sliceContract, /Every listed strategy is required unless/);
  assert.match(sliceContract, /Strategies use one or more\s+supported identifiers/);
});

test('static: every registered strategy has selection guidance without becoming another workflow', () => {
  const selection = section(implement, '| Change or obligation |', '## Implementation methods');
  for (const id of strategyIds) assert.ok(selection.includes(id), `Missing candidate guidance: ${id}`);
  const manifest = rows(section(framework, '| Workflow | Artifact |', '## Normative model')).slice(2);
  assert.deepEqual(manifest.map(row => row[0]), workflows);
});

test('static: optional methods preserve existing record shape, evidence gate and frozen Attempt', () => {
  const policy = section(artifact, 'An implementation method describes', 'Each Implement Record contains')
    .replace(/\s+/g, ' ');
  assert.match(policy, /optional free-form prose in Implementation Summary/);
  assert.match(policy, /not Verification Strategies/);
  assert.match(policy, /Existing records without method prose remain valid/);
  assert.match(policy, /A method supplies no verification evidence by itself/);
  const methods = section(implement, '## Implementation methods', '## Review-ready gate')
    .replace(/\s+/g, ' ');
  assert.match(methods, /change within the frozen Attempt/);
  assert.match(methods, /A method change creates no new Attempt or approval gate/);
  assert.match(methods, /outside the approved contracts require RETURN to their owner/);
  const fields = rows(section(artifact, '### Type-specific metadata', '### Feature-scoped versions'));
  assert.equal(fields.some(row => /Method/.test(row.join(' '))), false);
});
