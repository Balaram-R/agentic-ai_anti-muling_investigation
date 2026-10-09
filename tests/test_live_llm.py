from app.agents.analysis_schema import AMLAnalysis
from app.agents.investigator import InvestigatorAgent
from app.agents.llm_investigator import LLMInvestigator
from app.agents.openai_provider import OpenAIProvider
from app.db.session import SessionLocal


def test_live_llm_investigation():
    db = SessionLocal()

    try:
        investigator = InvestigatorAgent()

        evidence = investigator.investigate(
            db=db,
            alert_id="536c3ffe-cee4-47a5-b8ff-a76c5559c917",
        )

        llm_investigator = LLMInvestigator(
            provider=OpenAIProvider()
        )

        analysis = llm_investigator.analyze(evidence)

        assert isinstance(analysis, AMLAnalysis)

        print("\n--- LIVE AML ANALYSIS ---")
        print(analysis.model_dump_json(indent=2))

    finally:
        db.close()