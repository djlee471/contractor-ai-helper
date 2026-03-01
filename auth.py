import os
import secrets
from datetime import datetime, timedelta, timezone

import psycopg
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, RedirectResponse
from starlette.requests import Request

from access_codes import compute_hmac, normalize_access_code

app = FastAPI()

COOKIE_NAME = os.getenv("SESSION_COOKIE_NAME", "ns_session")
SESSION_DAYS = int(os.getenv("SESSION_DAYS", "30"))


def _db_conn():
    dsn = os.getenv("DATABASE_URL")
    if dsn:
        return psycopg.connect(dsn, autocommit=True)
    return psycopg.connect(
        host=os.getenv("DB_HOST", "cloudsql-proxy"),
        port=int(os.getenv("DB_PORT", "5432")),
        dbname=os.getenv("DB_NAME", "contractor_prod"),
        user=os.getenv("DB_USER", "contractor_app"),
        password=os.getenv("DB_PASSWORD"),
        autocommit=True,
    )


def _create_session(contractor_id: int) -> tuple[str, datetime]:
    token = secrets.token_urlsafe(32)
    expires_at = datetime.now(timezone.utc) + timedelta(days=SESSION_DAYS)
    q = """
        INSERT INTO public.client_sessions
            (contractor_id, expires_at, session_token, user_agent_hash, ip_hash)
        VALUES (%s, %s, %s, NULL, NULL)
        RETURNING id
    """
    with _db_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(q, (contractor_id, expires_at, token))
            cur.fetchone()
    return token, expires_at


@app.get("/auth/login", response_class=HTMLResponse)
async def login_form(error: str = ""):
    error_html = f'<p style="color:red">{error}</p>' if error else ""
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Build Answers</title>
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;600;700&display=swap');
            
            body {{
                font-family: "Manrope", sans-serif;
                background-color: #FAFAFA;
                max-width: 400px;
                margin: 100px auto;
                padding: 0 20px;
            }}
            h2 {{ font-size: 2rem; font-weight: 6500; color: #94A3B8; margin-bottom: 1.75rem; }}
            p {{ color: #64748B; font-size: 0.95rem; margin-bottom: 1.75rem; }}
            input {{ width: 100%; padding: 10px; margin-bottom: 12px; border: 1px solid #CBD5E1; border-radius: 8px; font-family: "Manrope", sans-serif; font-size: 0.95rem; box-sizing: border-box; }}
            button {{ width: 100%; padding: 10px; background: #420741; color: white; border: none; border-radius: 8px; font-family: "Manrope", sans-serif; font-size: 0.95rem; font-weight: 600; cursor: pointer; }}
            button:hover {{ background: #5a0a58; }}
            .error {{ color: #DC2626; font-size: 0.875rem; margin-bottom: 1rem; }}
        </style>
    </head>
    <body>
        <h2>Build Answers</h2>
        <p>Enter the access code provided by your contractor.</p>
        {error_html}
        <form method="POST" action="/auth/login">
            <input type="password" name="code" placeholder="Access code" autofocus />
            <button type="submit">Continue</button>
        </form>
    </body>
    </html>
    """

@app.post("/auth/login")
async def do_login(request: Request):
    form = await request.form()
    code = form.get("code", "")

    normalized = normalize_access_code(code)
    if not normalized:
        return RedirectResponse("/auth/login?error=Please+enter+an+access+code", status_code=303)

    try:
        h = compute_hmac(normalized)
    except Exception:
        return RedirectResponse("/auth/login?error=Server+configuration+error", status_code=303)

    q = """
        SELECT id, subscription_status, trial_ends_at
        FROM public.contractors
        WHERE access_code_hmac = %s
        LIMIT 1
    """
    with _db_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(q, (h,))
            row = cur.fetchone()

    if not row:
        return RedirectResponse("/auth/login?error=Invalid+access+code", status_code=303)

    contractor_id, status, trial_ends_at = row
    now = datetime.now(timezone.utc)

    if status == "active":
        pass
    elif status == "trial":
        if trial_ends_at is None or trial_ends_at <= now:
            return RedirectResponse("/auth/login?error=Trial+has+ended", status_code=303)
    else:
        return RedirectResponse("/auth/login?error=Access+code+not+active", status_code=303)

    session_token, expires_at = _create_session(int(contractor_id))

    response = RedirectResponse("/", status_code=303)
    response.set_cookie(
        key=COOKIE_NAME,
        value=session_token,
        max_age=SESSION_DAYS * 24 * 60 * 60,
        secure=True,
        httponly=False,
        samesite="lax",
        path="/",
    )
    return response


@app.post("/auth/logout")
async def logout():
    response = RedirectResponse("/auth/login", status_code=303)
    response.delete_cookie(COOKIE_NAME)
    return response