import logging
from mitmproxy import http


def request(flow: http.HTTPFlow) -> None:
    if "oleg2002.com" in flow.request.pretty_host:
        flow.response = http.Response.make(
            200,
            b"Hello from mitmproxy 2109!",
            {"Content-Type": "text/html"}
        )


def response(flow: http.HTTPFlow) -> None:
    if "ya.ru" in flow.request.pretty_host:
        
        flow.response.text = "Hello! This response was modified by mitmproxy. 2025-09-11"

        flow.response.headers["X-Modified-By"] = "mitmproxy"

        # flow.response.text = '{"status":"ok","data":[]}'

