"""LLM client for OpenAI and Anthropic integration."""

from typing import Literal, Optional, Dict, Any

Provider = Literal["openai", "anthropic"]
Mode = Literal["plan", "code", "reflect"]


class LLMClient:
    def __init__(self, provider: Provider, plan_model: str, code_model: str, reflect_model: Optional[str] = None) -> None:
        self.provider = provider
        self.plan_model = plan_model
        self.code_model = code_model
        self.reflect_model = reflect_model or plan_model
        self._init_clients()

    def _init_clients(self) -> None:
        if self.provider == "openai":
            import openai
            self._client = openai.Client()
        elif self.provider == "anthropic":
            import anthropic
            self._client = anthropic.Anthropic()
        else:
            raise ValueError(f"Unknown provider: {self.provider}")

    def _choose_model(self, mode: Mode) -> str:
        if mode == "plan": return self.plan_model
        if mode == "code": return self.code_model
        if mode == "reflect": return self.reflect_model
        return self.plan_model

    def _call_openai(self, model: str, system: str, user: str) -> str:
        resp = self._client.chat.completions.create(
            model=model,
            messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
        )
        return resp.choices[0].message.content or ""

    def _call_anthropic(self, model: str, system: str, user: str) -> str:
        resp = self._client.messages.create(
            model=model,
            max_tokens=2048,
            system=system,
            messages=[{"role": "user", "content": user}],
        )
        return "".join(getattr(block, "text", "") for block in resp.content)

    def _call(self, mode: Mode, system: str, user: str) -> str:
        model = self._choose_model(mode)
        if self.provider == "openai": return self._call_openai(model, system, user)
        elif self.provider == "anthropic": return self._call_anthropic(model, system, user)
        raise RuntimeError("Unsupported provider")

    def generate_code(self, prompt: str, context: Optional[Dict[str, Any]] = None) -> str:
        system = "You are an expert software engineer. Output only code unless asked otherwise."
        if context: system += "\n\nProject context:\n" + str(context)
        return self._call("code", system, prompt)

    def analyze_error(self, stderr: str, context: Optional[Dict[str, Any]] = None) -> str:
        system = "You are a debugging assistant. Given an error and context, propose specific code or command fixes."
        user = f"Error:\n{stderr}\n\nContext:\n{context or {}}"
        return self._call("reflect", system, user)

    def plan_next_steps(self, state_summary: str) -> str:
        system = "You are a project architect. Given the current state, propose 3–5 concrete next steps with commands."
        return self._call("plan", system, state_summary)
