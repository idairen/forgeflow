#!/usr/bin/env python3
"""Build the bilingual ForgeFlow executive brief with headless Chrome."""

from __future__ import annotations

import argparse
import html
from pathlib import Path
import shutil
import subprocess
import time


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "docs" / "presentations"
SCRATCH = ROOT / "tmp" / "pdfs"
CHROME_CANDIDATES = (
    Path("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"),
    Path("/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge"),
    Path("/Applications/Chromium.app/Contents/MacOS/Chromium"),
)


CSS = r"""
@page { size: A4 landscape; margin: 0; }
* { box-sizing: border-box; }
html, body { margin: 0; padding: 0; background: #edf3fb; color: #132238; }
body { font-family: Inter, "Helvetica Neue", Arial, "PingFang SC", "Microsoft YaHei", sans-serif; }
.page {
  width: 297mm; height: 210mm; overflow: hidden; position: relative;
  page-break-after: always; padding: 17mm 18mm 15mm;
  background:
    radial-gradient(circle at 90% 6%, rgba(37, 99, 235, .12), transparent 30%),
    linear-gradient(145deg, #ffffff 0%, #f6f9fd 58%, #eef4fb 100%);
}
.page:last-child { page-break-after: auto; }
.page::after {
  content: ""; position: absolute; inset: 0; pointer-events: none;
  background-image: linear-gradient(rgba(31,72,125,.025) 1px, transparent 1px),
                    linear-gradient(90deg, rgba(31,72,125,.025) 1px, transparent 1px);
  background-size: 18px 18px;
}
.content { position: relative; z-index: 1; height: 100%; }
.topline { display: flex; align-items: center; justify-content: space-between; margin-bottom: 7mm; }
.brand { font-size: 10px; letter-spacing: 2.4px; text-transform: uppercase; color: #245fba; font-weight: 700; }
.section-no { font-size: 10px; color: #627897; letter-spacing: 1.2px; }
h1 { margin: 0; font-size: 34px; line-height: 1.08; letter-spacing: -1px; }
h2 { margin: 0 0 3mm; font-size: 24px; line-height: 1.14; letter-spacing: -.4px; }
h3 { margin: 0 0 2mm; font-size: 14px; color: #152b48; }
p { margin: 0; font-size: 12.2px; line-height: 1.55; color: #50647f; }
.lead { font-size: 16px; line-height: 1.5; color: #304866; max-width: 238mm; }
.accent { color: #155fc3; }
.green { color: #087d68; }
.muted { color: #6c7f99; }
.small { font-size: 9.5px; line-height: 1.45; }
.grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 6mm; }
.grid-3 { display: grid; grid-template-columns: repeat(3, 1fr); gap: 4.5mm; }
.grid-4 { display: grid; grid-template-columns: repeat(4, 1fr); gap: 4mm; }
.card {
  border: 1px solid #d5e1ef; border-radius: 14px;
  padding: 5mm; background: linear-gradient(160deg, #ffffff, #f5f8fc);
  box-shadow: 0 10px 30px rgba(40,73,113,.08);
}
.card.blue { border-color: #8eb9ee; }
.card.green-card { border-color: #8ccfc2; }
.card .kicker { font-size: 9px; color: #2869be; letter-spacing: 1.2px; text-transform: uppercase; margin-bottom: 2mm; }
.metric { font-size: 31px; line-height: 1; font-weight: 750; color: #1a4f91; margin-bottom: 2mm; }
.quote { border-left: 3px solid #2178d4; padding-left: 5mm; font-size: 19px; line-height: 1.45; color: #1b3557; }
.footer { position: absolute; z-index: 2; left: 18mm; right: 18mm; bottom: 7mm; display: flex; justify-content: space-between; font-size: 8.5px; color: #71839a; }
.pill { display: inline-block; border: 1px solid #83afe3; border-radius: 999px; padding: 1.5mm 3mm; color: #225eaa; background: rgba(255,255,255,.7); font-size: 9px; margin: 0 1.5mm 1.5mm 0; }
.flow { display: flex; align-items: stretch; gap: 2.5mm; margin-top: 5mm; }
.flow .node { flex: 1; text-align: center; padding: 5mm 2mm; border-radius: 11px; background: #eaf2fc; border: 1px solid #9cbee6; }
.flow .arrow { display: flex; align-items: center; color: #2673c9; font-size: 19px; }
.node strong { display: block; font-size: 13px; color: #173b69; margin-bottom: 1mm; }
.node span { display: block; font-size: 8.5px; line-height: 1.35; color: #607590; }
.stack { display: grid; gap: 3mm; }
.row { display: grid; grid-template-columns: 36mm 1fr 46mm; align-items: center; gap: 4mm; padding: 3.2mm 4mm; border-radius: 10px; background: #f2f6fb; border: 1px solid #d9e4f0; }
.row .owner { color: #1765bd; font-weight: 700; }
.row .decision { font-size: 11px; color: #304a68; }
.row .scope { font-size: 9px; color: #71849d; text-align: right; }
.callout { margin-top: 5mm; padding: 4mm 5mm; border-radius: 11px; background: #edf9f5; border: 1px solid #9fd6ca; color: #176755; font-size: 12px; line-height: 1.5; }
.warning { background: #fff7e8; border-color: #efc77d; color: #79551f; }
.cover { padding: 0; }
.cover .content { padding: 20mm 20mm 16mm; display: grid; grid-template-columns: 1.25fr .75fr; gap: 10mm; align-items: center; }
.cover h1 { font-size: 43px; max-width: 180mm; }
.cover .subtitle { margin-top: 7mm; font-size: 17px; line-height: 1.5; color: #526b89; max-width: 175mm; }
.cover .tag { display: inline-block; margin-bottom: 7mm; padding: 2mm 4mm; border: 1px solid #87b3e6; border-radius: 999px; color: #245fa8; background: rgba(255,255,255,.75); font-size: 10px; letter-spacing: 1.3px; }
.orb { width: 66mm; height: 66mm; border-radius: 50%; margin: auto; position: relative; background: radial-gradient(circle at 35% 30%, #d8f5ff, #4b8ee8 46%, #173f86 76%); box-shadow: 0 0 70px rgba(54,130,255,.22); }
.orb::before, .orb::after { content: ""; position: absolute; border-radius: 50%; border: 1px solid rgba(148,225,255,.48); }
.orb::before { inset: -12mm; } .orb::after { inset: -23mm; border-color: rgba(98,215,255,.2); }
.orbit-label { position: absolute; font-size: 9px; color: #245b9c; letter-spacing: 1px; font-weight: 700; }
.o1 { top: -17mm; left: 19mm; } .o2 { right: -21mm; top: 29mm; } .o3 { bottom: -17mm; left: 18mm; }
.big-line { font-size: 26px; line-height: 1.25; font-weight: 700; color: #173a65; }
.architecture { display: grid; grid-template-columns: repeat(4, 1fr); gap: 4mm; margin-top: 5mm; }
.architecture .card { min-height: 59mm; }
.architecture .num { font-size: 11px; color: #226fc4; margin-bottom: 4mm; }
.architecture h3 { font-size: 16px; }
.two-loop { display: grid; grid-template-columns: 1fr 1fr; gap: 7mm; margin-top: 5mm; }
.loop { border-radius: 50%; border: 2px solid #80aee2; min-height: 86mm; display: flex; align-items: center; justify-content: center; text-align: center; padding: 13mm; position: relative; background: radial-gradient(circle, #edf5ff, transparent 70%); }
.loop.green-loop { border-color: #79c7b7; background: radial-gradient(circle, #ecfaf6, transparent 70%); }
.loop .label { font-size: 19px; font-weight: 700; color: #183c68; }
.loop .sub { font-size: 11px; line-height: 1.5; color: #5c728e; margin-top: 3mm; }
.artifact-line { display: flex; align-items: center; gap: 3mm; margin-top: 7mm; }
.artifact { flex: 1; min-height: 48mm; padding: 4mm; border-radius: 10px; background: #f6f9fd; border: 1px solid #d8e3ef; border-top: 3px solid #3d8dff; }
.artifact:nth-child(2n) { border-top-color: #45d6ac; }
.artifact strong { font-size: 12px; color: #183b67; display: block; margin-bottom: 2mm; }
.artifact span { font-size: 8.8px; line-height: 1.45; color: #5d728d; }
.governance { display: grid; grid-template-columns: 1fr 1fr; gap: 6mm; margin-top: 5mm; }
.guardrail { display: grid; grid-template-columns: 32mm 1fr; gap: 4mm; padding: 4mm; border-bottom: 1px solid #dde6f0; }
.guardrail strong { color: #1765bd; font-size: 12px; }
.guardrail span { color: #526982; font-size: 10.5px; line-height: 1.45; }
.roadmap { display: grid; grid-template-columns: repeat(3, 1fr); gap: 5mm; margin-top: 6mm; }
.roadmap .card { min-height: 66mm; }
.status { display: inline-block; margin-top: 3mm; font-size: 8.5px; color: #8ea2c0; border: 1px solid rgba(142,162,192,.25); border-radius: 999px; padding: 1.2mm 2.5mm; }
.page.preview-hide { display: none; }
@media screen {
  body { padding: 16px; }
  .page { margin: 0 auto 16px; box-shadow: 0 16px 50px rgba(0,0,0,.35); }
  body.preview { padding: 0; overflow: hidden; }
  body.preview .page { margin: 0; box-shadow: none; }
}
"""


