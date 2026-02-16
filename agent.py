from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.graph.message import add_messages
from langchain_core.messages import SystemMessage, AIMessage
from typing import Annotated, TypedDict
from tools import multiply
import os

# 
os.environ["GOOGLE_API_KEY"] = os.getenv("GOOGLE_API_KEY")

class State(TypedDict):
    messages: Annotated[list, add_messages]

# 
SYSTEM_PROMPT = SystemMessage(
    content="""أنت مساعد ذكي ومتخصص. إذا لم تكن لديك أداة لاستعمالها في الرد، 
    لا تقم بتخمين الإجابة وإنما رد بالتالي: "لا املك اداة لاستعمالها"."""
)

tools = [multiply]

# 1. 
llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash") 
llm_with_tools = llm.bind_tools(tools)

# 2. 
def chatbot_node(state: State):
    full_messages = [SYSTEM_PROMPT] + state["messages"]
    response = llm_with_tools.invoke(full_messages)
    
    if isinstance(response.content, list):
        for item in response.content:
            if isinstance(item, dict) and "text" in item:
                response.content = item["text"]
                break
            elif isinstance(item, str):
                response.content = item
                break

    return {"messages": [response]}

# 3
builder = StateGraph(State)
builder.add_node("chatbot", chatbot_node)
builder.add_node("tools", ToolNode(tools))

builder.add_edge(START, "chatbot")
builder.add_conditional_edges("chatbot", tools_condition)
builder.add_edge("tools", "chatbot")

agent = builder.compile()