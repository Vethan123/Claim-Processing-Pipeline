from langgraph.graph import StateGraph, END
from app.schema.models import DocumentState
from app.agents.segregator import classify_pages
from app.agents.extractors import id_agent, discharge_agent, bill_agent, default_agent
from app.agents.aggregator import aggregate_results
from langgraph.types import RetryPolicy

def router(state: DocumentState):
    print(f"DEBUG: Segregator identified: {state.classifications}")
    mapping = {
        "bill_agent": "bill_extraction",
        "id_agent": "id_extraction",
        "discharge_agent": "discharge_extraction",
        "default_agent": "default_extraction"
    }
    
    raw_labels = set(state.classifications.values())
    next_nodes = []
    
    for label in raw_labels:
        target_node = mapping.get(label.lower())
        if target_node:
            next_nodes.append(target_node)
    
    if not next_nodes:
        print("DEBUG: No valid nodes found, defaulting to aggregator")
        return ["aggregator"]
        
    print(f"DEBUG: Routing to nodes: {next_nodes}")
    return next_nodes

def create_graph():
    workflow = StateGraph(DocumentState)

    standard_retry = RetryPolicy(max_attempts=3)

    workflow.add_node("segregator", classify_pages, retry=standard_retry)
    workflow.add_node("id_extraction", id_agent, retry=standard_retry)
    workflow.add_node("discharge_extraction", discharge_agent, retry=standard_retry)
    workflow.add_node("bill_extraction", bill_agent, retry=standard_retry)
    workflow.add_node("default_extraction", default_agent, retry=standard_retry)
    workflow.add_node("aggregator", aggregate_results)

    workflow.set_entry_point("segregator")

    workflow.add_conditional_edges(
        "segregator",
        router,
        {
            "id_extraction": "id_extraction",
            "discharge_extraction": "discharge_extraction",
            "bill_extraction": "bill_extraction",
            "default_extraction": "default_extraction",
            "aggregator": "aggregator"
        }
    )

    workflow.add_edge("id_extraction", "aggregator")
    workflow.add_edge("discharge_extraction", "aggregator")
    workflow.add_edge("bill_extraction", "aggregator")
    workflow.add_edge("default_extraction", "aggregator")

    workflow.add_edge("aggregator", END)

    return workflow.compile()