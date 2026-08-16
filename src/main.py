import json
import os


def load_schema(filepath):
    """Loads a JSON schema file safely."""
    with open(filepath, 'r') as f:
        return json.load(f)


def compare_schemas(v1_path, v2_path):
    """Compares two schemas and detects added, removed, or modified fields."""
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

    # Print the Audit Report
    print("=" * 40)
    print("  REVSHIELD AI - SCHEMA AUDIT REPORT")
    print("=" * 40)
    print(f"Comparing v{schema_v1.get('version')} -> v{schema_v2.get('version')}\n")

    print(f"🟢 Added Fields ({len(added_fields)}):")
    for field in sorted(added_fields):
        print(f"   + {field}: {fields_v2[field]}")

    print(f"\n🔴 Removed Fields ({len(removed_fields)}):")
    for field in sorted(removed_fields):
        print(f"   - {field}: {fields_v1[field]}")

    print(f"\n🟡 Modified Types ({len(modified_fields)}):")
    for field, info in sorted(modified_fields.items()):
        print(f"   ~ {field}: changed from {info['old_type']} to {info['new_type']}")

    print("\n" + "=" * 40)


if __name__ == "__main__":
    v1 = "schemas/v1_schema.json"
    v2 = "schemas/v2_schema.json"
    compare_schemas(v1, v2)
