from mcp.server.fastmcp import FastMCP
from tools.summarize import register_summary_tool
from tools.model_search import register_search_tool
from tools.install_instruction import register_install_instruction_tool

from langchain_google_genai import ChatGoogleGenerativeAI

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0.2
)


mcp = FastMCP(name="Huggingface MCP", port=3000, host="127.0.0.1")

# Register tools

register_summary_tool(mcp, llm)
register_search_tool(mcp)
register_install_instruction_tool(mcp,llm)

# Start MCP server using stdio or socket
mcp.run(transport="sse")
