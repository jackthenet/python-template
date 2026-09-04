import {
  agent,
  choice,
  compute,
  defineHumanChoices,
  defineWorkflow,
  humanDecision,
  humanDecisionEdge,
} from "@osolmaz/pi-workflows";

type SpecTDDInput = {
  task: string;
};

/**
 * spec-tdd — orchestrate the repository's 6-Phase Spec-TDD protocol as one
 * durable workflow run. Each phase is an agent step that reads and follows the
 * matching skill under .agents/skills/<phase>/SKILL.md, then reports whether the
 * phase completed ("done") or is blocked ("blocked").
 *
 * Phase 1 (DISCOVER & SPECIFY) is gated by a human decision: the specification
 * must be approved before it is decomposed into a task DAG. Any phase reporting
 * "blocked" routes to a terminal blocked node so the run stops for review.
 */

const phaseOutput = `{ "status": "done" | "blocked", "summary": "<one-line summary>" }`;

const approveChoices = defineHumanChoices({
  continue: choice({ label: "Approved, continue" }),
  stop: choice({ label: "Not approved, stop" }),
});

function phasePrompt(phase: string, skill: string, request: string, detail: string, doneNote: string, blockedNote: string): string {
  return [
    `Execute ${phase} for this feature.`,
    ``,
    `Feature request:`,
    request,
    ``,
    `Read and follow the skill at .agents/skills/${skill}/SKILL.md. ${detail}`,
    ``,
    `When the phase is complete (${doneNote}), submit:`,
    `{ "status": "done", "summary": "<one-line summary>" }`,
    `If you cannot complete the phase safely (${blockedNote}), submit:`,
    `{ "status": "blocked", "summary": "<what is blocked and why>" }`,
  ].join("\n");
}

export default defineWorkflow({
  name: "spec-tdd",
  title: ({ input }) => `Spec-TDD: ${(input as SpecTDDInput).task}`,
  startAt: "specify",
  maxSteps: 100,
  input: (value: unknown) => {
    const v = value as Partial<SpecTDDInput>;
    if (typeof v.task !== "string" || v.task.trim().length === 0) {
      throw new Error("spec-tdd requires a non-empty 'task' string.");
    }
    return v as SpecTDDInput;
  },
  nodes: {
    specify: agent({
      prompt: ({ input }) =>
        phasePrompt(
          "Phase 1 (DISCOVER & SPECIFY)",
          "specify",
          (input as SpecTDDInput).task,
          "It covers creating the feature branch from main, adversarially interrogating the feature idea into a brief, writing the specification with stable REQ/AC/INV/EDGE/NFR IDs, and presenting it for human approval via a Git PR.",
          "the spec is written and presented for approval",
          "you cannot safely produce an approvable spec",
        ),
      expectedOutput: phaseOutput,
    }),
    approveSpec: humanDecision({
      audience: "operator",
      choices: approveChoices,
      request: ({ outputs }) => ({
        title: "Approve the specification",
        subject: { phase: "specify", result: outputs.specify },
        presentation: {
          schema: "pi-workflows.decision-presentation.v1",
          summary: "The specification has been written and presented for approval. Approve it before decomposing into a task DAG.",
          blocks: [{ kind: "paragraph", text: "Review the spec. Approving continues the workflow; stopping halts it for rework." }],
        },
      }),
    }),
    decompose: agent({
      prompt: ({ input }) =>
        phasePrompt(
          "Phase 2 (DECOMPOSE)",
          "decompose",
          (input as SpecTDDInput).task,
          "It covers creating ADRs for significant design decisions and decomposing the approved specification into a machine-readable JSON task DAG at docs/tasks/[feature-name].tasks.json.",
          "the ADRs and the task DAG are written",
          "you cannot safely decompose the spec",
        ),
      expectedOutput: phaseOutput,
    }),
    test: agent({
      prompt: ({ input }) =>
        phasePrompt(
          "Phase 3 (TEST & RED)",
          "test",
          (input as SpecTDDInput).task,
          "It covers writing acceptance/property/unit/contract/integration tests derived from the specification, running the suite to confirm RED state, recording RED evidence in docs/verification/, and updating the traceability matrix.",
          "the tests are written and RED is confirmed",
          "RED cannot be confirmed",
        ),
      expectedOutput: phaseOutput,
    }),
    implement: agent({
      prompt: ({ input }) =>
        phasePrompt(
          "Phase 4 (IMPLEMENT)",
          "implement",
          (input as SpecTDDInput).task,
          "It covers implementing the minimum behavior to turn failing tests (RED) into passing tests (GREEN), refactoring without changing behavior while re-running tests, and recording GREEN evidence.",
          "GREEN is achieved and the code is refactored",
          "you cannot safely reach GREEN",
        ),
      expectedOutput: phaseOutput,
    }),
    verify: agent({
      prompt: ({ input }) =>
        phasePrompt(
          "Phase 5 (VERIFY)",
          "verify",
          (input as SpecTDDInput).task,
          "It covers running the full/acceptance/property/contract suites, updating the traceability matrix, and producing a verification report with spec coverage = 100%.",
          "spec coverage = 100% and all gates pass",
          "spec coverage is below 100% or a gate fails",
        ),
      expectedOutput: phaseOutput,
    }),
    review: agent({
      prompt: ({ input }) =>
        phasePrompt(
          "Phase 6 (REVIEW)",
          "review",
          (input as SpecTDDInput).task,
          "It covers reviewing the code changes against the specification, checking traceability, feature boundaries, and architecture rules, and producing a clean review report.",
          "the review report is clean",
          "the review report is not clean",
        ),
      expectedOutput: phaseOutput,
    }),
    complete: compute({
      run: ({ outputs }) => ({
        status: "complete",
        phases: {
          specify: outputs.specify,
          decompose: outputs.decompose,
          test: outputs.test,
          implement: outputs.implement,
          verify: outputs.verify,
          review: outputs.review,
        },
      }),
    }),
    blocked: compute({
      run: ({ outputs }) => ({
        status: "blocked",
        phases: {
          specify: outputs.specify,
          decompose: outputs.decompose,
          test: outputs.test,
          implement: outputs.implement,
          verify: outputs.verify,
          review: outputs.review,
        },
      }),
    }),
  },
  edges: [
    { from: "specify", switch: { on: "$.status", cases: { done: "approveSpec", blocked: "blocked" } } },
    humanDecisionEdge({
      from: "approveSpec",
      choices: approveChoices,
      cases: { continue: "decompose", stop: "blocked" },
    }),
    { from: "decompose", switch: { on: "$.status", cases: { done: "test", blocked: "blocked" } } },
    { from: "test", switch: { on: "$.status", cases: { done: "implement", blocked: "blocked" } } },
    { from: "implement", switch: { on: "$.status", cases: { done: "verify", blocked: "blocked" } } },
    { from: "verify", switch: { on: "$.status", cases: { done: "review", blocked: "blocked" } } },
    { from: "review", switch: { on: "$.status", cases: { done: "complete", blocked: "blocked" } } },
  ],
});
