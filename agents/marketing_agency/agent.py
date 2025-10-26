import random
from typing import Any, Dict, List

from google.adk.agents import LlmAgent, SequentialAgent, ParallelAgent, LoopAgent
from google.adk.models.lite_llm import LiteLlm


def _print_header(title: str) -> None:
    print("\n" + "=" * 80)
    print(title)
    print("=" * 80)


# -----------------------------
# Agent definitions
# -----------------------------

ceo_agent = LlmAgent(
    model=LiteLlm(model="claude-3-7-sonnet-20250219"),
    name="ceo_agent",
    description="CEO reviews brief, sets strategy, provides sign-off",
    instruction=(
        "You are the CEO. Read the marketing brief in inputs['brief'] and defaults in pipeline.defaults.\n"
        "Set clear goals, constraints, and success metrics. Later, provide final sign-off."
    ),
)

copywriter_agent = LlmAgent(
    model=LiteLlm(model="claude-3-7-sonnet-20250219"),
    name="copywriter_agent",
    description="Creates campaign brief with A/B variants",
    instruction=(
        "You are a copywriter. Create a campaign brief with two variants A and B.\n"
        "Include headlines, body, CTA, and rationale for each.\n"
        "Output JSON with keys: { 'campaign_brief': { 'A': {...}, 'B': {...} } }"
    ),
)

legal_agent = LlmAgent(
    model=LiteLlm(model="claude-3-7-sonnet-20250219"),
    name="legal_agent",
    description="Ensures claims are compliant; sets all_clear flag",
    instruction=(
        "You are Legal. Review the latest campaign content.\n"
        "Identify non-compliant claims and propose edits.\n"
        "Return JSON like { 'edits': [...], 'all_clear': true|false }"
    ),
)

market_research_agent = LlmAgent(
    model=LiteLlm(model="claude-3-7-sonnet-20250219"),
    name="market_research_agent",
    description="Designs quick KOL feedback plan and survey",
    instruction=(
        "Design a lightweight research plan to validate A vs B with 10 KOLs.\n"
        "Return JSON with { 'survey': {...}, 'metrics': ['notes','score','go_no_go'] }"
    ),
)


def make_kol_agent(kol_id: int) -> LlmAgent:
    return LlmAgent(
        model=LiteLlm(model="claude-3-7-sonnet-20250219"),
        name=f"kol_{kol_id}",
        description="Key opinion leader providing structured feedback",
        instruction=(
            "You are a KOL. You're assigned either variant A or B in pipeline.meta['ab_assignment'][name].\n"
            "Provide structured feedback: { 'notes': str, 'score': 1-10, 'go_no_go': 'go'|'no-go' }"
        ),
    )


aggregator_agent = LlmAgent(
    model=LiteLlm(model="claude-3-7-sonnet-20250219"),
    name="aggregator_agent",
    description="Aggregates KOL feedback and recommends A or B",
    instruction=(
        "Aggregate KOL feedback in inputs['kol_feedback'].\n"
        "Compute average scores per variant and recommend 'A' or 'B'.\n"
        "Return JSON { 'summary': str, 'avg_scores': {'A': num, 'B': num}, 'recommendation': 'A'|'B' }"
    ),
)


# -----------------------------
# Tools and helpers
# -----------------------------

def randomize_ab_assignment(pipeline: Dict[str, Any], kol_names: List[str]) -> Dict[str, str]:
    assignment = {}
    for name in kol_names:
        assignment[name] = random.choice(["A", "B"])
    pipeline.setdefault("meta", {})["ab_assignment"] = assignment
    _print_header("A/B assignment for KOLs")
    for k, v in assignment.items():
        print(f"  {k}: {v}")
    return assignment


def deploy_markdown(pipeline: Dict[str, Any], output_path: str = "deploy_output.md") -> str:
    brief = pipeline.get("inputs", {}).get("brief", "")
    rec = pipeline.get("state", {}).get("aggregator", {}).get("recommendation", "")
    with open(output_path, "w") as f:
        f.write(f"# Campaign Deployment\n\n")
        f.write(f"## Recommendation: {rec}\n\n")
        f.write(f"## Brief\n\n{brief}\n")
    print(f"Deployed to {output_path}")
    return output_path


# -----------------------------
# Pipeline composition
# -----------------------------

def build_marketing_pipeline() -> SequentialAgent:
    # 1) CEO reads brief
    # 2) Copywriter-Legal loop until all_clear
    copywriter_legal_sequence = SequentialAgent(
        name="copywriter_legal_sequence",
        description="Copywriter then Legal",
        sub_agents=[copywriter_agent, legal_agent],
    )

    def terminate_on_all_clear(pipeline: Dict[str, Any]) -> bool:
        last_legal = pipeline.get("state", {}).get("legal_agent", {})
        all_clear = bool(last_legal.get("all_clear") or last_legal.get("output", {}).get("all_clear"))
        print(f"Loop termination check – all_clear={all_clear}")
        return all_clear

    copywriter_legal_loop = LoopAgent(
        name="copywriter_legal_loop",
        description="Iterate copywriter and legal until all_clear",
        agent=copywriter_legal_sequence,
        should_terminate=terminate_on_all_clear,
        max_iterations=6,
    )

    # 3) Market research + Parallel KOLs
    kol_agents = [make_kol_agent(i) for i in range(1, 11)]
    kol_parallel = ParallelAgent(
        name="kol_parallel",
        description="Run 10 KOLs in parallel",
        sub_agents=kol_agents,
    )

    # 4) Aggregator
    # 5) Copywriter & Legal revise again (reuse loop)
    # 6) CEO final sign-off
    pipeline = SequentialAgent(
        name="marketing_agency_pipeline",
        description="End-to-end marketing agency pipeline",
        sub_agents=[
            ceo_agent,
            copywriter_legal_loop,
            market_research_agent,
            kol_parallel,
            aggregator_agent,
            copywriter_legal_loop,
            ceo_agent,
        ],
    )

    return pipeline


# For convenience: a root_agent that callers can import
root_agent = build_marketing_pipeline()


