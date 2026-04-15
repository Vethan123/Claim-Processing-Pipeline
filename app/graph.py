from langgraph.graph import StateGraph, END
from app.schema.models import DocumentState
from app.agents.segregator import classify_pages
from app.agents.extractors import id_agent, discharge_agent, bill_agent
from app.agents.aggregator import aggregate_results

def create_graph():
    workflow = StateGraph(DocumentState)

    # Add the nodes
    workflow.add_node("segregator", classify_pages)
    workflow.add_node("id_extraction", id_agent)
    workflow.add_node("discharge_extraction", discharge_agent)
    workflow.add_node("bill_extraction", bill_agent)
    workflow.add_node("aggregator", aggregate_results)

    # START -> Segregator
    workflow.set_entry_point("segregator")

    # Parallel branching: Segregator -> All 3 Extraction Agents
    workflow.add_edge("segregator", "id_extraction")
    workflow.add_edge("segregator", "discharge_extraction")
    workflow.add_edge("segregator", "bill_extraction")

    # All 3 Agents -> Aggregator
    workflow.add_edge("id_extraction", "aggregator")
    workflow.add_edge("discharge_extraction", "aggregator")
    workflow.add_edge("bill_extraction", "aggregator")

    # Aggregator -> END
    workflow.add_edge("aggregator", END)

    return workflow.compile()