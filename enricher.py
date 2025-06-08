import openai
import json
import time
import pandas as pd
import os
from tqdm import tqdm
from dotenv import load_dotenv

load_dotenv()
# ✅ Set your API key
openai.api_key = os.getenv("OPENAI_API_KEY")

# Input/output CSV paths
INPUT_XL = os.path.join("Data", "Sample_dirty.xlsx")
OUTPUT_CSV = os.path.join("Data", "enriched_catalog.csv")

def build_prompt(full_row_text):
    return f"""
You are a helpful AI assistant that cleans and enriches messy food product catalog data.

Given the following raw row from a product catalog:
\"\"\"{full_row_text}\"\"\"

Please extract and enrich the product info. Provide a JSON output with the following fields:
- clean_title: A clean, properly capitalized product name
- brand: Brand name if present or inferable, else null
- category: One of [Meat, Beverage, Pantry, Produce, Paper Goods, Dairy, Frozen, Other]
- packaging: Packaging size and type if mentioned (e.g., "5kg", "2 x 500ml", "12CT")
- tags: List of relevant tags such as ["frozen", "organic", "bulk", "gluten-free"]
- price: The price as a number

Please ONLY return the JSON object and nothing else.
"""

def enrich_product(row):
    full_row_text = ", ".join([f"{col}: {row[col]}" for col in row.index])
    prompt = build_prompt(full_row_text)
    try:
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
            max_tokens=300,
        )
        content = response.choices[0].message.content.strip()
        json_start = content.find("{")
        json_end = content.rfind("}") + 1
        json_text = content[json_start:json_end]
        return json.loads(json_text)
    except Exception as e:
        print("❌ Error enriching product:", e)
        return None

def main():
    df = pd.read_excel(INPUT_XL)
    enriched_rows = []

    for _, row in tqdm(df.iterrows(), total=len(df)):
        enriched = enrich_product(row)
        if enriched:
            enriched_rows.append(enriched)
        time.sleep(1)  # Optional: respect rate limits

    if enriched_rows:
        enriched_df = pd.DataFrame(enriched_rows)
        enriched_df.to_csv(OUTPUT_CSV, index=False)
        print(f"✅ Enriched data saved to {OUTPUT_CSV}")

if __name__ == "__main__":
    main()
