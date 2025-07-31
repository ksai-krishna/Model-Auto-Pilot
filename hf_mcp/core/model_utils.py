from huggingface_hub import HfApi
from typing import List
import requests
import re
from bs4 import BeautifulSoup
from datetime import datetime,timedelta
from dotenv import load_dotenv
import os
load_dotenv()

HF_TOKEN = os.getenv("HF_TOKEN")
def search_model_web(query: str, limit: int = 5, tag_filter: str = "text-to-image"):
    base_url = "https://huggingface.co/api/models"
    params = {
        "pipeline_tag": tag_filter,
        "sort": "downloads",  # Just to get most relevant stuff upfront
        "limit": 100
    }

    headers = {
            "Authorization": f"Bearer {HF_TOKEN}"
        }

    try:
        res = requests.get(base_url, params=params,headers=headers)
        res.raise_for_status()
        models = res.json()

        fresh_cutoff = datetime.now() - timedelta(days=180)
        # print("Fresh cutoff -------------------------- ",fresh_cutoff)
        scored_models = []
        # print(f"🔍 Model {model_id} has score: {score} (likes: {likes}, downloads: {downloads}, age_days: {age_days})")
        # print(f"🔍 Found {models} models for query: {query} with tag '{tag_filter}'")
        for model in models:

            created = model.get("createdAt")
            if not created:
                continue
            
            created_dt = datetime.strptime(created, "%Y-%m-%dT%H:%M:%S.%fZ")
            likes = model.get("likes", 0)
            if created_dt < fresh_cutoff or likes < 200:
                continue  # skip oldies

            downloads = model.get("downloads", 0)
            model_id = model.get("modelId", "")
            

            age_days = max((datetime.now() - created_dt).days, 1)
            score = (likes * 2 + downloads * 0.01) / age_days

            # print(f"🔍 Model {model_id} has score: {score} (likes: {likes}, downloads: {downloads}, age_days: {age_days})")
            scored_models.append({
                "modelId": model_id,
                "downloads": downloads,
                "likes": likes,
                "uri": f"hf://model/{model_id}",
                "score": score
            })
        
        
        # Sort by custom freshness score
        sorted_models = sorted(scored_models, key=lambda m: m["score"], reverse=True)
        # print(f"🔍 Found {len(sorted_models)} models for query: {query} with tag '{tag_filter}'")
        # print(f"🔍 Found {sorted_models} models for query: {query} with tag '{tag_filter}'")
        print(sorted_models[:limit])
        return sorted_models[:limit]

    except Exception as e:
        print("🚨 Model fetch failed:", str(e))
        return []


def search_for_readme(model_id: str) -> str:
    """
    Fetch and clean the README.md content for a Hugging Face model,
    converting useful HTML content like tables and links into Markdown for LLM processing.

    Args:
        model_id (str): Hugging Face model ID (e.g., "stabilityai/stable-diffusion")

    Returns:
        str: Cleaned README content suitable for LLM processing.
    """
    try:
        raw_url = f"https://huggingface.co/{model_id}/raw/main/README.md"
        headers = {
            "Authorization": f"Bearer {HF_TOKEN}"
        }

        response = requests.get(raw_url,headers=headers)

        if response.status_code != 200:
            return f"README not found for model: `{model_id}` (Status: {response.status_code})"

        original_markdown = response.text

        # Step 1: Convert Markdown to HTML for reliable parsing
        soup = BeautifulSoup(original_markdown, 'html.parser')

        markdown_tables = []
        for table in soup.find_all("table"):
            title = "Untitled Table"

            # Search up to 4 previous siblings to guess the table title
            prev_candidates = list(table.find_all_previous(limit=10))  # pull a few for backup
            for i, prev in enumerate(prev_candidates):
                if i >= 4:
                    break
                if prev.name in ["h1", "h2", "h3", "h4", "h5", "h6"] and prev.get_text(strip=True):
                    title = prev.get_text(strip=True)
                    break
                elif prev.name == "p":
                    text = prev.get_text(strip=True)
                    if re.match(r"^(#{2,6})\s+.+", text):  # detect markdown heading inside <p>
                        title = re.sub(r"^(#{2,6})\s+", "", text).strip()
                        break
                    elif len(text) > 5:
                        title = text
                        break

            # Build Markdown version of the table
            rows = table.find_all("tr")
            table_md = []
            for row in rows:
                cols = row.find_all(["td", "th"])
                table_md.append("| " + " | ".join(col.get_text(strip=True) for col in cols) + " |")

            if len(table_md) >= 2:
                col_count = table_md[0].count("|") - 1
                separator = "| " + " | ".join(["---"] * col_count) + " |"
                table_md.insert(1, separator)

            # Append with a nice title
            markdown_tables.append(f"### {title}\n\n" + "\n".join(table_md))
            table.decompose()  # Clean up from soup

        # Step 3: Extract all <a> tags and build the "Links" section
        links = []
        for a in soup.find_all("a", href=True):
            text = a.get_text(strip=True)
            href = a["href"]
            cleaned_text = re.sub(r'[^\w\s\-&]', '', text).strip()
            if cleaned_text and href:
                links.append(f"- **{cleaned_text}**: {href}")
            a.replace_with(text)

        # Step 4: Remove useless <div>, <style>, <script>, <img>, etc.
        for tag in soup(["div", "style", "script", "picture", "img"]):
            tag.decompose()

        # Step 5: Extract remaining cleaned text
        cleaned_text = soup.get_text(separator="\n").strip()

        # Step 6: Merge everything together
        final_readme = cleaned_text

        if markdown_tables:
            final_readme += "\n\n## Tables Extracted\n" + "\n\n".join(markdown_tables)

        if links:
            final_readme += "\n\n## Links\n" + "\n".join(links)
        print(final_readme)
        return final_readme

    except Exception as e:
        return f"⚠️ Error fetching or processing README for `{model_id}`:\n{str(e)}"
