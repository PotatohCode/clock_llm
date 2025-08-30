import os
import csv
import json
import requests

# Ollama API endpoint (default local installation)
OLLAMA_API_URL = os.getenv("OLLAMA_API_URL", "http://localhost:11434/api/chat")

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
    
    glossary_context = _load_glossary()

    prompt = f"""
    You are TikTok's regulatory compliance AI analyst. Your mission: FLAG features that require geo-specific compliance logic to prevent regulatory violations BEFORE launch.

    BUSINESS CONTEXT: TikTok operates under intense global regulatory scrutiny. Missing compliance requirements results in fines, bans, or shutdowns. You must identify compliance needs proactively.

    ANALYSIS PROCESS:
    1. **First, check against these 5 CORE REGULATIONS** (most relevant to TikTok):
    2. **Then, search the web** for additional current regulations relevant to the feature
    3. **Analyze all findings** to determine geo-compliance needs

    **CORE REFERENCE REGULATIONS TO CHECK FIRST:**

    1. **EU Digital Services Act (DSA)**
    - Reference: https://en.wikipedia.org/wiki/Digital_Services_Act
    - Focus: Content moderation, transparency, risk assessment obligations

    2. **California SB976 (2023–24) - Social Media Platform Duty to Children**  
    - Reference: https://leginfo.legislature.ca.gov/faces/billTextClient.xhtml?bill_id=202320240SB976
    - Focus: Personalized feeds, age verification, parental controls for minors

    3. **Florida SB3 (2024) - Online Protections for Minors**
    - Reference: https://www.flsenate.gov/Session/Bill/2024/3  
    - Focus: Age verification, parental consent, minor account restrictions

    4. **Utah Social Media Regulation Act**
    - Reference: https://en.wikipedia.org/wiki/Utah_Social_Media_Regulation_Act
    - Focus: Minor curfews, parental oversight, age verification

    5. **US Federal Law on Reporting CSAM (18 U.S.C. §2258A)**
    - Reference: https://www.law.cornell.edu/uscode/text/18/2258A
    - Focus: Child sexual abuse material detection and reporting requirements

    **ADDITIONAL WEB SEARCH STRATEGY:**
    After checking core regulations, search for:
    - Recent regulations (2020-2025) in relevant domains
    - Specific articles, sections, and requirements from major jurisdictions (EU, US states, UK, China, India, Brazil)
    - Both existing laws and pending legislation
    - Enforcement dates and compliance deadlines

    **HIGH-RISK DOMAINS TO SEARCH FOR:**
    - Content moderation and safety systems
    - Child safety and age verification  
    - Algorithm transparency and personalization
    - Data collection and privacy
    - Cross-border data transfers and localization

    FLAG IF EITHER:
    1. **Explicit Compliance**: Feature explicitly implements regulatory compliance
    2. **Implicit Risk**: Feature operates in domains with different legal requirements across jurisdictions

    **DO NOT FLAG:**
    - Pure UI/UX changes without data/content implications  
    - Internal engineering tools not touching user data
    - Standard A/B tests without compliance implications

    **ANALYSIS REQUIREMENTS:**
    - **Core + Current Laws**: Check core regulations first, then search for additional current laws with exact article/section numbers
    - **Jurisdictional Differences**: Explain why different regions require different handling  
    - **Never use generic terms**: Always cite specific acts/regulations
    - **Include sources**: Reference both core regulations and web search findings

    To help you understand the feature description, here is a glossary of internal terms:
    ---
    <GLOSSARY>
    {glossary_context}
    </GLOSSARY>
    ---

    Feature to analyze:
    ---
    {description}
    ---

    **REQUIRED PROCESS:**
    1. FIRST: Check if feature relates to any of the 5 CORE REGULATIONS listed above
    2. THEN: Search the web for additional relevant current regulations  
    3. FINALLY: Provide comprehensive analysis based on core regulations + web search findings

    Provide analysis as JSON with these exact keys:
    1. "is_geo_compliance_needed": boolean (true if geo-compliance required, false otherwise)
    2. "reasoning": string (detailed explanation citing specific core regulations and additional regulations found through web search, with article/section numbers, explaining jurisdictional differences)
    3. "relevant_regulation": string (comma-separated list including applicable core regulations and additional regulations found through search, with full citations)

    **EXAMPLE OUTPUT FORMAT:**
    {{"is_geo_compliance_needed": true, "reasoning": "This feature relates to [Core Regulation X] which requires [specific requirement]. Additional web search reveals [Current law Y] mandates [different requirement in another jurisdiction]. These regulatory differences necessitate jurisdiction-specific implementation because [explain differences].", "relevant_regulation": "[Applicable core regulations], [Additional regulations found through search with citations]"}}

    Now, check the core regulations first, then search the web for additional relevant regulations, then provide your JSON analysis.
    """

    try:
        # Prepare the request for Ollama
        payload = {
            "model": "deepseek-r1",
            "messages": [
                {"role": "system", "content": "You are an expert compliance analyst AI."},
                {"role": "user", "content": prompt}
            ],
            "stream": False,
            "format": "json"  # Request JSON response format
        }
        
        # Make the API call to Ollama
        response = requests.post(OLLAMA_API_URL, json=payload)
        response.raise_for_status()  # Raise an exception for bad status codes
        
        # Parse the response
        result = response.json()
        
        # Extract the message content from Ollama's response
        if 'message' in result and 'content' in result['message']:
            analysis_json = result['message']['content']
        else:
            # Fallback if response structure is different
            analysis_json = result.get('response', '{}')
        
        return json.loads(analysis_json)
        
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to Ollama. Make sure Ollama is running locally.")
        print("Start Ollama with: ollama serve")
        print("Then pull the model with: ollama pull deepseek-r1")
        return {
            "is_geo_compliance_needed": None,
            "reasoning": "Could not connect to Ollama service. Please ensure Ollama is running.",
            "relevant_regulation": "N/A"
        }
    except requests.exceptions.RequestException as e:
        print(f"An error occurred during Ollama API call: {e}")
        return {
            "is_geo_compliance_needed": None,
            "reasoning": f"API request error: {str(e)}",
            "relevant_regulation": "N/A"
        }
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON response from Ollama: {e}")
        return {
            "is_geo_compliance_needed": None,
            "reasoning": f"JSON parsing error: {str(e)}",
            "relevant_regulation": "N/A"
        }
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return {
            "is_geo_compliance_needed": None,
            "reasoning": f"Unexpected error: {str(e)}",
            "relevant_regulation": "N/A"
        }