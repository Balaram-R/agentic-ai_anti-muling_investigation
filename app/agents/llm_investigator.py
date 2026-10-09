import json

from app.agents.analysis_schema import AMLAnalysis
from app.agents.investigator_prompt import (
    SYSTEM_PROMPT,
    build_investigator_prompt,
)
from app.agents.schemas import InvestigatorResult


class LLMInvestigator:
    """
    LLM-based investigator.

    The investigator is provider-agnostic.
    The provider handles the actual LLM call.
    """

    def __init__(self, provider):
        self.provider = provider

    def analyze(
        self,
        result: InvestigatorResult,
    ) -> AMLAnalysis:

        user_prompt = build_investigator_prompt(result)

        raw_response = self.provider.generate(
            system_prompt=SYSTEM_PROMPT,
            user_prompt=user_prompt,
        )

        if not raw_response:
            raise ValueError("LLM provider returned an empty response")

        print("\n========== RAW LLM RESPONSE ==========")
        print(raw_response)
        print("========== END RAW LLM RESPONSE ==========\n")

        try:
            data = json.loads(raw_response)
        except json.JSONDecodeError as exc:
            raise ValueError(
                "LLM provider returned invalid JSON"
            ) from exc

        return AMLAnalysis.model_validate(data)