EN_PAGES = [
    ("cover", """
      <div><div class="tag">EXECUTIVE ARCHITECTURE BRIEF · TECHNICAL PREVIEW</div>
      <h1>ForgeFlow</h1><div class="big-line accent">A stateful execution protocol for AI-assisted software engineering</div>
      <p class="subtitle">A protocol layer above delivery methods: governing how AI Agents make decisions, preserve engineering state and recover execution.</p>
      <div style="margin-top:10mm"><span class="pill">Agent-agnostic Core</span><span class="pill">Repository-native</span><span class="pill">Evidence-driven</span></div></div>
      <div class="orb"><span class="orbit-label o1">STATE</span><span class="orbit-label o2">OWNERSHIP</span><span class="orbit-label o3">VERIFICATION</span></div>
    """),
    ("01 · WHY FORGEFLOW", """
      <h2>Why AI Coding Needs<br><span class="accent">an Engineering Protocol</span></h2>
      <p class="lead">Agents can draft, code, test and refactor. The remaining problem is coordinating decisions and preserving truth across long-running delivery.</p>
      <div class="grid-2" style="margin-top:7mm">
        <div class="card"><div class="kicker">What AI already improved</div><h3>Speed and local productivity</h3><p>Rapid code generation, explanation, test drafting, refactoring and tool execution.</p></div>
        <div class="card blue"><div class="kicker">What engineering still needs</div><h3>State, authority and recovery</h3><p>Durable decisions, bounded scope, independent verification and a reliable path back upstream.</p></div>
      </div>
      <div class="grid-4" style="margin-top:5mm">
        <div class="card"><div class="metric">01</div><h3>Context drift</h3><p class="small">Conversation is not a durable source of project truth.</p></div>
        <div class="card"><div class="metric">02</div><h3>Decision blur</h3><p class="small">Agents silently decide business, architecture and delivery trade-offs.</p></div>
        <div class="card"><div class="metric">03</div><h3>Scope expansion</h3><p class="small">One task grows into unrelated implementation without explicit authorization.</p></div>
        <div class="card"><div class="metric">04</div><h3>Weak recovery</h3><p class="small">Failures become retries instead of returning to the correct decision owner.</p></div>
      </div>
    """),
    ("02 · WHAT IS FORGEFLOW", """
      <h2>An Engineering Protocol<br><span class="accent">for AI Agents</span></h2>
      <div class="quote" style="margin-top:7mm">Artifacts preserve state. Workflows own decisions. The Artifact Graph authorizes execution. Handoffs report validated transfers.</div>
      <div class="grid-3" style="margin-top:8mm">
        <div class="card green-card"><div class="kicker">Positioning</div><h3>Protocol + reference implementation</h3><p>Repository-native Markdown contracts with deterministic parsing, resolution and optional orchestration.</p></div>
        <div class="card"><div class="kicker">Relationship to Agents</div><h3>Agent-agnostic Core</h3><p>The Core does not depend on a model API or vendor runtime. Adapters isolate host-specific invocation.</p></div>
        <div class="card"><div class="kicker">Current integration boundary</div><h3>Codex and Copilot</h3><p>Dedicated launchers exist today. Other agents may read the protocol, but are not claimed as validated integrations.</p></div>
      </div>
      <div class="callout warning"><b>Leadership takeaway:</b> ForgeFlow governs how an Agent participates in delivery; it does not replace engineering judgment, CI, source control or human accountability.</div>
    """),
    ("03 · FROM SDLC TO AI ENGINEERING PROTOCOL", """
      <h2>ForgeFlow does not replace the SDLC.<br><span class="accent">It governs AI participation across it.</span></h2>
      <p class="lead">An SDLC describes delivery stages and organizational practices. ForgeFlow defines executable rules for Agent authority, evidence, transition and recovery inside those stages.</p>
      <div class="grid-2" style="margin-top:8mm">
        <div class="card"><div class="kicker">Traditional SDLC</div><h3>How software delivery is organized</h3><p>Planning, requirements, design, implementation, testing, release and operations - adapted to each organization.</p><div class="status">PROCESS MODEL</div></div>
        <div class="card green-card"><div class="kicker">ForgeFlow Protocol</div><h3>How AI execution is authorized</h3><p>Who may decide, which evidence is current, what Scope may run next, and where execution must return when blocked.</p><div class="status">EXECUTION CONTROL MODEL</div></div>
      </div>
      <div class="quote" style="margin-top:9mm">SDLC provides the organizational lifecycle. ForgeFlow provides the stateful execution protocol for AI Agents operating within it.</div>
      <div class="callout warning"><b>Positioning:</b> ForgeFlow is protocol infrastructure above any specific SDLC methodology - not a new waterfall, Agile variant or replacement for engineering management.</div>
    """),
    ("04 · FORGEFLOW PROTOCOL ARCHITECTURE", """
      <h2>Workflow / Artifact / Handoff / Ownership</h2>
      <p class="lead">The familiar Workflow, Artifact and Handoff model is completed by the Artifact Graph, which determines what is actually authorized now.</p>
      <div class="architecture">
        <div class="card"><div class="num">01</div><h3>Workflow</h3><p>Assigns exclusive responsibility for a class of engineering decisions.</p><div class="status">WHO MAY DECIDE?</div></div>
        <div class="card"><div class="num">02</div><h3>Artifact</h3><p>Persists approved intent, requirements, design, implementation and review evidence.</p><div class="status">WHAT IS TRUE?</div></div>
        <div class="card"><div class="num">03</div><h3>Handoff</h3><p>Reports a validated move across Workflow or Scope authorizations.</p><div class="status">WHO TAKES OVER?</div></div>
        <div class="card green-card"><div class="num">04</div><h3>Artifact Graph</h3><p>Validates versions, dependencies and blockers, then resolves the next authorization.</p><div class="status">WHAT MAY RUN NOW?</div></div>
      </div>
      <div class="callout">A Handoff never creates truth by itself. Every participant rebuilds the graph from repository evidence and resolves authorization again.</div>
    """),
    ("05 · WORKFLOW EXECUTION MODEL", """
      <h2>A protocol-defined execution sequence with explicit gates</h2>
      <div class="flow">
        <div class="node"><strong>PLAN</strong><span>Project intent<br>Feature order</span></div><div class="arrow">›</div>
        <div class="node"><strong>GRILL</strong><span>Observable behavior<br>Business clarity</span></div><div class="arrow">›</div>
        <div class="node"><strong>SOLUTION</strong><span>Engineering baseline<br>Cross-feature design</span></div><div class="arrow">›</div>
        <div class="node"><strong>SLICE</strong><span>Bounded delivery<br>Ordered slices</span></div><div class="arrow">›</div>
        <div class="node"><strong>TDD</strong><span>Implementation<br>Tests and evidence</span></div><div class="arrow">›</div>
        <div class="node"><strong>REVIEW</strong><span>Independent<br>PASS or FAIL</span></div>
      </div>
      <div class="grid-3" style="margin-top:8mm">
        <div class="card"><div class="kicker">Business barrier</div><h3>Planning + Requirements</h3><p>Features and observable outcomes must be current before engineering design begins.</p></div>
        <div class="card"><div class="kicker">Engineering barrier</div><h3>Solution + Slicing</h3><p>Architecture and delivery boundaries must be current before implementation begins.</p></div>
        <div class="card"><div class="kicker">Quality barrier</div><h3>TDD + Review</h3><p>Implementation evidence is independently reviewed per Slice attempt before progress continues.</p></div>
      </div>
      <div class="callout warning">This sequence is a ForgeFlow Workflow model, not a replacement for the full SDLC. Return and Recovery are protocol-level paths whenever evidence exposes an upstream gap.</div>
    """),
    ("06 · FEATURE & SLICE EXECUTION MODEL", """
      <h2>Two dimensions of controlled iteration</h2>
      <p class="lead">A project is decomposed by product value and by implementation risk - without flattening both into one task list.</p>
      <div class="two-loop">
        <div class="loop"><div><div class="label">Feature iteration</div><div class="sub">Planning declares stable Feature IDs and delivery order.<br>Each Feature receives its own Requirement contract.</div></div></div>
        <div class="loop green-loop"><div><div class="label">Slice iteration</div><div class="sub">Each Feature receives an ordered Slice Plan.<br>Every Slice advances through TDD and independent Review.</div></div></div>
      </div>
      <div class="callout"><b>Deterministic completion:</b> Planning defines Feature order. Slice Plans define Slice order. A single successful Slice can never be mistaken for project completion.</div>
    """),
    ("07 · ENGINEERING OWNERSHIP MODEL", """
      <h2>Every decision has one authoritative owner</h2>
      <p class="lead">Ownership prevents the common AI failure mode of making every decision locally because it can.</p>
      <div class="stack" style="margin-top:5mm">
        <div class="row"><div class="owner">PLAN</div><div class="decision">Project intent, Feature order, exclusions and incremental Change Set</div><div class="scope">PROJECT</div></div>
        <div class="row"><div class="owner">GRILL</div><div class="decision">Business behavior, acceptance criteria and unresolved ambiguity</div><div class="scope">FEATURE</div></div>
        <div class="row"><div class="owner">SOLUTION</div><div class="decision">Architecture, interfaces, data, security, operations and verification strategy</div><div class="scope">PROJECT</div></div>
        <div class="row"><div class="owner">SLICE</div><div class="decision">Bounded implementation slices and their declared execution order</div><div class="scope">FEATURE</div></div>
        <div class="row"><div class="owner">TDD</div><div class="decision">Implementation and tests for one authorized Slice attempt</div><div class="scope">SLICE</div></div>
        <div class="row"><div class="owner">REVIEW</div><div class="decision">Independent PASS/FAIL decision and routed findings</div><div class="scope">SLICE ATTEMPT</div></div>
      </div>
    """),
    ("08 · HANDOFF & RETURN PROTOCOL", """
      <h2>Failures return to the owner of the missing decision</h2>
      <div class="grid-2" style="margin-top:6mm">
        <div class="card"><div class="kicker">Return routing</div><div class="stack">
          <div class="row" style="grid-template-columns:40mm 1fr"><div class="owner">Business blocker</div><div class="decision">Return to Grill - or Plan for project scope</div></div>
          <div class="row" style="grid-template-columns:40mm 1fr"><div class="owner">Engineering blocker</div><div class="decision">Return to Solution</div></div>
          <div class="row" style="grid-template-columns:40mm 1fr"><div class="owner">Slice boundary</div><div class="decision">Return to Slice</div></div>
          <div class="row" style="grid-template-columns:40mm 1fr"><div class="owner">Implementation issue</div><div class="decision">Return to TDD</div></div>
        </div></div>
        <div class="card green-card"><div class="kicker">Recovery without conversation memory</div><h3>Restart from evidence</h3><p>A new process rebuilds the Artifact Graph, validates the current persisted blocker and re-authorizes only the correct owner and scope.</p>
          <div class="callout" style="margin-top:6mm">Runtime history is diagnostic. Repository evidence remains the recovery authority.</div>
        </div>
      </div>
      <div class="quote" style="margin-top:7mm">ForgeFlow distinguishes retrying execution from correcting the decision that made execution impossible.</div>
    """),
    ("09 · ARTIFACT & ENGINEERING STATE", """
      <h2>Engineering knowledge becomes a versioned evidence chain</h2>
      <div class="artifact-line">
        <div class="artifact"><strong>Planning</strong><span>Intent, Feature order, constraints, Change Set</span></div>
        <div class="artifact"><strong>Requirement</strong><span>Behavior, acceptance criteria, business contract version</span></div>
        <div class="artifact"><strong>Solution Plan</strong><span>Engineering baseline and per-Feature engineering versions</span></div>
        <div class="artifact"><strong>Slice Plan</strong><span>Ordered delivery boundaries for one Feature</span></div>
        <div class="artifact"><strong>TDD Record</strong><span>Implementation attempt, tests and current upstream versions</span></div>
        <div class="artifact"><strong>Review Report</strong><span>Immutable attempt, findings, PASS/FAIL and Return disposition</span></div>
      </div>
      <div class="grid-3" style="margin-top:8mm">
        <div class="card"><h3>Current truth</h3><p>Only canonical paths and valid current versions participate in authorization.</p></div>
        <div class="card"><h3>Historical trace</h3><p>Replaced contracts and supplemental reports move to dedicated history roots.</p></div>
        <div class="card"><h3>Scoped change</h3><p>Feature contract and engineering versions preserve unaffected downstream evidence.</p></div>
      </div>
    """),
    ("10 · AI ENGINEERING GOVERNANCE", """
      <h2>Governance is embedded in execution, not added after it</h2>
      <div class="governance">
        <div class="card"><div class="guardrail"><strong>Scope</strong><span>Typed Project, Feature and Slice authorization prevents silent expansion.</span></div><div class="guardrail"><strong>Decision</strong><span>Exclusive Artifact ownership prevents agents from approving their own assumptions.</span></div><div class="guardrail"><strong>Quality</strong><span>TDD evidence and independent Review create a per-attempt quality gate.</span></div></div>
        <div class="card"><div class="guardrail"><strong>Traceability</strong><span>Version edges connect intent, requirement, design, implementation and verification.</span></div><div class="guardrail"><strong>AI overreach</strong><span>Invalid, stale or contradictory evidence fails closed instead of authorizing work.</span></div><div class="guardrail"><strong>Extensibility</strong><span>Markdown Review plugins add ordered checks without transferring PASS/FAIL ownership.</span></div></div>
      </div>
      <div class="callout warning"><b>Important boundary:</b> ForgeFlow reduces workflow risk. It does not guarantee model correctness or replace normal security, branch protection, CI and human review.</div>
    """),
    ("11 · AGENT INDEPENDENCE", """
      <h2>Copilot / Claude / Codex independent by design</h2>
      <p class="lead">ForgeFlow's protocol truth lives in repository contracts, not in a model, prompt product or vendor runtime.</p>
      <div class="grid-3" style="margin-top:7mm">
        <div class="card"><div class="metric">1</div><h3>Stable Core</h3><p>Workflow, Artifact, Handoff and Ownership semantics remain host-independent.</p></div>
        <div class="card"><div class="metric">2</div><h3>Thin Adapters</h3><p>Launchers translate host invocation into the same protocol-defined Workflow entry.</p></div>
        <div class="card green-card"><div class="metric">3</div><h3>Replaceable Agents</h3><p>Teams can change Agents without replacing engineering state or governance contracts.</p></div>
      </div>
      <div class="grid-2" style="margin-top:8mm"><div class="card green-card"><h3>Validated today</h3><p>Dedicated ForgeFlow launchers and adapter content exist for Codex and GitHub Copilot.</p></div><div class="card"><h3>Protocol-compatible direction</h3><p>Claude and other Agents can participate through conforming adapters, but are not presented here as currently validated integrations.</p></div></div>
      <div class="callout">Agent independence protects the durable investment: engineering evidence, decision ownership and transition rules remain portable.</div>
    """),
    ("12 · FUTURE VISION", """
      <h2>From AI coding assistance to governed AI engineering</h2>
      <p class="lead">The strategic direction is a portable execution protocol that makes AI participation observable, replaceable and accountable across the software lifecycle.</p>
      <div class="roadmap">
        <div class="card"><div class="kicker">Strengthen the Core</div><h3>Stable protocol and test matrix</h3><p>Freeze versioned contracts, expand transition coverage and preserve deterministic behavior across implementations.</p><div class="status">DIRECTION - NOT A CURRENT CLAIM</div></div>
        <div class="card"><div class="kicker">Broaden the Edge</div><h3>More validated Adapters</h3><p>Add host integrations only after verifying real discovery, invocation, permissions and acceptance behavior.</p><div class="status">DIRECTION - NOT A CURRENT CLAIM</div></div>
        <div class="card green-card"><div class="kicker">Operationalize Governance</div><h3>Safer automation and upgrade paths</h3><p>Improve distribution, refresh, evidence inspection and controlled automation without creating a second source of truth.</p><div class="status">DIRECTION - NOT A CURRENT CLAIM</div></div>
      </div>
      <div class="quote" style="margin-top:8mm">From AI Coding to Protocol-Driven AI Engineering: the long-term asset is not one smarter Agent, but a system that safely coordinates changing Agents.</div>
    """),
]


