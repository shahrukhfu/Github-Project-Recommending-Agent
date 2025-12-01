from openai import OpenAI
import os

# --- PASTE YOUR KEY HERE ---
# Make sure there are NO SPACES around it!
API_KEY = "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"
# ---------------------------

print(f"Testing Key: {API_KEY[:10]}...{API_KEY[-5:]}")

client = OpenAI(
  base_url="https://openrouter.ai/api/v1",
  api_key=API_KEY,
)

try:
    print("\nConnecting to OpenRouter...")
    completion = client.chat.completions.create(
      model="openai/gpt-oss-20b:free",
      messages=[
        {"role": "user", "content": "Say 'Success!' if you can hear me."}
      ],
      timeout=10
    )
    print(f"✅ RESPONSE: {completion.choices[0].message.content}")
    print("🎉 Your key is working perfectly.")

except Exception as e:
    print(f"\n❌ FAILED: {e}")
    if "401" in str(e):
        print("👉 This confirms the KEY is wrong. Go to openrouter.ai/keys and generate a new one.")