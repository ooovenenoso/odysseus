import ast
from pathlib import Path

from starlette.responses import RedirectResponse


def _load_serve_login():
    source = Path("app.py").read_text(encoding="utf-8")
    module = ast.parse(source)
    serve_login = next(
        node for node in module.body
        if isinstance(node, ast.AsyncFunctionDef) and node.name == "serve_login"
    )
    ast.fix_missing_locations(serve_login)
    class _App:
        def get(self, _path):
            return lambda func: func

    namespace = {
        "app": _App(),
        "_auth_disabled": lambda: True,
        "RedirectResponse": RedirectResponse,
        "_serve_html_with_nonce": lambda request, path: "login page",
        "abs_join": lambda *parts: "/".join(parts),
        "BASE_DIR": "/tmp/odysseus",
        "Request": object,
    }
    exec(compile(ast.Module(body=[serve_login], type_ignores=[]), "app.py", "exec"), namespace)
    return namespace["serve_login"]


async def test_login_route_redirects_home_when_auth_disabled():
    response = await _load_serve_login()(request=object())

    assert isinstance(response, RedirectResponse)
    assert response.status_code == 302
    assert response.headers["location"] == "/"
