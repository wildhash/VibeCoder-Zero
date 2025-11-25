"""LLM client for OpenAI and Anthropic integration."""

from typing import Literal, Optional, Dict, Any

Provider = Literal["openai", "anthropic"]
Mode = Literal["plan", "code", "reflect"]


class LLMClient:
    def __init__(self, provider: Provider, plan_model: str, code_model: str, reflect_model: Optional[str] = None) -> None:
        """
        Configure the LLMClient with a provider and model names and initialize the underlying provider client.
        
        Parameters:
            provider (Provider): The provider identifier, either "openai" or "anthropic".
            plan_model (str): Model name to use for planning tasks.
            code_model (str): Model name to use for code generation tasks.
            reflect_model (Optional[str]): Model name to use for reflection tasks; when omitted, defaults to `plan_model`.
        
        Raises:
            ValueError: If the configured provider is unknown when initializing the underlying client.
        """
        self.provider = provider
        self.plan_model = plan_model
        self.code_model = code_model
        self.reflect_model = reflect_model or plan_model
        self._init_clients()

    def _init_clients(self) -> None:
        """
        Initialize and store the underlying provider client based on self.provider.
        
        This sets self._client to an instance of the selected provider's client for "openai" or "anthropic". If the provider value is not recognized, a ValueError is raised.
        
        Raises:
            ValueError: If self.provider is not "openai" or "anthropic".
        """
        if self.provider == "openai":
            import openai
            self._client = openai.Client()
        elif self.provider == "anthropic":
            import anthropic
            self._client = anthropic.Anthropic()
        else:
            raise ValueError(f"Unknown provider: {self.provider}")

    def _choose_model(self, mode: Mode) -> str:
        """
        Selects the model name corresponding to the given operation mode.
        
        Parameters:
        	mode (Mode): Operation mode that determines which model to use. Recognized values are "plan", "code", and "reflect".
        
        Returns:
        	model_name (str): The selected model name; falls back to `plan_model` if the mode is unrecognized.
        """
        if mode == "plan": return self.plan_model
        if mode == "code": return self.code_model
        if mode == "reflect": return self.reflect_model
        return self.plan_model

    def _call_openai(self, model: str, system: str, user: str) -> str:
        """
        Send a chat completion request using the OpenAI client and return the assistant's reply content.
        
        Parameters:
            model (str): Model name to use for the completion.
            system (str): System-role message that defines assistant behavior.
            user (str): User-role message containing the user's prompt.
        
        Returns:
            str: The assistant's response text, or an empty string if the response content is missing.
        """
        resp = self._client.chat.completions.create(
            model=model,
            messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
        )
        return resp.choices[0].message.content or ""

    def _call_anthropic(self, model: str, system: str, user: str) -> str:
        """
        Send a chat request to the Anthropic client and return the concatenated text from the response content blocks.
        
        Parameters:
            model (str): The Anthropic model name to use.
            system (str): System-level instructions to guide model behavior.
            user (str): The user message content.
        
        Returns:
            str: Concatenated text from all response content blocks; empty string if no text blocks are present.
        """
        resp = self._client.messages.create(
            model=model,
            max_tokens=2048,
            system=system,
            messages=[{"role": "user", "content": user}],
        )
        return "".join(getattr(block, "text", "") for block in resp.content)

    def _call(self, mode: Mode, system: str, user: str) -> str:
        """
        Dispatches the request to the configured provider using the model chosen for the given mode.
        
        Parameters:
        	mode (Mode): Operation mode used to select which model to call (e.g., "plan", "code", "reflect").
        	system (str): System prompt describing the assistant's role and constraints.
        	user (str): User prompt or content to send to the model.
        
        Returns:
        	response (str): The provider's text response (empty string if provider returned no content).
        
        Raises:
        	RuntimeError: If the configured provider is not supported.
        """
        model = self._choose_model(mode)
        if self.provider == "openai": return self._call_openai(model, system, user)
        elif self.provider == "anthropic": return self._call_anthropic(model, system, user)
        raise RuntimeError("Unsupported provider")

    def generate_code(self, prompt: str, context: Optional[Dict[str, Any]] = None) -> str:
        """
        Generate code based on a prompt and optional project context.
        
        Parameters:
            prompt (str): The user's instruction or request describing the code to generate.
            context (Optional[Dict[str, Any]]): Optional project-specific information that will be added to the system prompt to provide additional context.
        
        Returns:
            generated_code (str): The code produced by the language model as plain text.
        """
        system = "You are an expert software engineer. Output only code unless asked otherwise."
        if context: system += "\n\nProject context:\n" + str(context)
        return self._call("code", system, prompt)

    def analyze_error(self, stderr: str, context: Optional[Dict[str, Any]] = None) -> str:
        """
        Analyze a runtime error and propose concrete code changes or shell commands to fix it.
        
        Parameters:
            stderr (str): The error message or stack trace to analyze.
            context (Optional[Dict[str, Any]]): Optional project or environment context to assist diagnosis; omitted or empty dict if not provided.
        
        Returns:
            str: A text response containing specific suggestions, code snippets, or commands to resolve the provided error.
        """
        system = "You are a debugging assistant. Given an error and context, propose specific code or command fixes."
        user = f"Error:\n{stderr}\n\nContext:\n{context or {}}"
        return self._call("reflect", system, user)

    def plan_next_steps(self, state_summary: str) -> str:
        """
        Propose 3–5 concrete next steps for the project, each including recommended commands, based on the provided state summary.
        
        Parameters:
            state_summary (str): A concise description of the current project state, constraints, or recent progress to inform planning.
        
        Returns:
            str: A textual plan containing 3–5 numbered, actionable next steps. Each step includes a brief rationale and any shell commands or specific commands to run.
        """
        system = "You are a project architect. Given the current state, propose 3–5 concrete next steps with commands."
        return self._call("plan", system, state_summary)