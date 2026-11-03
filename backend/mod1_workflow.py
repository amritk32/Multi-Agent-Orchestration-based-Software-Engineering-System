import logging

from agents import Agents, Module1
from langgraph.graph import StateGraph, START, END
from events import emit_event
from syntax_analysis import SyntaxAnalyzer
from requirements_validation import validate_requirements

logger = logging.getLogger(__name__)


class Module1Workflow:

    def __init__(self, agents: Agents):
        self.agents = agents
        self.syntax_analyzer = SyntaxAnalyzer()
        self.graph = self._build_graph()

    def requirements_node(self, state: Module1):
        validation_error = validate_requirements(state.requirements)
        if validation_error:
            raise ValueError(validation_error)
        logger.info("Requirements Agent started")
        emit_event({"type": "agent_start", "agent": "requirements"})
        try:
            state.requirements = self.agents.requirements_agent(state.requirements)
            logger.info("Requirements Agent finished")
            emit_event({"type": "agent_end", "agent": "requirements"})
        except Exception as e:
            logger.exception("Requirements Agent failed")
            raise
        return state

    def syntax_analysis_node(self, state: Module1):
        logger.info("Syntax Analysis started")
        emit_event({"type": "agent_start", "agent": "syntax_analysis"})
        state.syntax_valid = self.syntax_analyzer.analyze(state.backend_code)
        state.syntax_error = self.syntax_analyzer.last_error
        emit_event(
            {
                "type": "agent_end",
                "agent": "syntax_analysis",
                "syntax_valid": state.syntax_valid,
                "syntax_error": state.syntax_error,
            }
        )
        return state

    def architecture_node(self, state: Module1):
        logger.info("Architecture Agent started")
        emit_event({"type": "agent_start", "agent": "architecture"})
        try:
            state.architecture = self.agents.architecture_agent(state.requirements)
            logger.info("Architecture Agent finished")
            emit_event({"type": "agent_end", "agent": "architecture"})
        except Exception as e:
            logger.exception("Architecture Agent failed")
            raise
        return state

    def boilerplate_node(self, state: Module1):
        logger.info("Boilerplate Agent started")
        emit_event({"type": "agent_start", "agent": "boilerplate"})
        try:
            state.boilerplate = self.agents.boilerplate_agent(
                state.requirements,
                state.architecture,
            )
            logger.info("Boilerplate Agent finished")
            emit_event({"type": "agent_end", "agent": "boilerplate"})
        except Exception as e:
            logger.exception("Boilerplate Agent failed")
            raise
        return state

    def code_writing_node(self, state: Module1):
        logger.info("Code Writing Agent started")
        emit_event({"type": "agent_start", "agent": "code_writing"})
        try:
            current_file = "backend"
            backend_parts: list[str] = []
            frontend_parts: list[str] = []

            def on_file_start(file_name: str):
                nonlocal current_file
                current_file = file_name
                emit_event({"type": "file_start", "file": file_name})

            def on_token(token: str):
                if current_file == "backend":
                    backend_parts.append(token)
                else:
                    frontend_parts.append(token)
                emit_event({"type": "code_token", "token": token, "file": current_file})

            state.code = self.agents.code_writing_agent(
                requirements=state.requirements,
                architecture=state.architecture,
                boilerplate=state.boilerplate,
                existing_code=state.code,
                on_token=on_token,
                on_file_start=on_file_start,
                on_file_end=lambda file_name: emit_event(
                    {"type": "file_end", "file": file_name}
                ),
            )
            state.backend_code = "".join(backend_parts).strip()
            state.frontend_code = "".join(frontend_parts).strip()

            logger.info("Code Writing Agent finished")
            emit_event({"type": "agent_end", "agent": "code_writing"})
        except Exception as e:
            logger.exception("Code Writing Agent failed")
            raise

        return state

    def analysis_node(self, state: Module1):
        logger.info("Analysis Agent started")
        emit_event({"type": "agent_start", "agent": "analysis"})
        try:
            result = self.agents.analysis_agent(
                generated_code=state.code,
            )

            state.review_result = result.model_dump()
            state.report = result.final_readme

            logger.info("Analysis Agent finished")
            emit_event({"type": "agent_end", "agent": "analysis"})
        except Exception as e:
            logger.exception("Analysis Agent failed")
            raise

        return state

    def _build_graph(self):

        workflow = StateGraph(Module1)

        workflow.add_node(
            "requirements",
            self.requirements_node,
        )

        workflow.add_node(
            "architecture",
            self.architecture_node,
        )

        workflow.add_node(
            "boilerplate",
            self.boilerplate_node,
        )

        workflow.add_node(
            "code_writing",
            self.code_writing_node,
        )

        workflow.add_node(
            "analysis",
            self.analysis_node,
        )

        workflow.add_node(
            "syntax_analysis",
            self.syntax_analysis_node,
        )

        workflow.add_edge(START, "requirements")

        workflow.add_edge(
            "requirements",
            "architecture",
        )

        workflow.add_edge(
            "architecture",
            "boilerplate",
        )

        workflow.add_edge(
            "boilerplate",
            "code_writing",
        )

        workflow.add_edge(
            "code_writing",
            "syntax_analysis",
        )

        workflow.add_edge(
            "syntax_analysis",
            "analysis",
        )

        workflow.add_edge("analysis", END)

        return workflow.compile()
