"""
scanner.py — 4-tier cascade orchestrator.

Usage:
    from agora_code import scan

    catalog = await scan("./my-api")           # auto-detect best extractor
    catalog = await scan("./my-api", use_llm=True)  # allow LLM tier
    catalog = await scan("https://api.example.com") # remote OpenAPI

The cascade:
    Tier 1: OpenAPI spec  → universal, free, instant
    Tier 2: Python AST    → accurate, free, instant (Python only)
    Tier 3: LLM extract   → any language, opt-in (costs money)
    Tier 4: Regex fallback → always works, ~70% accurate
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

from agora_code.models import RouteCatalog
from agora_code.extractors import openapi, python_ast, regex


async def scan(
    target: str,
    *,
    use_llm: bool = False,
    llm_provider: str = "openai",
    llm_model: Optional[str] = None,
    edition: str = "community",
) -> RouteCatalog:
    """
    Scan a codebase or API URL and return a RouteCatalog.

    Args:
        target:       local directory path or remote URL
        use_llm:      enable Tier 3 LLM extraction (opt-in, costs money)
        llm_provider: "openai" | "gemini" (only used if use_llm=True)
        llm_model:    override default LLM model
        edition:      "community" | "enterprise"

    Returns:
        RouteCatalog with all discovered routes
    """
    # --- Tier 1: OpenAPI ---
    if openapi.can_handle(target):
        catalog = await openapi.extract(target)
        catalog.edition = edition
        _log(f"✅ Tier 1 (OpenAPI): {len(catalog)} routes from {target!r}")
        return catalog

    # --- Tier 2: Python AST ---
    if python_ast.can_handle(target):
        catalog = await python_ast.extract(target)
        catalog.edition = edition
        _log(f"✅ Tier 2 (Python AST): {len(catalog)} routes from {target!r}")
        return catalog

    # --- Tier 3: LLM (opt-in) ---
    if use_llm:
        from agora_code.extractors import llm as llm_extractor
        catalog = await llm_extractor.extract(
            target, provider=llm_provider, model=llm_model
        )
        catalog.edition = edition
        _log(f"✅ Tier 3 (LLM/{llm_provider}): {len(catalog)} routes from {target!r}")
        return catalog

    # --- Tier 4: Regex fallback ---
    catalog = await regex.extract(target)
    catalog.edition = edition
    _log(f"⚠️  Tier 4 (Regex): {len(catalog)} routes from {target!r} (70% accuracy)")
    return catalog


# --------------------------------------------------------------------------- #
#  Enterprise edition helper                                                   #
# --------------------------------------------------------------------------- #

async def scan_enterprise(
    target: str,
    *,
    supabase_url: str,
    supabase_key: str,
    project_id: str,
    use_llm: bool = False,
    llm_provider: str = "openai",
) -> RouteCatalog:
    """
    Enterprise edition: scan + persist catalog to Supabase.

    Routes are stored in a `route_catalogs` table for:
      - Multi-user shared access
      - Incremental recompile (skip unchanged files)
      - Future: org-level auth gating (Supabase Auth / WorkOS)

    Requires: pip install agora-code[enterprise]
    """
    try:
        from supabase import create_client
    except ImportError:
        raise ImportError("Install: pip install agora-code[enterprise]")

    catalog = await scan(
        target,
        use_llm=use_llm,
        llm_provider=llm_provider,
        edition="enterprise",
    )

    # Persist to Supabase
    client = create_client(supabase_url, supabase_key)
    rows = []
    for route in catalog.routes:
        rows.append({
            "project_id": project_id,
            "method": route.method,
            "path": route.path,
            "description": route.description,
            "params": [
                {"name": p.name, "type": p.type, "required": p.required,
                 "location": p.location}
                for p in route.params
            ],
            "tags": route.tags,
            "extractor": catalog.extractor,
            "source": catalog.source,
        })

    if rows:
        # Upsert on (project_id, method, path) — safe to re-run
        client.table("route_catalogs").upsert(
            rows,
            on_conflict="project_id,method,path",
        ).execute()

    _log(f"☁️  Enterprise: {len(catalog)} routes persisted to Supabase (project={project_id})")
    return catalog


def _log(msg: str) -> None:
    import sys
    print(msg, file=sys.stderr)
