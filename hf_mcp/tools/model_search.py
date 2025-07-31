import sys
import os

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from typing import List
from core.model_utils import search_model_web
import requests
from datetime import datetime, timedelta
from math import log

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import Runnable
from langchain_google_genai import ChatGoogleGenerativeAI

# Setup LLM (replace with your preferred model if needed)
llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.2)

# Prompt to classify query into tags
tag_classifier_prompt = ChatPromptTemplate.from_template(
    """Classify the following user query into one of these model tags:
- text-to-image
- text-generation
- image-segmentation
- text-classification
- summarization
- image-to-text
- question-answering

User query: {query}

Respond with only the tag name."""
)

# Chain it with the LLM
tag_classifier: Runnable = tag_classifier_prompt | llm

# Tool registration
def register_search_tool(mcp):
    @mcp.tool()
    async def search_model(query: str, limit: int = 5):
        """
        Searches for models on Hugging Face based on a query. Automatically determines
        the appropriate model tag (e.g., 'text-to-image', 'text-generation') using an LLM.

        Args:
            query (str): Search query.
            limit (int): Maximum number of models to return.

        Returns:
            List[str]: List of model IDs matching the LLM-inferred tag.
        """
        # 🧠 Let the LLM classify the tag
        tag = await tag_classifier.ainvoke({"query": query})
        tag = tag.content.strip()
        print(f"🔖 Inferred tag from LLM: {tag}")

        # 🚀 Now run the actual search
        return search_model_web(query, limit, tag_filter=tag)