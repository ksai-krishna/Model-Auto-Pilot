# Model-Auto-Pilot

**Model-Auto-Pilot** is an intelligent tool that searches for Hugging Face models, extracts installation instructions, and summarizes relevant README content — all through an interactive Gradio UI. It is designed to assist developers in quickly identifying, understanding, and integrating ML models with minimal manual effort.

---

## 🔍 Features

- **Search Hugging Face Models by Tag/Keyword**  
  Uses Hugging Face’s public API to search models by pipeline tags, keywords, or tasks.

- **Gated Model Access with Token Authentication**  
  Supports private or gated models via Hugging Face API tokens.

- **Installation Instruction Extraction**  
  Automatically reads model `README.md` files and extracts relevant installation/setup steps using LLM-based parsing.

- **Usage Summary Generation**  
  Extracts only actionable parts from a model’s documentation, skipping research and abstract content.

- **Modular MCP Integration**  
  Built on top of the Model Context Protocol (MCP) framework, enabling future integrations with agents and automation systems.

---

## 📂 Folder Structure

```
Model-Auto-Pilot/
│
├── hf_mcp/
│   ├── core/
│   │   ├── model_utils.py          # Hugging Face API & README fetch utilities
│   │   └── __init__.py
│   │
│   └── tools/
│       ├── install_instruction.py  # LLM prompt logic to extract installation steps
│       ├── summarize.py            # Tool to summarize documentation
│       ├── model_search.py         # Searches Hugging Face models
│       └── __init__.py
│
├── server.py                       # registers MCP tools and starts the MCP server
├── mcp_client.py                   # Starts the gradio UI 
├── .env                            # Hugging Face token storage (HF_TOKEN)
├── pyproject.toml
└── README.md
```

---

## ⚙️ Setup

1. **Clone the Repository**

```bash
git clone https://github.com/ksai-krishna/Model-Auto-Pilot.git
cd Model-Auto-Pilot/hf_mcp
```

2. **Setup virtual Environment**
```bash
uv venv
```

3. **Install Dependencies**

```bash
uv sync
```

4. **Set Environment Variables**

Create a `.env` file in the root directory and add your Hugging Face token:

```env
HF_TOKEN=your_huggingface_token
```

> This is required to access gated/private models and fetch READMEs via the API.

5. **Start the Server**

```bash
uv run server.py
```

6. **Start the Client**

```bash
uv run mcp_client.py
```

The Gradio UI will launch at `http://localhost:7860`.

---

## 💡 Example Usage (via Gradio Interface)

Here are some example inputs you can try in the interface:

- **"Search for the best image-to-image models"**  
  Returns a list of relevant models with usage details.

- **"Get installation steps for runwayml/stable-diffusion-v1-5"**  
  Parses the README and provides step-by-step setup instructions.

- **"Find models that use ComfyUI"**  
  Filters models that include ComfyUI usage in their documentation.

---

## ✅ Current Limitations

- Does not yet install the models automatically (planned).
- Model README parsing depends on consistent documentation style.
- Only supports Hugging Face-hosted models.

---

## 🚧 Planned Features

- Fully automate the installation and environment setup.
- Visual installation progress tracking.

---

## 🛠️ Built With

- **Gradio** for the frontend interface
- **FastMCP** for the backend agent protocol
- **LangChain + LLM** for prompt-based instruction generation
- **Hugging Face Hub API** for model discovery