ZH_PAGES = [
    ("cover", """
      <div><div class="tag">管理层架构简报 · TECHNICAL PREVIEW</div>
      <h1>ForgeFlow</h1><div class="big-line accent">面向 AI 辅助软件工程的有状态执行协议</div>
      <p class="subtitle">位于交付方法之上的协议层：治理 AI Agent 如何决策、保存工程状态，以及恢复执行。</p>
      <div style="margin-top:10mm"><span class="pill">Agent-agnostic Core</span><span class="pill">仓库原生</span><span class="pill">证据驱动</span></div></div>
      <div class="orb"><span class="orbit-label o1">状态</span><span class="orbit-label o2">所有权</span><span class="orbit-label o3">验证</span></div>
    """),
    ("01 · 为什么需要 FORGEFLOW", """
      <h2>为什么 AI Coding 需要<br><span class="accent">一套工程协议</span></h2>
      <p class="lead">Agent 已经可以生成代码、测试和重构。真正遗留的问题，是如何在长期交付中协调决策并保存可信状态。</p>
      <div class="grid-2" style="margin-top:7mm"><div class="card"><div class="kicker">AI 已经改善</div><h3>速度与局部生产力</h3><p>快速生成代码、解释逻辑、编写测试、执行重构和调用工具。</p></div><div class="card blue"><div class="kicker">工程仍然需要</div><h3>状态、授权与恢复</h3><p>持久决策、受控 Scope、独立验证，以及回到正确上游的可靠路径。</p></div></div>
      <div class="grid-4" style="margin-top:5mm"><div class="card"><div class="metric">01</div><h3>上下文漂移</h3><p class="small">对话不是持久、可靠的项目事实来源。</p></div><div class="card"><div class="metric">02</div><h3>决策混杂</h3><p class="small">Agent 静默代替业务、架构与交付角色作出决定。</p></div><div class="card"><div class="metric">03</div><h3>Scope 扩张</h3><p class="small">单个任务在没有授权时扩大为无关实现。</p></div><div class="card"><div class="metric">04</div><h3>恢复薄弱</h3><p class="small">失败被当作重试，而不是返回缺失决策的 Owner。</p></div></div>
    """),
    ("02 · FORGEFLOW 是什么", """
      <h2>一套面向 AI Agent 的<br><span class="accent">工程执行协议</span></h2>
      <div class="quote" style="margin-top:7mm">Artifacts 保存状态。Workflows 拥有决策。Artifact Graph 授权执行。Handoffs 报告经过验证的执行转移。</div>
      <div class="grid-3" style="margin-top:8mm"><div class="card green-card"><div class="kicker">定位</div><h3>协议 + 参考实现</h3><p>仓库原生 Markdown 契约，配合确定性解析、状态计算和可选编排。</p></div><div class="card"><div class="kicker">与 Agent 的关系</div><h3>Agent-agnostic Core</h3><p>Core 不依赖模型 API 或厂商 Runtime；Adapter 隔离宿主专属调用。</p></div><div class="card"><div class="kicker">当前集成边界</div><h3>Codex 与 Copilot</h3><p>当前提供专用 Launcher；其他 Agent 可读取协议，但不宣称已经完成验证。</p></div></div>
      <div class="callout warning"><b>管理层结论：</b>ForgeFlow 治理 Agent 如何参与交付，但不替代工程判断、CI、源代码管理和人的最终责任。</div>
    """),
    ("03 · 从 SDLC 到 AI 工程协议", """
      <h2>ForgeFlow 不替代 SDLC，<br><span class="accent">而是治理 AI 如何参与其中。</span></h2>
      <p class="lead">SDLC 描述软件交付阶段和组织实践；ForgeFlow 定义 Agent 在这些阶段中的授权、证据、转移与恢复规则。</p>
      <div class="grid-2" style="margin-top:8mm"><div class="card"><div class="kicker">传统 SDLC</div><h3>软件交付如何组织</h3><p>规划、需求、设计、实现、测试、发布与运维，并由组织选择适合的方法。</p><div class="status">过程模型</div></div><div class="card green-card"><div class="kicker">ForgeFlow Protocol</div><h3>AI 执行如何被授权</h3><p>谁可以决定、哪些证据有效、下一步允许执行什么，以及受阻时必须返回哪里。</p><div class="status">执行控制模型</div></div></div>
      <div class="quote" style="margin-top:9mm">SDLC 提供组织级生命周期，ForgeFlow 提供 AI Agent 在其中运行的有状态执行协议。</div>
      <div class="callout warning"><b>定位：</b>ForgeFlow 是位于具体 SDLC 方法之上的协议基础设施，不是新的瀑布模型、Agile 变体或工程管理替代品。</div>
    """),
    ("04 · FORGEFLOW 协议架构", """
      <h2>Workflow / Artifact / Handoff / Ownership</h2><p class="lead">Workflow、Artifact 与 Handoff 的三机制，由 Artifact Graph 补全：它负责判断现在真正允许执行什么。</p>
      <div class="architecture"><div class="card"><div class="num">01</div><h3>Workflow</h3><p>为某一类工程决策指定唯一责任主体。</p><div class="status">谁可以决定？</div></div><div class="card"><div class="num">02</div><h3>Artifact</h3><p>保存已批准的意图、需求、设计、实现和 Review 证据。</p><div class="status">什么是真实状态？</div></div><div class="card"><div class="num">03</div><h3>Handoff</h3><p>报告跨 Workflow 或 Scope 的已验证转移。</p><div class="status">谁来接手？</div></div><div class="card green-card"><div class="num">04</div><h3>Artifact Graph</h3><p>验证版本、依赖与 Blocker，然后解析下一授权。</p><div class="status">现在允许做什么？</div></div></div>
      <div class="callout">Handoff 本身不会创造事实。每个参与者都必须从仓库证据重新构建 Graph，并再次解析授权。</div>
    """),
    ("05 · WORKFLOW 执行模型", """
      <h2>由协议定义、带显式门禁的执行序列</h2>
      <div class="flow"><div class="node"><strong>PLAN</strong><span>项目意图<br>Feature 顺序</span></div><div class="arrow">›</div><div class="node"><strong>GRILL</strong><span>可观察行为<br>业务澄清</span></div><div class="arrow">›</div><div class="node"><strong>SOLUTION</strong><span>工程基线<br>跨 Feature 设计</span></div><div class="arrow">›</div><div class="node"><strong>SLICE</strong><span>有限交付<br>有序 Slice</span></div><div class="arrow">›</div><div class="node"><strong>TDD</strong><span>实现<br>测试与证据</span></div><div class="arrow">›</div><div class="node"><strong>REVIEW</strong><span>独立<br>PASS 或 FAIL</span></div></div>
      <div class="grid-3" style="margin-top:8mm"><div class="card"><div class="kicker">业务门禁</div><h3>Planning + Requirements</h3><p>Feature 和可观察结果必须有效，才进入工程设计。</p></div><div class="card"><div class="kicker">工程门禁</div><h3>Solution + Slicing</h3><p>架构与交付边界必须有效，才进入实现。</p></div><div class="card"><div class="kicker">质量门禁</div><h3>TDD + Review</h3><p>每个 Slice Attempt 的实现证据必须经过独立 Review。</p></div></div>
      <div class="callout warning">这是 ForgeFlow Workflow 模型，不是对完整 SDLC 的替代。证据暴露上游缺口时，Return 与 Recovery 是协议级路径。</div>
    """),
    ("06 · FEATURE / SLICE 执行模型", """
      <h2>两个维度的受控迭代</h2><p class="lead">项目同时按产品价值和实现风险拆分，而不是把两者压平成一张无序任务清单。</p>
      <div class="two-loop"><div class="loop"><div><div class="label">Feature iteration</div><div class="sub">Planning 声明稳定 Feature ID 和顺序。<br>每个 Feature 拥有独立 Requirement Contract。</div></div></div><div class="loop green-loop"><div><div class="label">Slice iteration</div><div class="sub">每个 Feature 拥有有序 Slice Plan。<br>每个 Slice 依次进入 TDD 与独立 Review。</div></div></div></div>
      <div class="callout"><b>确定性完成：</b>Planning 决定 Feature 顺序，Slice Plan 决定 Slice 顺序。单个 Slice 成功不会被误判为项目完成。</div>
    """),
    ("07 · 工程所有权模型", """
      <h2>每一种决策只有一个权威 Owner</h2><p class="lead">所有权机制解决 AI 因为“能决定”就把所有问题都在当前阶段自行决定的问题。</p>
      <div class="stack" style="margin-top:5mm"><div class="row"><div class="owner">PLAN</div><div class="decision">项目意图、Feature 顺序、排除项和增量 Change Set</div><div class="scope">PROJECT</div></div><div class="row"><div class="owner">GRILL</div><div class="decision">业务行为、验收标准和未解决歧义</div><div class="scope">FEATURE</div></div><div class="row"><div class="owner">SOLUTION</div><div class="decision">架构、接口、数据、安全、运维与验证策略</div><div class="scope">PROJECT</div></div><div class="row"><div class="owner">SLICE</div><div class="decision">有限实现切片及其声明执行顺序</div><div class="scope">FEATURE</div></div><div class="row"><div class="owner">TDD</div><div class="decision">单个获准 Slice Attempt 的实现与测试</div><div class="scope">SLICE</div></div><div class="row"><div class="owner">REVIEW</div><div class="decision">独立 PASS/FAIL 决策和 Findings 路由</div><div class="scope">SLICE ATTEMPT</div></div></div>
    """),
    ("08 · HANDOFF / RETURN 协议", """
      <h2>失败返回缺失决策的 Owner</h2>
      <div class="grid-2" style="margin-top:6mm"><div class="card"><div class="kicker">Return 路由</div><div class="stack"><div class="row" style="grid-template-columns:40mm 1fr"><div class="owner">Business Blocker</div><div class="decision">返回 Grill；Project Scope 返回 Plan</div></div><div class="row" style="grid-template-columns:40mm 1fr"><div class="owner">Engineering Blocker</div><div class="decision">返回 Solution</div></div><div class="row" style="grid-template-columns:40mm 1fr"><div class="owner">Slice Boundary</div><div class="decision">返回 Slice</div></div><div class="row" style="grid-template-columns:40mm 1fr"><div class="owner">Implementation Issue</div><div class="decision">返回 TDD</div></div></div></div><div class="card green-card"><div class="kicker">无需对话记忆的 Recovery</div><h3>从证据重新启动</h3><p>新进程重建 Artifact Graph，验证当前持久化 Blocker，只重新授权正确 Owner 与 Scope。</p><div class="callout" style="margin-top:6mm">Runtime History 用于诊断，仓库证据才是恢复权威。</div></div></div>
      <div class="quote" style="margin-top:7mm">ForgeFlow 区分“重试执行”和“修正导致执行无法继续的决策”。</div>
    """),
    ("09 · ARTIFACT 与工程状态", """
      <h2>工程知识沉淀为版本化证据链</h2>
      <div class="artifact-line"><div class="artifact"><strong>Planning</strong><span>Intent、Feature 顺序、约束、Change Set</span></div><div class="artifact"><strong>Requirement</strong><span>行为、验收标准、业务 Contract Version</span></div><div class="artifact"><strong>Solution Plan</strong><span>工程基线和每 Feature Engineering Version</span></div><div class="artifact"><strong>Slice Plan</strong><span>单个 Feature 的有序交付边界</span></div><div class="artifact"><strong>TDD Record</strong><span>实现 Attempt、测试和当前上游版本</span></div><div class="artifact"><strong>Review Report</strong><span>不可变 Attempt、Findings、PASS/FAIL 和 Return</span></div></div>
      <div class="grid-3" style="margin-top:8mm"><div class="card"><h3>当前事实</h3><p>只有规范路径和有效当前版本参与授权。</p></div><div class="card"><h3>历史追踪</h3><p>被替换 Contract 与补充 Report 进入专用 History Root。</p></div><div class="card"><h3>作用域化变更</h3><p>Feature Contract 与 Engineering Version 保留未受影响证据。</p></div></div>
    """),
    ("10 · AI 工程治理", """
      <h2>治理嵌入执行过程，而不是事后补充</h2>
      <div class="governance"><div class="card"><div class="guardrail"><strong>Scope</strong><span>Project、Feature、Slice 类型化授权，防止静默扩张。</span></div><div class="guardrail"><strong>Decision</strong><span>Artifact 独占所有权，防止 Agent 自行批准假设。</span></div><div class="guardrail"><strong>Quality</strong><span>TDD 证据和独立 Review 形成逐 Attempt 质量门禁。</span></div></div><div class="card"><div class="guardrail"><strong>Traceability</strong><span>Version Edge 连接意图、需求、设计、实现和验证。</span></div><div class="guardrail"><strong>AI 越权</strong><span>非法、过期或矛盾证据失败关闭，不授权生产性工作。</span></div><div class="guardrail"><strong>Extensibility</strong><span>Markdown Review Plugin 增加检查，但不转移 PASS/FAIL 所有权。</span></div></div></div>
      <div class="callout warning"><b>重要边界：</b>ForgeFlow 降低流程风险，但不保证模型正确，也不替代安全控制、分支保护、CI 和人工 Review。</div>
    """),
    ("11 · AGENT INDEPENDENCE", """
      <h2>设计上与 Copilot / Claude / Codex 无关</h2>
      <p class="lead">ForgeFlow 的协议事实保存在仓库契约中，而不是绑定在某个模型、Prompt 产品或厂商 Runtime 中。</p>
      <div class="grid-3" style="margin-top:7mm"><div class="card"><div class="metric">1</div><h3>稳定 Core</h3><p>Workflow、Artifact、Handoff 与 Ownership 语义保持宿主无关。</p></div><div class="card"><div class="metric">2</div><h3>轻量 Adapter</h3><p>Launcher 把宿主调用转换为同一套协议定义的 Workflow 入口。</p></div><div class="card green-card"><div class="metric">3</div><h3>Agent 可替换</h3><p>团队更换 Agent 时，无需替换工程状态与治理契约。</p></div></div>
      <div class="grid-2" style="margin-top:8mm"><div class="card green-card"><h3>当前已验证</h3><p>当前为 Codex 与 GitHub Copilot 提供 ForgeFlow 专用 Launcher 和 Adapter 内容。</p></div><div class="card"><h3>协议兼容方向</h3><p>Claude 和其他 Agent 可通过符合协议的 Adapter 接入，但本文不把它们表述为当前已验证集成。</p></div></div>
      <div class="callout">Agent Independence 保护的是长期投入：工程证据、决策所有权与转移规则可以持续复用。</div>
    """),
    ("12 · 未来愿景", """
      <h2>从 AI Coding Assistance 走向可治理 AI Engineering</h2><p class="lead">战略方向是构建可移植执行协议，让 AI 在整个软件生命周期中的参与可观察、可替换、可问责。</p>
      <div class="roadmap"><div class="card"><div class="kicker">强化 Core</div><h3>稳定协议与测试矩阵</h3><p>冻结版本化契约，扩展 Transition 覆盖，在不同实现中保持确定性行为。</p><div class="status">方向，不是当前能力声明</div></div><div class="card"><div class="kicker">扩展边缘</div><h3>更多经过验证的 Adapter</h3><p>只有验证真实发现、调用、权限和验收行为后，才增加宿主集成。</p><div class="status">方向，不是当前能力声明</div></div><div class="card green-card"><div class="kicker">治理运营化</div><h3>更安全的自动化与升级路径</h3><p>改善分发、刷新、证据检查和受控自动化，不创建第二份事实来源。</p><div class="status">方向，不是当前能力声明</div></div></div>
      <div class="quote" style="margin-top:8mm">从 AI Coding 走向 Protocol-Driven AI Engineering：长期资产不是某一个更聪明的 Agent，而是一套能够安全协调不断变化 Agent 的工程系统。</div>
    """),
]


