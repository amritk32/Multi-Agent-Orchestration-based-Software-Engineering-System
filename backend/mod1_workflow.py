import logging

from agents import Agents, Module1
from langgraph.graph import StateGraph, START, END
from events import ProjectEventManager
from syntax_analysis import SyntaxAnalyzer
from requirements_validation import validate_requirements

logger = logging.getLogger(__name__)


class Module1Workflow:

    def __init__(self, agents: Agents, event_manager: ProjectEventManager):
        self.agents = agents
        self.event_manager = event_manager
        self.syntax_analyzer = SyntaxAnalyzer()
        self.graph = self._build_graph()

    def requirements_node(self, state: Module1):
        validation_error = validate_requirements(state.requirements)
        if validation_error:
            raise ValueError(validation_error)
        # Added print statement before logging
        print(f"Requirements Agent started project_id={state.project_id}")
        logger.info("Requirements Agent started project_id=%s", state.project_id)
        self.event_manager.publish(
            state.project_id, {"type": "agent_start", "agent": "requirements"}
        )
        try:
            state.requirements = self.agents.requirements_agent(state.requirements)
            # Added print statement before logging
            print(f"Requirements Agent finished project_id={state.project_id}")
            logger.info("Requirements Agent finished project_id=%s", state.project_id)
            self.event_manager.publish(
                state.project_id, {"type": "agent_end", "agent": "requirements"}
            )
        except Exception as e:
            # Added Print statement before logging
            print(f"Requirements Agent failed project_id={state.project_id}")
            logger.exception(
                "Requirements Agent failed project_id=%s", state.project_id
            )
            raise
        return state

    def syntax_analysis_node(self, state: Module1):
        print(f"Syntax Analysis started project_id={state.project_id}")
        logger.info("Syntax Analysis started project_id=%s", state.project_id)
        self.event_manager.publish(
            state.project_id, {"type": "agent_start", "agent": "syntax_analysis"}
        )
        state.syntax_valid = self.syntax_analyzer.analyze(state.backend_code)
        state.syntax_error = self.syntax_analyzer.last_error
        print(f"Syntax Analysis finished project_id={state.project_id}")
        logger.info("Syntax Analysis finished project_id=%s", state.project_id)
        self.event_manager.publish(
            state.project_id,
            {
                "type": "agent_end",
                "agent": "syntax_analysis",
                "syntax_valid": state.syntax_valid,
                "syntax_error": state.syntax_error,
            },
        )
        return state

    def architecture_node(self, state: Module1):
        print(f"Architecture Agent started project_id={state.project_id}")
        logger.info("Architecture Agent started project_id=%s", state.project_id)
        self.event_manager.publish(
            state.project_id, {"type": "agent_start", "agent": "architecture"}
        )
        try:
            state.architecture = self.agents.architecture_agent(state.requirements)
            print(f"Architecture Agent finished project_id={state.project_id}")
            logger.info("Architecture Agent finished project_id=%s", state.project_id)
            self.event_manager.publish(
                state.project_id, {"type": "agent_end", "agent": "architecture"}
            )
        except Exception as e:
            print(f"Architecture Agent failed project_id={state.project_id}")
            logger.exception(
                "Architecture Agent failed project_id=%s", state.project_id
            )
            raise
        return state

    def boilerplate_node(self, state: Module1):
        print(f"Boilerplate Agent started project_id={state.project_id}")
        logger.info("Boilerplate Agent started project_id=%s", state.project_id)
        self.event_manager.publish(
            state.project_id, {"type": "agent_start", "agent": "boilerplate"}
        )
        try:
            state.boilerplate = self.agents.boilerplate_agent(
                state.requirements,
                state.architecture,
            )
            print(f"Boilerplate Agent finished project_id={state.project_id}")
            logger.info("Boilerplate Agent finished project_id=%s", state.project_id)
            self.event_manager.publish(
                state.project_id, {"type": "agent_end", "agent": "boilerplate"}
            )
        except Exception as e:
            print(f"Boilerplate Agent failed project_id={state.project_id}")
            logger.exception("Boilerplate Agent failed project_id=%s", state.project_id)
            raise
        return state

    def code_writing_node(self, state: Module1):
        print(f"Code Writing Agent started project_id={state.project_id}")
        logger.info("Code Writing Agent started project_id=%s", state.project_id)
        self.event_manager.publish(
            state.project_id, {"type": "agent_start", "agent": "code_writing"}
        )
        try:
            current_file = "backend"
            backend_parts: list[str] = []
            frontend_parts: list[str] = []

            def on_file_start(file_name: str):
                nonlocal current_file
                current_file = file_name
                self.event_manager.publish(
                    state.project_id, {"type": "file_start", "file": file_name}
                )

            def on_token(token: str):
                if current_file == "backend":
                    backend_parts.append(token)
                else:
                    frontend_parts.append(token)
                self.event_manager.publish(
                    state.project_id,
                    {"type": "code_token", "token": token, "file": current_file},
                )

            state.code = self.agents.code_writing_agent(
                requirements=state.requirements,
                architecture=state.architecture,
                boilerplate=state.boilerplate,
                existing_code=state.code,
                on_token=on_token,
                on_file_start=on_file_start,
                on_file_end=lambda file_name: self.event_manager.publish(
                    state.project_id, {"type": "file_end", "file": file_name}
                ),
            )
            state.backend_code = "".join(backend_parts).strip()
            state.frontend_code = "".join(frontend_parts).strip()

            print(f"Code Writing Agent finished project_id={state.project_id}")
            logger.info("Code Writing Agent finished project_id=%s", state.project_id)
            self.event_manager.publish(
                state.project_id, {"type": "agent_end", "agent": "code_writing"}
            )
        except Exception as e:
            print(f"Code Writing Agent failed project_id={state.project_id}")
            logger.exception(
                "Code Writing Agent failed project_id=%s", state.project_id
            )
            raise

        return state

    def analysis_node(self, state: Module1):
        print(f"Analysis Agent started project_id={state.project_id}")
        logger.info("Analysis Agent started project_id=%s", state.project_id)
        self.event_manager.publish(
            state.project_id, {"type": "agent_start", "agent": "analysis"}
        )
        try:
            result = self.agents.analysis_agent(
                generated_code=state.code,
            )

            state.review_result = result.model_dump()
            state.report = result.final_readme

            print(f"Analysis Agent finished project_id={state.project_id}")
            logger.info("Analysis Agent finished project_id=%s", state.project_id)
            self.event_manager.publish(
                state.project_id, {"type": "agent_end", "agent": "analysis"}
            )
        except Exception as e:
            print(f"Analysis Agent failed project_id={state.project_id}")
            logger.exception("Analysis Agent failed project_id=%s", state.project_id)
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
