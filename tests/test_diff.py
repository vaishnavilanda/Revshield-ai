import pytest
import json
from src.main import analyze_schema_changes

def test_breaking_change_detection(tmp_path):
    # Temporary v1 schema
    v1 = tmp_path / "v1.json"
    v1.write_text(json.dumps({"version": "1.0", "fields": {"id": "string", "amount": "float"}}))
    
    # Temporary v2 schema with removed field (breaking)
    v2 = tmp_path / "v2.json"
    v2.write_text(json.dumps({"version": "2.0", "fields": {"id": "string"}}))
    
    assert analyze_schema_changes(str(v1), str(v2)) == True

def test_non_breaking_change_detection(tmp_path):
    # Temporary v1 schema
    v1 = tmp_path / "v1.json"
    v1.write_text(json.dumps({"version": "1.0", "fields": {"id": "string"}}))
    
    # Temporary v2 schema with added field (safe)
    v2 = tmp_path / "v2.json"
    v2.write_text(json.dumps({"version": "2.0", "fields": {"id": "string", "email": "string"}}))
    
    assert analyze_schema_changes(str(v1), str(v2)) == False