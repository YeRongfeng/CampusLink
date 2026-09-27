"""Fixed AMap service proxy; SDK responses deliberately bypass ApiResponse."""
import httpx
import re
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse, Response
from app.common.config import get_settings

router = APIRouter(prefix='/_AMapService', include_in_schema=False)
PATHS = {
    'v3/assistant/inputtips', 'v3/place/text', 'v3/place/detail', 'v3/place/around',
    'v3/geocode/regeo', 'v3/geocode/geo', 'v3/ip', 'v3/coordinate/convert',
    'v5/place/text', 'v5/place/detail', 'v5/place/around',
}


def failure(status):
    return JSONResponse({'status': '0', 'info': 'MAP_SERVICE_UNAVAILABLE'}, status_code=status, headers={'Cache-Control': 'no-store'})


@router.get('/status')
def status():
    return JSONResponse({'enabled': bool(get_settings().amap_security_code.get_secret_value())}, headers={'Cache-Control': 'no-store'})


@router.get('/{path:path}')
async def proxy(path: str, request: Request):
    if path not in PATHS:
        return failure(404)
    if len(request.url.query) > 4096 or any(k.lower() == 'jscode' for k in request.query_params):
        return failure(400)
    callback = request.query_params.get('callback')
    if callback is not None and not re.fullmatch(r'[A-Za-z_$][\w$]*(?:\.[A-Za-z_$][\w$]*)*', callback, re.ASCII):
        return failure(400)
    secret = get_settings().amap_security_code.get_secret_value()
    if not secret:
        return failure(503)
    params = list(request.query_params.multi_items()) + [('jscode', secret)]
    try:
        async with httpx.AsyncClient(timeout=8, follow_redirects=False, trust_env=False) as client:
            async with client.stream('GET', f'https://restapi.amap.com/{path}', params=params) as upstream:
                if upstream.status_code != 200:
                    return failure(502)
                chunks = bytearray()
                async for chunk in upstream.aiter_bytes():
                    chunks.extend(chunk)
                    if len(chunks) > 2 * 1024 * 1024:
                        return failure(502)
                # Never reflect the injected secret, even if an upstream error echoes it.
                content = bytes(chunks).replace(secret.encode(), b'[redacted]')
                content_type = upstream.headers.get('content-type', 'application/json').split(';')[0]
                if content_type not in ('application/json', 'application/javascript', 'text/javascript'):
                    return failure(502)
                # AMap labels some JSONP responses as JSON. With nosniff, the SDK
                # cannot execute these unless the verified callback uses JS MIME.
                if callback:
                    if not content.lstrip().startswith(callback.encode() + b'('):
                        return failure(502)
                    content_type = 'application/javascript'
                return Response(content, media_type=content_type, headers={'Cache-Control': 'no-store', 'X-Content-Type-Options': 'nosniff'})
    except httpx.HTTPError:
        return failure(502)
