import logging
from typing import Any

from langgraph.graph import StateGraph, START, END

from agents import Agents
from events import ProjectEventManager
from schemas import Module3

logger = logging.getLogger(__name__)


class Module2Workflow:
    """Workflow for Module 3: Cyber Intelligence and Code Audit."""

    def __init__(self, agents: Agents, event_manager: ProjectEventManager):
        self.agents = agents
        self.event_manager = event_manager
        self.graph = self._build_graph()

    # ------------------------------------------------------------
    # 1. Cyber Security Analysis
    # ------------------------------------------------------------

    def cyber_security_node(self, state: Module3) -> dict[str, Any]:
        print(f"Security Analytics Agent started project_id={state.project_id}")
        logger.info("Security Analytics Agent started project_id=%s", state.project_id)
        self.event_manager.publish(
            state.project_id,
            {
                "type": "agent_start",
                "agent": "cyber_security",
            }
        )

        try:
            result = self.agents.cyber_security_agent(
                source_code=state.source_code,
            )

            print(f"Security Analytics Agent finished project_id={state.project_id}")
            logger.info("Security Analytics Agent finished project_id=%s", state.project_id)
            self.event_manager.publish(
                state.project_id,
                {
                    "type": "agent_end",
                    "agent": "cyber_security",
                }
            )

            return {"security_result": result}

        except Exception as exc:
            print(f"Security Analytics Agent failed project_id={state.project_id}")
            logger.exception("Security Analytics Agent failed project_id=%s", state.project_id)
            self.event_manager.publish(
                state.project_id,
                {
                    "type": "agent_error",
                    "agent": "cyber_security",
                    "error": str(exc),
                }
            )
            raise

    # ------------------------------------------------------------
    # 2. Final Audit
    # ------------------------------------------------------------

    def final_audit_node(self, state: Module3) -> dict[str, Any]:
        print(f"Final Audit Agent started project_id={state.project_id}")
        logger.info("Final Audit Agent started project_id=%s", state.project_id)
        self.event_manager.publish(
            state.project_id,
            {
                "type": "agent_start",
                "agent": "final_audit",
            }
        )

        try:
            report = self.agents.final_audit_agent(
                security_result=state.security_result,
            )

            print(f"Final Audit Agent finished project_id={state.project_id}")
            logger.info("Final Audit Agent finished project_id=%s", state.project_id)
            self.event_manager.publish(
                state.project_id,
                {
                    "type": "agent_end",
                    "agent": "final_audit",
                }
            )

            return {"final_report": report}

        except Exception as exc:
            print(f"Final Audit Agent failed project_id={state.project_id}")
            logger.exception("Final Audit Agent failed project_id=%s", state.project_id)
            self.event_manager.publish(
                state.project_id,
                {
                    "type": "agent_error",
                    "agent": "final_audit",
                    "error": str(exc),
                }
            )
            raise

    # ------------------------------------------------------------
    # Graph Construction
    # ------------------------------------------------------------

    def _build_graph(self):
        workflow = StateGraph(Module3)

        workflow.add_node(
            "cyber_security",
            self.cyber_security_node,
        )

        workflow.add_node(
            "final_audit",
            self.final_audit_node,
        )

        # Start all three independent analyses.
        workflow.add_edge(START, "cyber_security")
        # Wait for all three before generating the final report.
        workflow.add_edge(
            [
                "cyber_security",
            ],
            "final_audit",
        )

        workflow.add_edge("final_audit", END)

        return workflow.compile()
