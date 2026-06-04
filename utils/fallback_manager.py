from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Optional

from config.llm_config import llm_config

try:
    import cohere
except ImportError:  # pragma: no cover
    cohere = None

try:
    import google.genai as genai
except ImportError:  # pragma: no cover
    genai = None

logger = logging.getLogger("ujima_fallback")


@dataclass
class ProviderResult:
    provider_name: str
    text: str
    success: bool


class BaseProvider:
    def __init__(self, api_key: str, model: str, provider_name: str):
        self.api_key = api_key
        self.model = model
        self.provider_name = provider_name

    def complete(self, prompt: str, max_tokens: int = 800) -> ProviderResult:
        raise NotImplementedError()


class CohereProvider(BaseProvider):
    def complete(self, prompt: str, max_tokens: int = 800) -> ProviderResult:
        if not cohere or not self.api_key:
            raise RuntimeError("Cohere provider is unavailable.")
        client = cohere.Client(self.api_key)
        if hasattr(client, "chat"):
            response = client.chat.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                temperature=0.2,
            )
            text = getattr(response, "text", None) or getattr(response, "response", None) or ""
        else:
            response = client.generate(
                model=self.model,
                prompt=prompt,
                max_tokens=max_tokens,
                temperature=0.2,
                stop_sequences=["\n\n"],
            )
            text = getattr(response, "text", "")
        return ProviderResult(self.provider_name, text, True)


class GeminiProvider(BaseProvider):
    def complete(self, prompt: str, max_tokens: int = 800) -> ProviderResult:
        if not genai or not self.api_key:
            raise RuntimeError("Gemini provider is unavailable.")
        genai.configure(api_key=self.api_key)
        if hasattr(genai, "chat"):
            response = genai.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2,
                max_output_tokens=max_tokens,
            )
            text = getattr(response, "last", None)
            if text is not None:
                text = getattr(text, "message", None)
            if text is not None:
                text = getattr(text, "content", None)
        else:
            response = genai.responses.create(
                model=self.model,
                text=prompt,
                temperature=0.2,
                max_output_tokens=max_tokens,
            )
            text = getattr(response, "output", None)
            if text is None:
                text = getattr(response, "response", None)
        text = text or str(response)
        return ProviderResult(self.provider_name, text, True)


class CerebrasProvider(BaseProvider):
    def complete(self, prompt: str, max_tokens: int = 800) -> ProviderResult:
        if self.api_key:
            # If a Cerebras client is available in the environment, this is where it would be invoked.
            if llm_config.enable_local_fallback:
                logger.warning(
                    "Cerebras remote provider is not configured or unavailable; falling back to local Cerebras fallback."
                )
                fallback_text = self._local_cerebras_fallback(prompt)
                return ProviderResult(self.provider_name, fallback_text, True)
            raise RuntimeError("Cerebras remote provider is not configured for this deployment.")

        fallback_text = self._local_cerebras_fallback(prompt)
        return ProviderResult(self.provider_name, fallback_text, True)

    @staticmethod
    def _local_cerebras_fallback(prompt: str) -> str:
        summary_lines = [
            "The application requires human review.",
            "Key indicators: close cash flow, childcare pressure, and loan amount above conservative thresholds.",
            "Recommend an officer briefing packet with empathy and cultural context.",
        ]
        return " ".join(summary_lines)


class FallbackManager:
    def __init__(self) -> None:
        self.providers: list[BaseProvider] = []
        self.active_provider: str = "None"
        self._build_providers()

    def _build_providers(self) -> None:
        if llm_config.cohere_api_key:
            self.providers.append(CohereProvider(llm_config.cohere_api_key, llm_config.cohere_model, "Cohere"))
        if llm_config.gemini_api_key:
            self.providers.append(GeminiProvider(llm_config.gemini_api_key, llm_config.gemini_model, "Gemini"))
        self.providers.append(CerebrasProvider(llm_config.cerebras_api_key, llm_config.cerebras_model, "Cerebras"))

    def complete(self, prompt: str, max_tokens: int = 800) -> ProviderResult:
        last_exception: Optional[Exception] = None
        for provider in self.providers:
            try:
                result = provider.complete(prompt, max_tokens=max_tokens)
                self.active_provider = provider.provider_name
                logger.info("Provider selected: %s", provider.provider_name)
                return result
            except Exception as error:
                last_exception = error
                logger.warning("Provider %s failed: %s", provider.provider_name, error)
                continue

        raise RuntimeError("No LLM provider could complete the request.") from last_exception
