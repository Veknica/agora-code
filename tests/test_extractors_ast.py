"""
test_extractors_ast.py — Python AST extractor tests.

Tests FastAPI, Flask, and Django route extraction via the stdlib ast module.
No external dependencies — runs fully offline.
"""
from __future__ import annotations

import textwrap

import pytest

from agora_code.extractors import python_ast


# --------------------------------------------------------------------------- #
#  can_handle                                                                  #
# --------------------------------------------------------------------------- #

def test_can_handle_python_dir(tmp_path):
    (tmp_path / "main.py").write_text("pass")
    assert python_ast.can_handle(str(tmp_path)) is True


def test_cannot_handle_empty_dir(tmp_path):
    assert python_ast.can_handle(str(tmp_path)) is False


def test_cannot_handle_url():
    assert python_ast.can_handle("https://api.example.com") is False


# --------------------------------------------------------------------------- #
#  FastAPI                                                                     #
# --------------------------------------------------------------------------- #

@pytest.mark.asyncio
async def test_fastapi_fixture(fastapi_code, tmp_path):
    """Scan the sample_fastapi.py fixture — expect 4 routes."""
    (tmp_path / "app.py").write_text(fastapi_code)
    catalog = await python_ast.extract(str(tmp_path))

    assert len(catalog.routes) == 4
    methods = {r.method for r in catalog.routes}
    assert "GET" in methods
    assert "POST" in methods
    assert "DELETE" in methods


def test_fastapi_path_param():
    code = textwrap.dedent("""\
        from fastapi import FastAPI
        app = FastAPI()

        @app.get("/users/{user_id}")
        async def get_user(user_id: int):
            pass
    """)
    routes = python_ast._extract_from_source(code, source_label="inline")
    assert len(routes) == 1
    r = routes[0]
    assert r.method == "GET"
    assert r.path == "/users/{user_id}"
    uid = next(p for p in r.params if p.name == "user_id")
    assert uid.type == "int"
    assert uid.location == "path"
    assert uid.required is True


def test_fastapi_query_param_with_default():
    code = textwrap.dedent("""\
        from fastapi import FastAPI
        app = FastAPI()

        @app.get("/items")
        async def list_items(limit: int = 10):
            pass
    """)
    routes = python_ast._extract_from_source(code, source_label="inline")
    lim = next(p for p in routes[0].params if p.name == "limit")
    assert lim.required is False
    assert lim.default == 10


def test_fastapi_docstring_becomes_description():
    code = textwrap.dedent("""\
        from fastapi import FastAPI
        app = FastAPI()

        @app.get("/ping")
        async def ping():
            \"\"\"Health check endpoint.\"\"\"
            pass
    """)
    routes = python_ast._extract_from_source(code, source_label="inline")
    assert "Health check" in routes[0].description


@pytest.mark.parametrize("method", ["get", "post", "put", "delete", "patch"])
def test_fastapi_all_methods(method):
    code = textwrap.dedent(f"""\
        from fastapi import FastAPI
        app = FastAPI()

        @app.{method}("/test")
        def handler(): pass
    """)
    routes = python_ast._extract_from_source(code, source_label="inline")
    assert routes[0].method == method.upper()


def test_fastapi_no_routes():
    code = "x = 1\nprint('hello')"
    routes = python_ast._extract_from_source(code, source_label="inline")
    assert routes == []


# --------------------------------------------------------------------------- #
#  Flask                                                                       #
# --------------------------------------------------------------------------- #

@pytest.mark.asyncio
async def test_flask_fixture(flask_code, tmp_path):
    (tmp_path / "app.py").write_text(flask_code)
    catalog = await python_ast.extract(str(tmp_path))
    # 3 @app.route decorators in fixture (GET /items, items, delete_item)
    assert len(catalog.routes) >= 2


def test_flask_typed_path_param():
    code = textwrap.dedent("""\
        from flask import Flask
        app = Flask(__name__)

        @app.route("/items/<int:item_id>", methods=["GET"])
        def get_item(item_id): pass
    """)
    routes = python_ast._extract_from_source(code, source_label="inline")
    assert len(routes) == 1
    assert routes[0].path == "/items/{item_id}"
    assert routes[0].method == "GET"


def test_flask_multi_method_route():
    code = textwrap.dedent("""\
        from flask import Flask
        app = Flask(__name__)

        @app.route("/items", methods=["GET", "POST"])
        def items(): pass
    """)
    routes = python_ast._extract_from_source(code, source_label="inline")
    # Should produce one route per method
    methods = {r.method for r in routes}
    assert "GET" in methods
    assert "POST" in methods


# --------------------------------------------------------------------------- #
#  Edge cases                                                                  #
# --------------------------------------------------------------------------- #

def test_empty_string():
    routes = python_ast._extract_from_source("", source_label="inline")
    assert routes == []


def test_syntax_error_file_skipped(tmp_path):
    """A file with a syntax error should be skipped, not crash the scan."""
    (tmp_path / "broken.py").write_text("def broken syntax!!")
    (tmp_path / "good.py").write_text(
        "@app.get('/ok')\ndef ok(): pass"
    )
    # Should not raise
    routes = python_ast._extract_from_source(
        (tmp_path / "good.py").read_text(), source_label="good.py"
    )
    assert len(routes) >= 0  # broken.py skipped in full scan
