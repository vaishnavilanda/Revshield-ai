import json
import os
import sys

def load_schema(filepath):
    """Loads a JSON schema file safely."""
    with open(filepath, 'r') as f:
        return json.load(f)

def generate_ai_mitigation(removed_fields, modified_fields):
    """
    Generates AI-powered developer mitigation strategies for breaking changes.
    Uses Gemini API if GEMINI_API_KEY is available, or structured AI heuristics.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    
    prompt = f"""
    You are an API Architect. Analyze these breaking schema changes and suggest mitigation steps:
    - Removed Fields: {list(removed_fields)}
    - Modified Fields: {modified_fields}
    
    Provide:
    1. Downstream Impact: Why this breaks API clients.
    2. Recommended Migration Strategy: How developers should update code/queries.
    """

    if api_key:
        try:
            from google import genai
            client = genai.Client(api_key=api_key)
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt,
            )
            return response.text
        except Exception as e:
            return f"⚠️ API Note: Could not call Gemini ({e}). Showing local fallback advice."

    # Heuristic Fallback Strategy (When API key is not present)
    advice = []
    if removed_fields:
        fields_str = ", ".join(sorted(removed_fields))
        advice.append(f"  • Removed Fields ({fields_str}):\n    - Downstream Impact: Clients expecting these fields will receive null pointer errors or missing key exceptions.\n    - Migration Strategy: Implement API v1 deprecation header and provide a fallback default in client SDKs before hard deletion.")
    
    if modified_fields:
        fields_str = ", ".join(sorted(modified_fields.keys()))
        advice.append(f"  • Type Alterations ({fields_str}):\n    - Downstream Impact: Type mismatch during JSON deserialization in client code.\n    - Migration Strategy: Use API middleware transformer to accept both legacy and new data types during transition period.")
        
    return "\n".join(advice)

def analyze_schema_changes(v1_path, v2_path):
    """Compares schemas, classifies risk, and attaches AI mitigation guidance."""
    schema_v1 = load_schema(v1_path)
    schema_v2 = load_schema(v2_path)
    
    fields_v1 = schema_v1.get("fields", {})
    fields_v2 = schema_v2.get("fields", {})
    
    keys_v1 = set(fields_v1.keys())
    keys_v2 = set(fields_v2.keys())
    
    added_fields = keys_v2 - keys_v1
    removed_fields = keys_v1 - keys_v2
    common_fields = keys_v1.intersection(keys_v2)
    
    modified_fields = {}
    for field in common_fields:
        if fields_v1[field] != fields_v2[field]:
            modified_fields[field] = {
                "old_type": fields_v1[field],
                "new_type": fields_v2[field]
            }
            
    is_breaking = len(removed_fields) > 0 or len(modified_fields) > 0
    
    print("=" * 55)
    print("  REVSHIELD AI - BREAKING CHANGE & MITIGATION ENGINE")
    print("=" * 55)
    print(f"Comparing v{schema_v1.get('version')} -> v{schema_v2.get('version')}\n")
    
    if is_breaking:
        print("🚨 STATUS: BREAKING CHANGES DETECTED (Deployment Blocked)\n")
    else:
        print("✅ STATUS: SAFE CHANGE (Backward Compatible)\n")
        
    print(f"🔴 CRITICAL (Removed Fields - {len(removed_fields)}):")
    for field in sorted(removed_fields):
        print(f"   - {field}: {fields_v1[field]}")
        
    print(f"\n🟡 HIGH RISK (Modified Types - {len(modified_fields)}):")
    for field, info in sorted(modified_fields.items()):
        print(f"   ~ {field}: changed from {info['old_type']} to {info['new_type']}")

    print(f"\n🟢 LOW RISK (Added Fields - {len(added_fields)}):")
    for field in sorted(added_fields):
        print(f"   + {field}: {fields_v2[field]}")
        
    if is_breaking:
        print("\n🤖 AI DEVELOPER MITIGATION & MIGRATION ADVICE:")
        mitigation_advice = generate_ai_mitigation(removed_fields, modified_fields)
        print(mitigation_advice)

    print("\n" + "=" * 55)
    
    return is_breaking

if __name__ == "__main__":
    v1 = "schemas/v1_schema.json"
    v2 = "schemas/v2_schema.json"
    
    is_breaking = analyze_schema_changes(v1, v2)
    
    if is_breaking:
        sys.exit(1)
    else:
        sys.exit(0)
        