from graph.state import AgentState
from graph.prompt import SYSTEM_PROMPT
from agents import tools as all_tools
from langchain_aws import ChatBedrock
from langchain_core.messages import SystemMessage
from langgraph.graph import StateGraph , START
from langgraph.prebuilt import ToolNode, tools_condition

_llm = ChatBedrock(model="global.anthropic.claude-sonnet-4-6", streaming=True)
_llm_with_tools = _llm.bind_tools(all_tools)

async def agent_node(state: AgentState)-> dict:
    """
    Node function for the agent. It takes the conversation history and other relevant information
      from the state, and returns the next message to be sent to the user."""
    messages= [SystemMessage(content=SYSTEM_PROMPT)] + state["messages"]
    response = await _llm_with_tools.ainvoke(messages)
    return {"messages": [response]}


def build_graph() -> StateGraph:
  builder = StateGraph(AgentState)

  builder.add_node("agent",agent_node)
  builder.add_node("tools", ToolNode(all_tools))

  builder.add_edge(START, "agent")
  builder.add_conditional_edges("agent", tools_condition)
  builder.add_edge("tools", "agent")

  return builder.compile()

graph=build_graph()