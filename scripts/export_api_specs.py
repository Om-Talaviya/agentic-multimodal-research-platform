#!/usr/bin/env python3
"""Export OpenAPI schema and Postman v2.1 Collection from FastAPI Application."""

import json
import os
import sys

root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(root_dir, "packages", "shared", "src"))
sys.path.insert(0, os.path.join(root_dir, "packages", "database", "src"))
sys.path.insert(0, os.path.join(root_dir, "packages", "ai", "src"))
sys.path.insert(0, os.path.join(root_dir, "packages", "tools", "src"))
sys.path.insert(0, os.path.join(root_dir, "packages", "ingestion", "src"))
sys.path.insert(0, os.path.join(root_dir, "packages", "retrieval", "src"))
sys.path.insert(0, os.path.join(root_dir, "packages", "research", "src"))
sys.path.insert(0, os.path.join(root_dir, "packages", "agents", "src"))
sys.path.insert(0, os.path.join(root_dir, "apps", "api", "src"))

from fastapi.openapi.utils import get_openapi
from main import app


def export_openapi_and_postman():
    print("[*] Generating OpenAPI 3.1 specification from FastAPI app...")
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        openapi_version=app.openapi_version,
        description=app.description,
        routes=app.routes,
    )

    docs_dir = os.path.join(root_dir, "docs")
    os.makedirs(docs_dir, exist_ok=True)

    # 1. Write openapi.json
    openapi_path = os.path.join(docs_dir, "openapi.json")
    with open(openapi_path, "w", encoding="utf-8") as f:
        json.dump(openapi_schema, f, indent=2)
    print(f"[+] Exported OpenAPI schema -> {openapi_path}")

    # 2. Build Postman Collection v2.1
    postman_items = []
    paths = openapi_schema.get("paths", {})

    for path, methods in paths.items():
        for method, details in methods.items():
            tags = details.get("tags", ["General"])
            tag_name = tags[0] if tags else "General"
            summary = details.get("summary", f"{method.upper()} {path}")

            item = {
                "name": summary,
                "request": {
                    "method": method.upper(),
                    "header": [
                        {"key": "Content-Type", "value": "application/json"},
                        {"key": "Authorization", "value": "Bearer {{jwt_token}}", "type": "text"}
                    ],
                    "url": {
                        "raw": "{{base_url}}" + path,
                        "host": ["{{base_url}}"],
                        "path": [p for p in path.strip("/").split("/") if p]
                    },
                    "description": details.get("description", "")
                }
            }
            postman_items.append({"folder": tag_name, "item": item})

    # Group into folders by tag
    folders_dict = {}
    for entry in postman_items:
        folder_name = entry["folder"]
        if folder_name not in folders_dict:
            folders_dict[folder_name] = []
        folders_dict[folder_name].append(entry["item"])

    postman_folders = [
        {"name": fname, "item": fitems}
        for fname, fitems in folders_dict.items()
    ]

    postman_collection = {
        "info": {
            "_postman_id": "ai-research-os-collection-v28",
            "name": "AI Research OS - Complete REST API Collection",
            "description": "Comprehensive Postman collection for all 34 research phases.",
            "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
        },
        "item": postman_folders,
        "variable": [
            {"key": "base_url", "value": "http://localhost:8000", "type": "string"},
            {"key": "jwt_token", "value": "", "type": "string"}
        ]
    }

    postman_path = os.path.join(docs_dir, "Postman_Collection_AI_Research_OS.json")
    with open(postman_path, "w", encoding="utf-8") as f:
        json.dump(postman_collection, f, indent=2)
    print(f"[+] Exported Postman collection -> {postman_path}")
    print("[SUCCESS] API specifications exported successfully.")


if __name__ == "__main__":
    export_openapi_and_postman()
