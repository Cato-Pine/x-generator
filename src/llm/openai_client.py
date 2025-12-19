import os
from openai import OpenAI
from typing import Optional


class OpenAIClient:
    """Wrapper for OpenAI API (GPT-4 Turbo, embeddings)"""

    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4-turbo"):
        api_key = api_key or os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set")
        self.client = OpenAI(api_key=api_key)
        self.model = model
        self.embedding_model = "text-embedding-3-small"

    def generate(
        self,
        prompt: str,
        max_tokens: int = 2000,
        temperature: float = 0.7,
        system: Optional[str] = None,
    ) -> str:
        """Generate content using GPT-4 Turbo"""
        try:
            messages = []

            if system:
                messages.append({"role": "system", "content": system})

            messages.append({"role": "user", "content": prompt})

            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
            )

            return response.choices[0].message.content
        except Exception as e:
            raise Exception(f"Error calling OpenAI API: {str(e)}")

    def generate_streaming(
        self,
        prompt: str,
        max_tokens: int = 2000,
        temperature: float = 0.7,
        system: Optional[str] = None,
    ):
        """Generate content using GPT-4 Turbo with streaming"""
        try:
            messages = []

            if system:
                messages.append({"role": "system", "content": system})

            messages.append({"role": "user", "content": prompt})

            with self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
                stream=True,
            ) as response:
                for chunk in response:
                    if chunk.choices[0].delta.content:
                        yield chunk.choices[0].delta.content
        except Exception as e:
            raise Exception(f"Error calling OpenAI API: {str(e)}")

    def get_embedding(self, text: str) -> list:
        """Get embedding for text"""
        try:
            response = self.client.embeddings.create(
                model=self.embedding_model,
                input=text,
            )
            return response.data[0].embedding
        except Exception as e:
            raise Exception(f"Error getting embedding: {str(e)}")
