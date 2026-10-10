from typing import Any

from langgraph.graph import StateGraph, START, END

from agents import Agents
from events import emit_event
from schemas import Module3


class Module2Workflow:
    """Workflow for Module 3: Cyber Intelligence and Code Audit."""

    def __init__(self, agents: Agents):
        self.agents = agents
        self.graph = self._build_graph()

    # ------------------------------------------------------------
    # 1. Cyber Security Analysis
    # ------------------------------------------------------------

    def cyber_security_node(self, state: Module3) -> dict[str, Any]:
        print("➡️ Cyber Security Agent")
        emit_event(
            {
                "type": "agent_start",
                "agent": "cyber_security",
            }
        )

        try:
            result = self.agents.cyber_security_agent(
                source_code=state.source_code,
            )

            emit_event(
                {
                    "type": "agent_end",
                    "agent": "cyber_security",
                }
            )

            return {"security_result": result}

        except Exception as exc:
            emit_event(
                {
                    "type": "agent_error",
                    "agent": "cyber_security",
                    "error": str(exc),
                }
            )
            raise

    # ------------------------------------------------------------
    # 2. Static Analysis
    # ------------------------------------------------------------

    def static_analysis_node(self, state: Module3) -> dict[str, Any]:
        print("➡️ Static Analysis Agent")
        emit_event(
            {
                "type": "agent_start",
                "agent": "static_analysis",
            }
        )

        try:
            result = self.agents.static_analysis_agent(
                source_code=state.source_code,
            )

            emit_event(
                {
                    "type": "agent_end",
                    "agent": "static_analysis",
                }
            )

            return {"static_result": result}

        except Exception as exc:
            emit_event(
                {
                    "type": "agent_error",
                    "agent": "static_analysis",
                    "error": str(exc),
                }
            )
            raise

    # ------------------------------------------------------------
    # 3. Complexity Analysis
    # ------------------------------------------------------------

    def complexity_analysis_node(
        self,
        state: Module3,
    ) -> dict[str, Any]:
        print("➡️ Complexity Analysis Agent")
        emit_event(
            {
                "type": "agent_start",
                "agent": "complexity_analysis",
            }
        )

        try:
            result = self.agents.complexity_analysis_agent(
                source_code=state.source_code,
            )

            emit_event(
                {
                    "type": "agent_end",
                    "agent": "complexity_analysis",
                }
            )

            return {"complexity_result": result}

        except Exception as exc:
            emit_event(
                {
                    "type": "agent_error",
                    "agent": "complexity_analysis",
                    "error": str(exc),
                }
            )
            raise

    # ------------------------------------------------------------
    # 4. Final Audit
    # ------------------------------------------------------------

    def final_audit_node(self, state: Module3) -> dict[str, Any]:
        print("➡️ Final Audit Agent")
        emit_event(
            {
                "type": "agent_start",
                "agent": "final_audit",
            }
        )

        try:
            report = self.agents.final_audit_agent(
                security_result=state.security_result,
                static_result=state.static_result,
                complexity_result=state.complexity_result,
            )

            emit_event(
                {
                    "type": "agent_end",
                    "agent": "final_audit",
                }
            )

            return {"final_report": report}

        except Exception as exc:
            emit_event(
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
            "static_analysis",
            self.static_analysis_node,
        )

        workflow.add_node(
            "complexity_analysis",
            self.complexity_analysis_node,
        )

        workflow.add_node(
            "final_audit",
            self.final_audit_node,
        )

        # Start all three independent analyses.
        workflow.add_edge(START, "cyber_security")
        workflow.add_edge(START, "static_analysis")
        workflow.add_edge(START, "complexity_analysis")

        # Wait for all three before generating the final report.
        workflow.add_edge(
            [
                "cyber_security",
                "static_analysis",
                "complexity_analysis",
            ],
            "final_audit",
        )

        workflow.add_edge("final_audit", END)

        return workflow.compile()
