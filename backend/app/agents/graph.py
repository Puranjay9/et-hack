"""LangGraph StateGraph definition — wires all agent nodes with conditional edges."""

from langgraph.graph import StateGraph, END
from app.agents.state import AgentState
from app.agents.supervisor import supervisor_node
from app.agents.strategy import strategy_agent
from app.agents.discovery import discovery_agent
from app.agents.memory import memory_retrieval
from app.agents.email_gen import email_generation_agent
from app.agents.evaluator import evaluator_agent


def route_evaluator(state: AgentState) -> str:
    """Route after evaluator: retry email gen or accept and end."""
    if state.get("eval_score", 0) >= 7.0 or state.get("retry_count", 0) >= 3:
        return "accept"
    return "retry"


def build_graph() -> StateGraph:
    """Build and return the compiled LangGraph agent pipeline."""
    graph = StateGraph(AgentState)

    # Add all nodes
    graph.add_node("supervisor", supervisor_node)
    graph.add_node("strategy", strategy_agent)
    graph.add_node("discovery", discovery_agent)
    graph.add_node("memory", memory_retrieval)
    graph.add_node("email_gen", email_generation_agent)
    graph.add_node("evaluator", evaluator_agent)

    # Set entry point
    graph.set_entry_point("supervisor")

    # Linear edges: supervisor → strategy → discovery → memory → email_gen → evaluator
    graph.add_edge("supervisor", "strategy")
    graph.add_edge("strategy", "discovery")
    graph.add_edge("discovery", "memory")
    graph.add_edge("memory", "email_gen")
    graph.add_edge("email_gen", "evaluator")

    # Conditional edge: evaluator → retry email_gen OR accept → END
    graph.add_conditional_edges(
        "evaluator",
        route_evaluator,
        {
            "retry": "email_gen",
            "accept": END,
        },
    )

    return graph.compile()


# Compile the graph at module level for reuse
compiled_graph = build_graph()
