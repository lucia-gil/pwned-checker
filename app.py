import hashlib
import httpx
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from pathlib import Path

limiter = Limiter(key_func=get_remote_address)
app = FastAPI(title="PwnedChecker API")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


@app.get("/", response_class=HTMLResponse)
async def serve_frontend():
    html_path = Path(__file__).parent / "index.html"
    return HTMLResponse(content=html_path.read_text(encoding="utf-8"))


@app.post("/verificar")
@limiter.limit("10/minute")
async def verificar_contrasena(request: Request):
    try:
        body = await request.json()
        password = body.get("password", "")

        if not password:
            return JSONResponse({"error": "Contraseña vacía"}, status_code=400)

        # SHA-1 hash en mayúsculas
        sha1_hash = hashlib.sha1(password.encode("utf-8")).hexdigest().upper()
        prefix = sha1_hash[:5]
        suffix = sha1_hash[5:]

        # Consulta k-Anonymity a HIBP
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                f"https://api.pwnedpasswords.com/range/{prefix}",
                headers={"Add-Padding": "true"}
            )

        if response.status_code != 200:
            return JSONResponse(
                {"error": "No se pudo conectar con HIBP"},
                status_code=502
            )

        # Buscar la terminación del hash en la lista
        lines = response.text.strip().splitlines()
        veces = 0
        for line in lines:
            hash_suffix, count = line.split(":")
            if hash_suffix.upper() == suffix:
                veces = int(count)
                break

        return JSONResponse({
            "vulnerada": veces > 0,
            "veces": veces,
            "hash_prefix": prefix  # útil para debug / mostrar en UI
        })

    except httpx.TimeoutException:
        return JSONResponse({"error": "Timeout al contactar HIBP"}, status_code=504)
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
