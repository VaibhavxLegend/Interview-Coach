from __future__ import annotations
from typing import Dict, Any
from langgraph.graph import StateGraph, END
from .agents import evaluator_agent, feedback_agent, interviewer_agent


def build_graph():
    g = StateGraph(dict)

    async def evaluate_node(state: Dict[str, Any]):
        ev = await evaluator_agent(state["question"], state["answer"])
        state["evaluation"] = ev
        return state

    async def feedback_node(state: Dict[str, Any]):
        friendly = await feedback_agent(state["evaluation"])
        state["friendly"] = friendly
        return state

    async def interviewer_node(state: Dict[str, Any]):
        nq = await interviewer_agent(state["role"], state["seniority"])
        state["next_question"] = nq
        return state

    g.add_node("evaluate", evaluate_node)
    g.add_node("feedback", feedback_node)
    g.add_node("interviewer", interviewer_node)

    g.set_entry_point("evaluate")
    g.add_edge("evaluate", "feedback")
    g.add_edge("feedback", "interviewer")
    g.add_edge("interviewer", END)

    return g.compile()


compiled_graph = build_graph()


async def run_interview_step(question: str, answer: str, role: str, seniority: str) -> Dict[str, Any]:
    init = {"question": question, "answer": answer, "role": role, "seniority": seniority}
    state = await compiled_graph.ainvoke(init)
    return state
