import os
import csv
import json
from openai import OpenAI

# It is recommended to set the OpenAI API key as an environment variable.
# Example: export OPENAI_API_KEY='your-api-key'
# The client automatically picks it up from the environment.
try:
    client = OpenAI()
except ImportError:
    print("OpenAI library is not installed. Please install it using 'pip install openai'")
    client = None

# --- Glossary Loading and Caching ---
_glossary_cache = None

def _load_glossary(filepath: str = "data_set.csv") -> str:
    """
    Loads the glossary from the CSV file and formats it into a string.
    Caches the result to avoid repeated file I/O.
    """
    global _glossary_cache
    if _glossary_cache is not None:
        return _glossary_cache

    try:
        with open(filepath, mode='r', encoding='utf-8') as infile:
            reader = csv.reader(infile)
            next(reader)  # Skip header row
            glossary_terms = [f"- {row[0]}: {row[1]}" for row in reader]

        _glossary_cache = "\n".join(glossary_terms)
        return _glossary_cache
    except FileNotFoundError:
        print(f"Warning: Glossary file not found at '{filepath}'. Proceeding without it.")
        _glossary_cache = "" # Cache empty string to prevent re-attempts
        return ""
    except Exception as e:
        print(f"Warning: Failed to load glossary file. Error: {e}. Proceeding without it.")
        _glossary_cache = ""
        return ""

# --- Main Analysis Function ---
def analyze_feature_description(description: str) -> dict:
    """
    Analyzes a feature description using an LLM to determine if it requires
    geo-specific compliance logic, using a glossary for context.
    """
    if not client:
        return {
            "is_geo_compliance_needed": None,
            "reasoning": "OpenAI client is not initialized. Please check your installation.",
            "relevant_regulation": "N/A"
        }

    glossary_context = _load_glossary()

    prompt = f"""
    You are an expert compliance analyst AI. Your task is to determine if a feature
    requires geo-specific compliance logic based on its description.

    A feature requires geo-specific compliance if it is being implemented to
    comply with a specific law, regulation, or legal mandate in a particular
    geographic region (e.g., a country, state, or union like the EU).

    Do NOT flag features for the following reasons:
    - Business-driven decisions, such as market testing, phased rollouts, or A/B tests in specific regions.
    - General safety or policy features that apply globally, even if they mention a region for context.

    To help you understand the feature description, here is a glossary of internal terms that may be used:
    ---
    <GLOSSARY>
    {glossary_context}
    </GLOSSARY>
    ---

    Now, analyze the following feature description:
    ---
    <FEATURE_DESCRIPTION>
    {description}
    </FEATURE_DESCRIPTION>
    ---

    Provide your analysis as a JSON object with the following three keys:
    1. "is_geo_compliance_needed": boolean (true if it requires geo-specific compliance, false otherwise)
    2. "reasoning": string (a clear, concise explanation for your decision)
    3. "relevant_regulation": string (the name of the law or regulation if mentioned, otherwise "N/A")
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4-turbo",
            messages=[
                {"role": "system", "content": "You are an expert compliance analyst AI."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}
        )
        analysis_json = response.choices[0].message.content
        return json.loads(analysis_json)
    except Exception as e:
        print(f"An error occurred during API call or JSON parsing: {e}")
        return {
            "is_geo_compliance_needed": None,
            "reasoning": f"An error occurred: {str(e)}",
            "relevant_regulation": "N/A"
        }