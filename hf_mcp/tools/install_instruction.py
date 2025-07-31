from core.model_utils import search_model_web, search_for_readme

def register_install_instruction_tool(mcp, llm):
    @mcp.tool()
    def generate_installation_instructions(query: str, limit: int = 2) -> str:
        """
        Generates installation instructions for a model based on its README.md content.

        Args:
            query (str): User's query to find relevant models.

        Returns:
            str: Concise installation instructions for the model.
        """
        models = search_model_web(query, limit)
        if not models:
            return "No models found matching your query."
        
        instructions = []
        print(f"🔍 Found {len(models)} models for installation instructions.")
        
        for model in models:
            model_id = model.get("modelId")
            print(f"🔍 Fetching README for model: {model_id}")
            if not model_id:
                continue
            instructions.append(f"for Model: {model_id}\n")
            try:
                readme_content = search_for_readme(model_id)
                if readme_content:
                    prompt = f"""
                    You are an Installation Instruction Generator AI.
                    Your job is to carefully read the README.md from a Hugging Face model repository and extract all relevant installation instructions.
                    For each model mentioned:
                    Identify how to install or use the model, whether it’s through pip, transformers, diffusers, ComfyUI, web UIs, or any other method.
                    If there are multiple ways to install or run the model (e.g., local setup, cloud usage, UI-based tools), clearly outline each option.
                    Include system requirements or setup dependencies if mentioned.
                    Ignore general model descriptions or research background unless they’re tied to setup.
                    Your output should be a clear, step-by-step installation and usage guide based on the README.
                    This is the README content:
                    {readme_content}
                    """
                response = llm.invoke(prompt)
                return response.content
            except Exception as e:
                return f"⚠️ Failed to generate installation instructions for model {model_id}: {str(e)}"
