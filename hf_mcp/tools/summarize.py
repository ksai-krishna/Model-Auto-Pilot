from core.model_utils import search_for_readme,search_model_web

def register_summary_tool(mcp, llm):
    @mcp.tool()
    def generate_summary(llm,query:str,limit:int = 2) -> str:
        """
        Summarizes a model's README.md content using a provided LLM.

        Args:
            query (str): Users query.

        Returns:
            str: Concise summary of the README.
        """
        models = search_model_web(query, limit)
        if not models:
            return "No models found matching your query."
        summaries = []
        print(f"🔍 Found {models} models for summarization.")
        for model in models:
            model_id = model.get("modelId")
            print(f"🔍 Fetching README for model: {model_id}")
            if not model_id:
                continue
            readme_content = search_for_readme(model_id)
            print(f"The readme content for {model_id} is : {readme_content} ************")
            if "README not found" in readme_content:
                summaries.append(f"⚠️ {readme_content}")
                continue
        print(f"🔍 Summarizing README for model: ---- {readme_content}")
        try:
            prompt = f"""You are a helpful AI agent. Please read and summarize the following README.md from a Hugging Face model repository.
                        README :{readme_content} Give a clear and concise summary for each model, focusing on key features, usage instructions, and any important notes.:
                        """
            response = llm.invoke(prompt)
            # print(f"🔍 Summarizing README for model: {response.content}")
            return response.content if hasattr(response, "content") else str(response)
        except Exception as e:
            return f"⚠️ Failed to generate summary: {str(e)}"