def chrome_path() -> Path:
    for candidate in CHROME_CANDIDATES:
        if candidate.is_file():
            return candidate
    raise FileNotFoundError("A supported Chromium browser was not found")


def document(locale: str, pages: list[tuple[str, str]]) -> str:
    title = "ForgeFlow Executive Architecture Brief"
    if locale == "zh-CN":
        title = "ForgeFlow 管理层架构简报"
    rendered = []
    total = len(pages)
    for index, (section, body) in enumerate(pages, start=1):
        page_class = "page cover" if section == "cover" else "page"
        topline = "" if section == "cover" else (
            f'<div class="topline"><div class="brand">ForgeFlow · Executive Architecture Brief</div>'
            f'<div class="section-no">{html.escape(section)}</div></div>'
        )
        footer = (
            f'<div class="footer"><span>ForgeFlow · Technical Preview · 2026-08-19</span>'
            f'<span>{index:02d} / {total:02d}</span></div>'
        )
        rendered.append(f'<section class="{page_class}" data-page="{index}"><div class="content">{topline}{body}</div>{footer}</section>')
    script = """
    const params = new URLSearchParams(location.search);
    const selected = Number(params.get('page') || 0);
    if (selected) {
      document.body.classList.add('preview');
      document.querySelectorAll('.page').forEach((page, index) => {
        if (index + 1 !== selected) page.classList.add('preview-hide');
      });
    }
    """
    return f"<!doctype html><html lang=\"{locale}\"><head><meta charset=\"utf-8\"><title>{html.escape(title)}</title><style>{CSS}</style></head><body>{''.join(rendered)}<script>{script}</script></body></html>"


