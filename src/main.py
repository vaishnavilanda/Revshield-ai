import json
import sys

def load_schema(filepath):
    """Loads a JSON schema file safely."""
    with open(filepath, 'r') as f:
        return json.load(f)

def analyze_schema_changes(v1_path, v2_path):
    """
    Compares two schemas, classifies changes by severity, 
    and determines if the release contains breaking changes.
    """
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
            
    # Classify Risk Levels
    # Breaking = Any removed field OR modified data type
    is_breaking = len(removed_fields) > 0 or len(modified_fields) > 0
    
    print("=" * 45)
    print("  REVSHIELD AI - BREAKING CHANGE GUARDRAIL")
    print("=" * 45)
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
        
    print("\n" + "=" * 45)
    
    return is_breaking

if __name__ == "__main__":
    v1 = "schemas/v1_schema.json"
    v2 = "schemas/v2_schema.json"
    
    is_breaking = analyze_schema_changes(v1, v2)
    
    # Exit with code 1 if breaking changes exist (blocks CI/CD builds)
    if is_breaking:
        sys.exit(1)
    else:
        sys.exit(0)
        