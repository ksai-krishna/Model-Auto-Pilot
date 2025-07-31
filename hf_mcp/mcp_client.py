from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver 
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain_google_genai import ChatGoogleGenerativeAI

from typing import List, TypedDict
from dotenv import load_dotenv
import asyncio
import gradio as gr
import os
import nest_asyncio
import uuid


# Load environment variables
load_dotenv()

# Define a custom memory state
class AgentState(TypedDict):
    messages: List[BaseMessage]

checkpointer = AsyncSqliteSaver.from_conn_string("sqlite:///memory.db")

# Global agent instance and memory checkpoint
agent = None

async def setup_agent():
    global agent
    if agent is None:
        # MCP client setup
        client = MultiServerMCPClient({
            "huggingface_mcp": {
                "url": "http://127.0.0.1:3000/sse",
                "transport": "sse",
            }
        })

        # Discover available tools
        tools = await client.get_tools()
        print("Discovered HuggingFace tools:", [tool.name for tool in tools])

        # LLM: Gemini via Google Generative AI
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            temperature=0.2
        )

        checkpointer = AsyncSqliteSaver.from_conn_string("sqlite:///memory.db")
        # Create ReAct agent with tools + memory
        agent = create_react_agent(
            model=llm,
            tools=tools,
            checkpointer=checkpointer,
            debug=True
        )

    return agent

async def chat_handler(message, history):
    try :
        agent = await setup_agent()
        thread_id = uuid.uuid4() # Generating unique id
        prev_state = await checkpointer.aget({"configurable": {"thread_id": thread_id}})

        # Load previous memory state (conversation history)

        if prev_state is None:
            prev_state = AgentState(messages=[])

        # Append user message to memory
        prev_state["messages"].append(HumanMessage(content=message))
        new_state = await agent.ainvoke(prev_state, config={"thread_id": thread_id})
        reply = new_state["messages"]
        return reply[-1].content
    except Exception as e:
        return f"❌ Error: {str(e)}"

# Gradio UI
demo = gr.ChatInterface(
    fn=chat_handler,
    title="🤖 HuggingFace Model Explorer",
    description="""Ask me things like:
- 🔍 Search: 'Find a model for image segmentation'
- 💯 Top models: 'Show best LLMs for summarization'
- 🛠️ Tools: 'Get installation steps for mistralai/Mixtral'""",
    theme="soft",
)

if __name__ == "__main__":
    nest_asyncio.apply()
    demo.launch()
