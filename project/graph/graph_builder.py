from langgraph.graph import StateGraph, START, END
from .state import SupportState
from .nodes import tool_node, connect_node, determine_next

AIgraph = StateGraph(SupportState)

AIgraph.add_node('connect_node', connect_node)
AIgraph.add_node('tool_node', tool_node)
AIgraph.add_edge(START, 'connect_node')
AIgraph.add_conditional_edges('connect_node',  determine_next, ['tool_node', END])
AIgraph.add_edge('tool_node', 'connect_node')
AIgraph.add_edge('connect_node', END)
graph = AIgraph.compile()