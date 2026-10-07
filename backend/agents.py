from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI
from pydantic import BaseModel
from typing import Callable, Optional
from aapi import OPEN_AI_API
from langchain_core.messages import HumanMessage, SystemMessage
from schemas import *
from prompts import *
from generated_code_validation import validate_generated_source


class Agents:
    """Agent implementations for Module 1.

    This class contains agent logic only. Workflow orchestration, routing,
    persistence, and execution infrastructure belong in separate layers.
    """

    def __init__(self, llm1: ChatOpenAI, llm2: ChatOpenAI) -> None:
        """Initialize agents with one reusable, injected LLM instance."""
        self.llm1 = llm1
        self.llm2 = llm2

    def requirements_agent(self, user_requirements: str) -> str:
        """Convert raw user requirements into a structured specification."""
        return self._invoke_text_llm2(
            REQUIREMENTS_SYSTEM_PROMPT,
            user_requirements,
        )

    def architecture_agent(self, requirements: str) -> str:
        """Design an architecture from the structured requirements."""
        return self._invoke_text_llm1(
            ARCHITECTURE_SYSTEM_PROMPT,
            f"Requirements:\n{requirements}",
        )

    def boilerplate_agent(self, requirements: str, architecture: str) -> str:
        """Generate a project skeleton from requirements and architecture."""
        return self._invoke_text_llm1(
            BOILERPLATE_SYSTEM_PROMPT,
            (f"Requirements:\n{requirements}\n\n" f"Architecture:\n{architecture}"),
        )

    def code_writing_agent(
        self,
        requirements: str,
        architecture: str,
        boilerplate: str,
        existing_code: str,
        on_token: Optional[Callable[[str], None]] = None,
        on_file_start: Optional[Callable[[str], None]] = None,
        on_file_end: Optional[Callable[[str], None]] = None,
    ) -> str:
        """Generate a Python backend first, then a separate frontend file."""
        prompt = (
            f"Requirements:\n{requirements}\n\n"
            f"Boilerplate:\n{boilerplate}\n\n"
            f"Existing generated code/context:\n{existing_code}\n\n"
        )
        if on_file_start:
            on_file_start("backend")
        backend_code = self._stream_text_llm1(
            CODE_WRITING_SYSTEM_PROMPT,
            prompt,
            on_token,
        )
        if on_file_end:
            validate_generated_source(backend_code, "backend")
            on_file_end("backend")

        if on_file_start:
            on_file_start("frontend")
        frontend_code = self._stream_text_llm1(
            FRONTEND_CODE_WRITING_SYSTEM_PROMPT,
            (
                f"Requirements:\n{requirements}\n\n"
                f"Architecture:\n{architecture}\n\n"
                f"Frontend file contract:\n{boilerplate}\n\n"
                f"Backend file that the frontend must call:\n{backend_code}\n\n"
                f"Existing generated context:\n{existing_code}\n"
            ),
            on_token,
        )
        if on_file_end:
            validate_generated_source(frontend_code, "frontend")
            on_file_end("frontend")

        return backend_code + "\n\n" + frontend_code

    def analysis_agent(
        self,
        generated_code: str,
    ) -> ReviewResult:
        """Analyse the generated code and make a readme file for the code."""
        prompt = f"Generated project files:\n{generated_code}"
        return self._invoke_structured(ANALYSIS_SYSTEM_PROMPT, prompt, ReviewResult)

    def _invoke_text_llm2(self, system_prompt: str, user_prompt: str) -> str:
        """Invoke the LLM and normalize its text response."""
        try:
            response = self.llm2.invoke(
                [
                    SystemMessage(content=system_prompt),
                    HumanMessage(content=user_prompt),
                ]
            )
            content = response.content

            if isinstance(content, str):
                return content.strip()

            return "".join(
                block.get("text", "") for block in content if isinstance(block, dict)
            ).strip()
        except Exception as exc:
            raise RuntimeError("LLM text generation failed.") from exc

    def _invoke_text_llm1(self, system_prompt: str, user_prompt: str) -> str:
        """Invoke the LLM and normalize its text response."""
        try:
            response = self.llm2.invoke(
                [
                    SystemMessage(content=system_prompt),
                    HumanMessage(content=user_prompt),
                ]
            )
            content = response.content

            if isinstance(content, str):
                return content.strip()

            return "".join(
                block.get("text", "") for block in content if isinstance(block, dict)
            ).strip()
        except Exception as exc:
            raise RuntimeError("LLM text generation failed.") from exc

    def _stream_text_llm1(
        self,
        system_prompt: str,
        user_prompt: str,
        on_token: Optional[Callable[[str], None]],
    ) -> str:
        """Collect a complete response while forwarding chunks immediately."""
        try:
            chunks: list[str] = []
            for response in self.llm2.stream(
                [
                    SystemMessage(content=system_prompt),
                    HumanMessage(content=user_prompt),
                ]
            ):
                content = response.content
                if isinstance(content, str):
                    text = content
                else:
                    text = "".join(
                        block.get("text", "")
                        for block in content
                        if isinstance(block, dict)
                    )
                if text:
                    chunks.append(text)
                    if on_token is not None:
                        on_token(text)
            return "".join(chunks).strip()
        except Exception as exc:
            raise RuntimeError("LLM streaming generation failed.") from exc

    def _invoke_structured(
        self,
        system_prompt: str,
        user_prompt: str,
        schema: type[BaseModel],
    ) -> BaseModel:
        """Invoke the LLM with a Pydantic structured-output schema."""
        try:
            structured_llm = self.llm2.with_structured_output(schema)
            return structured_llm.invoke(
                [
                    SystemMessage(content=system_prompt),
                    HumanMessage(content=user_prompt),
                ]
            )
        except Exception as exc:
            raise RuntimeError(
                f"Structured LLM generation failed for {schema.__name__}."
            ) from exc
