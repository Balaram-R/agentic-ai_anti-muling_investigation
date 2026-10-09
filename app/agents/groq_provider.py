from groq import Groq


class GroqLLMProvider:
    def __init__(self, api_key: str, model: str):
        self.client = Groq(api_key=api_key)
        self.model = model

    def generate(
        self,
        system_prompt: str,
        user_prompt: str,
    ) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": system_prompt,
                },
                {
                    "role": "user",
                    "content": user_prompt,
                },
            ],
            temperature=0,
            response_format={"type": "json_object"},
        )

        content = response.choices[0].message.content

        if not content:
            raise ValueError("Groq returned an empty response")

        return content