from openai import OpenAI
import os
import re

# --- 🔑 CONFIGURATION ---
# 1. Get a Key: https://openrouter.ai/keys
# 2. Paste it below inside the quotes (No spaces!)
API_KEY = "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"

# OpenRouter Configuration
BASE_URL = "https://openrouter.ai/api/v1"
MODEL_NAME = "openai/gpt-oss-20b:free"

client = OpenAI(
  base_url=BASE_URL,
  api_key=API_KEY,
)
# ---------------------

def get_cypher_query(user_question):
    # Safety Check
    if "PASTE_YOUR" in API_KEY:
        print("❌ ERROR: You forgot to paste your OpenRouter API Key in llm_helper.py")
        return None

    print(f"   [LLM] Translating: '{user_question}'")

    schema_text = """
    My Neo4j Graph Schema:
    - Nodes: 
      - Repository (properties: name, stars, libraries, owner)
      - ProgrammingLanguage (properties: name)
      - TopicTag (properties: name)
    
    - Relationships:
      - (:Repository)-[:IS_WRITTEN_IN]->(:ProgrammingLanguage)
      - (:Repository)-[:HAS_TOPIC]->(:TopicTag)
    """

    system_instruction = f"""
    {schema_text}
    
    You are a code generator. Your ONLY task is to translate the user's question into a Cypher query.
    
    CRITICAL RULES:
    1. Output ONLY the Cypher query. No markdown. No "Here is the query".
    2. Do NOT use the word 'ILIKE'. It causes errors.
    3. Instead, use 'WHERE toLower(n.name) CONTAINS toLower("value")'.
    4. Do NOT put conditions inside the node brackets {{}}. Use a WHERE clause.
       - WRONG: (l:ProgrammingLanguage {{name: 'Python'}})
       - RIGHT: (l:ProgrammingLanguage) WHERE toLower(l.name) = 'python'
    5. Always RETURN: r.name, r.stars, r.libraries, r.owner
    6. Order by stars descending.
    7. Limit results to 10.
    """

    try:
        print(f"   [System] Sending to {MODEL_NAME}...")

        completion = client.chat.completions.create(
            extra_headers={
                "HTTP-Referer": "http://localhost:8501",
                "X-Title": "GitHub Recommender App",
            },
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": user_question}
            ],
            temperature=0,
            timeout=45,
            extra_body={ "reasoning": {"enabled": True} }
        )

        content = completion.choices[0].message.content.strip()
        clean_query = content.replace("```cypher", "").replace("```", "").strip()

        if "MATCH" in clean_query.upper():
            match = re.search(r"(MATCH[\s\S]*)", clean_query, re.IGNORECASE)
            if match:
                clean_query = match.group(1)
            return clean_query
        else:
            print(f"   [Warning] Invalid response: {clean_query[:50]}...")
            return None

    except Exception as e:
        print(f"   [Error] Request Failed: {e}")
        return None