import os
from pathlib import Path

import httpx
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel


load_dotenv()

PROJECT_ROOT = Path(__file__).resolve().parent
PUBLIC_DIR = PROJECT_ROOT / "public"

app = FastAPI(
    title="고양 스마트시티즌 방문자 카운터",
    description="로컬 FastAPI와 Vercel이 같은 Supabase 방문자 수를 공유하는 예제",
)


def mount_public_files(application: FastAPI, directory: Path) -> None:
    """Serve the local web page when the static directory is available.

    Vercel serves public/** from its CDN and does not include that directory in
    the Python function bundle, so the function must also import without it.
    """
    if directory.is_dir():
        application.mount(
            "/",
            StaticFiles(directory=directory, html=True),
            name="public",
        )


class VisitResponse(BaseModel):
    count: int


class SupabaseConfigurationError(RuntimeError):
    """Raised when the server-only Supabase configuration is incomplete."""


def get_supabase_settings() -> tuple[str, str]:
    supabase_url = os.getenv("SUPABASE_URL", "").rstrip("/")
    secret_key = os.getenv("SUPABASE_SECRET_KEY", "")

    if not supabase_url or not secret_key:
        raise SupabaseConfigurationError(
            "SUPABASE_URL과 SUPABASE_SECRET_KEY 환경변수가 필요합니다."
        )

    return supabase_url, secret_key


def parse_counter_value(payload: object) -> int:
    """Normalize the scalar JSON value returned by the Supabase RPC endpoint."""
    if isinstance(payload, bool):
        raise ValueError("방문자 수 응답 형식이 올바르지 않습니다.")

    if isinstance(payload, int):
        return payload

    if isinstance(payload, str) and payload.isdigit():
        return int(payload)

    raise ValueError("방문자 수 응답 형식이 올바르지 않습니다.")


async def increment_page_view(page_key: str = "home") -> int:
    supabase_url, secret_key = get_supabase_settings()

    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.post(
            f"{supabase_url}/rest/v1/rpc/increment_page_view",
            headers={
                "apikey": secret_key,
                "Content-Type": "application/json",
            },
            json={"target_key": page_key},
        )
        response.raise_for_status()

    return parse_counter_value(response.json())


@app.get("/api/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/visit", response_model=VisitResponse)
async def record_visit() -> VisitResponse:
    try:
        count = await increment_page_view()
    except SupabaseConfigurationError as exc:
        raise HTTPException(
            status_code=503,
            detail="서버의 Supabase 환경변수를 확인해 주세요.",
        ) from exc
    except (httpx.HTTPError, ValueError) as exc:
        raise HTTPException(
            status_code=502,
            detail="방문자 수 서버에 잠시 연결할 수 없습니다.",
        ) from exc

    return VisitResponse(count=count)


# API routes are declared first so this catch-all mount only handles the web page.
mount_public_files(app, PUBLIC_DIR)
