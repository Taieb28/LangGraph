# agent.py
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.graph.message import add_messages
from typing import Annotated, TypedDict, List
from tools import multiply
import os


# read the key
os.environ["GOOGLE_API_KEY"] = os.getenv("GOOGLE_API_KEY")

class State(TypedDict):
    messages: Annotated[list, add_messages]

tools = [multiply] # list of Tools


# 2. Configuraton
llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash")
llm_with_tools = llm.bind_tools(tools)

# 3. Agent Node
def chatbot_node(state:State):
	response = llm_with_tools.invoke(state["messages"])
	return {"messages":[response]}

# 4. Tool Node
tool_node = ToolNode(tools)

builder = StateGraph(State)

# Add Nodes
builder.add_node("chatbot", chatbot_node)
builder.add_node("tools", tool_node)

# Select first node
builder.add_edge(START, "chatbot")

# Add conditional node
builder.add_conditional_edges(
    "chatbot",
    tools_condition, # it is function
)
# Add edge
builder.add_edge("tools", "chatbot")

# 
agent = builder.compile()
