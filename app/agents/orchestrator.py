from app.agents.fallback_investigator import DeterministicInvestigator
from app.agents.investigator import InvestigatorAgent
from app.agents.critic import InvestigationCritic

from app.aml.case_assessment import AMLCaseAssessmentEngine
from app.aml.recommendation import AMLRecommendationEngine

from app.policy.service import PolicyService

from app.agents.llm_investigator import LLMInvestigator


class InvestigationOrchestrator:

    def __init__(
        self,
        investigator=None,
        reasoning_engine=None,
        assessment_engine=None,
        recommendation_engine=None,
        policy_service=None,
        critic=None,
        llm_provider=None,
    ):
        self.investigator = investigator or InvestigatorAgent()

        self.reasoning_engine = (
            LLMInvestigator(llm_provider)
            if llm_provider
            else DeterministicInvestigator()
        )

        self.assessment_engine = (
            assessment_engine or AMLCaseAssessmentEngine()
        )

        self.recommendation_engine = (
            recommendation_engine or AMLRecommendationEngine()
        )

        self.policy_service = policy_service or PolicyService()

        self.critic = critic or InvestigationCritic()

    def run(
        self,
        db,
        alert_id: str,
        investigation_id: str | None = None,
    ):
        # 1. Gather investigation evidence
        evidence = self.investigator.investigate(
            db=db,
            alert_id=alert_id,
            investigation_id=investigation_id,
        )

        # 2. Analyze the evidence
        analysis = self.reasoning_engine.analyze(evidence)

        findings = analysis.findings

        # 3. Assess the findings
        assessment = self.assessment_engine.assess(findings)

        # 4. Generate a recommendation
        recommendation = self.recommendation_engine.recommend(
            assessment
        )

        # 5. Retrieve relevant AML policy
        finding_codes = [
            finding.code
            for finding in findings
        ]

        policy_evidence = self.policy_service.retrieve_for_findings(
            finding_codes=finding_codes,
        )

        # 6. Critic / governance check
        critic_result = self.critic.review(
            findings=findings,
            policy_evidence=policy_evidence,
            recommendation=recommendation,
        )

        return {
            "alert_id": alert_id,
            "evidence": evidence,
            "analysis": analysis,
            "assessment": assessment,
            "recommendation": recommendation,
            "policy_evidence": policy_evidence,
            "critic": critic_result,
        }