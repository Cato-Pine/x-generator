import anthropic
from typing import Optional


class AnthropicClient:
    """Wrapper for Anthropic API (Claude models)"""

    def __init__(self, api_key: str, model: str = "claude-3-5-sonnet-20241022"):
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = model

    def generate(
        self,
        prompt: str,
        max_tokens: int = 2000,
        temperature: float = 0.7,
        system: Optional[str] = None,
    ) -> str:
        """Generate content using Claude"""
        try:
            kwargs = {
                "model": self.model,
                "max_tokens": max_tokens,
                "messages": [{"role": "user", "content": prompt}],
            }

            if system:
                kwargs["system"] = system

            if temperature is not None:
                kwargs["temperature"] = temperature

            response = self.client.messages.create(**kwargs)

            return response.content[0].text
        except Exception as e:
            raise Exception(f"Error calling Anthropic API: {str(e)}")

    def generate_streaming(
        self,
        prompt: str,
        max_tokens: int = 2000,
        temperature: float = 0.7,
        system: Optional[str] = None,
    ):
        """Generate content using Claude with streaming"""
        try:
            kwargs = {
                "model": self.model,
                "max_tokens": max_tokens,
                "messages": [{"role": "user", "content": prompt}],
            }

            if system:
                kwargs["system"] = system

            if temperature is not None:
                kwargs["temperature"] = temperature

            with self.client.messages.stream(**kwargs) as stream:
                for text in stream.text_stream:
                    yield text
        except Exception as e:
            raise Exception(f"Error calling Anthropic API: {str(e)}")