def run_chrome(arguments: list[str], expected: Path) -> None:
    profile = SCRATCH / f"chrome-profile-{time.monotonic_ns()}"
    profile.mkdir(parents=True, exist_ok=True)
    command = [
        str(chrome_path()),
        "--headless=new",
        "--disable-gpu",
        "--disable-background-networking",
        "--disable-component-update",
        "--disable-default-apps",
        "--disable-extensions",
        "--disable-sync",
        "--metrics-recording-only",
        "--no-first-run",
        "--no-default-browser-check",
        f"--user-data-dir={profile}",
        *arguments,
    ]
    expected.unlink(missing_ok=True)
    process = subprocess.Popen(
        command,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    deadline = time.monotonic() + 20
    last_size = -1
    stable_checks = 0
    try:
        while time.monotonic() < deadline:
            if expected.is_file() and expected.stat().st_size > 1024:
                size = expected.stat().st_size
                stable_checks = stable_checks + 1 if size == last_size else 0
                last_size = size
                if stable_checks >= 3:
                    return
            if process.poll() is not None:
                break
            time.sleep(0.2)
    finally:
        if process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout=3)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()
        shutil.rmtree(profile, ignore_errors=True)
    if not expected.is_file() or expected.stat().st_size <= 1024:
        raise RuntimeError(f"Chrome did not create {expected}")


