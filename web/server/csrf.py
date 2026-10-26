from __future__ import annotations

import typing as t
from urllib.parse import urlsplit

from starlette.datastructures import Headers
from starlette.responses import JSONResponse
from starlette.status import HTTP_403_FORBIDDEN
from starlette.types import ASGIApp, Receive, Scope, Send

from web.server.exceptions import ApiException

SAFE_METHODS = frozenset({"GET", "HEAD", "OPTIONS"})


class CrossOriginProtectionMiddleware:
    """Rejects cross-origin state-changing requests to protect against CSRF.

    Browsers attach the `Sec-Fetch-Site` and `Origin` headers to cross-origin requests and
    they can't be forged by a web page, so a request is rejected when either of them indicates
    that it originated from a different site. Requests without either header don't come from a
    browser (e.g. curl or the VSCode extension) and are allowed through.
    """

    def __init__(self, app: ASGIApp, trusted_origins: t.Optional[t.Iterable[str]] = None) -> None:
        self.app = app
        self.trusted_origins = {origin.rstrip("/").lower() for origin in trusted_origins or []}

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] == "http" and not self._is_allowed(scope):
            response = JSONResponse(
                status_code=HTTP_403_FORBIDDEN,
                content=ApiException(
                    status_code=HTTP_403_FORBIDDEN,
                    message="Cross-origin request rejected",
                    origin="API -> csrf -> CrossOriginProtectionMiddleware",
                ).to_dict(),
            )
            await response(scope, receive, send)
            return
        await self.app(scope, receive, send)

    def _is_allowed(self, scope: Scope) -> bool:
        if scope["method"] in SAFE_METHODS:
            return True

        headers = Headers(scope=scope)
        origin = headers.get("origin")
        if origin is not None and origin.rstrip("/").lower() in self.trusted_origins:
            return True

        sec_fetch_site = headers.get("sec-fetch-site")
        if sec_fetch_site is not None:
            return sec_fetch_site in ("same-origin", "none")

        if origin is None:
            return True

        host = headers.get("host")
        return host is not None and urlsplit(origin).netloc.lower() == host.lower()
