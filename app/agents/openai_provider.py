import os

from dotenv import load_dotenv
from openai import OpenAI, RateLimitError, APIError

load_dotenv()

from app.agents.analysis_schema import AMLAnalysis


class LLMProviderError(RuntimeError):
    pass


class OpenAIProvider:

    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY")
        self.model = os.getenv(
            "GROQ_MODEL",
            "openai/gpt-oss-120b",
        )

        if not self.api_key:
            raise LLMProviderError(
                "GROQ_API_KEY is not configured."
            )

        self.client = OpenAI(
            api_key=self.api_key,
            base_url="https://api.groq.com/openai/v1",
        )

    def analyze(
        self,
        system_prompt: str,
        user_prompt: str,
    ) -> AMLAnalysis:

        try:
            response = self.client.responses.parse(
                model=self.model,
                instructions=system_prompt,
                input=user_prompt,
                text_format=AMLAnalysis,
            )

            return response.output_parsed

        except RateLimitError as exc:
            raise LLMProviderError(
                "Groq provider quota/rate limit is unavailable."
            ) from exc

        except APIError as exc:
            raise LLMProviderError(
                f"Groq provider API error: {exc}"
            ) from exc