def build(
    previews: bool, selected_locale: str, preview_pages: tuple[int, ...] = ()
) -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    if selected_locale == "all" and SCRATCH.exists():
        shutil.rmtree(SCRATCH)
    SCRATCH.mkdir(parents=True, exist_ok=True)
    documents = {
        "en": (EN_PAGES, "forgeflow-executive-architecture-brief.en.pdf"),
        "zh-CN": (ZH_PAGES, "forgeflow-executive-architecture-brief.zh-CN.pdf"),
    }
    for locale, (pages, filename) in documents.items():
        if selected_locale not in ("all", locale):
            continue
        source = SCRATCH / f"executive-brief.{locale}.html"
        source.write_text(document(locale, pages), encoding="utf-8")
        target = OUTPUT / filename
        run_chrome([
            "--print-to-pdf-no-header",
            "--no-pdf-header-footer",
            f"--print-to-pdf={target}",
            source.as_uri(),
        ], target)
        if previews:
            preview_root = SCRATCH / f"previews-{locale}"
            if preview_root.exists():
                shutil.rmtree(preview_root)
            preview_root.mkdir()
            page_numbers = preview_pages or tuple(range(1, len(pages) + 1))
            for index in page_numbers:
                if not 1 <= index <= len(pages):
                    raise ValueError(f"Preview page out of range: {index}")
                image = preview_root / f"page-{index:02d}.png"
                run_chrome([
                    "--hide-scrollbars",
                    "--force-device-scale-factor=1",
                    "--window-size=1584,1120",
                    f"--screenshot={image}",
                    f"{source.as_uri()}?page={index}",
                ], image)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--previews", action="store_true")
    parser.add_argument("--preview-page", action="append", type=int, default=[])
    parser.add_argument("--locale", choices=("all", "en", "zh-CN"), default="all")
    args = parser.parse_args()
    build(args.previews, args.locale, tuple(args.preview_page))


if __name__ == "__main__":
    main()
