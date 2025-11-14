# gmailbox/views.py
import os
import base64
from pathlib import Path

from django.shortcuts import redirect, render
from django.http import HttpResponseBadRequest, Http404
from django.conf import settings
from django.urls import reverse
from django.core.exceptions import ImproperlyConfigured

from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

# ---- Config ----
GMAIL_SCOPES = os.getenv(
    "GMAIL_SCOPES",
    "https://www.googleapis.com/auth/gmail.readonly"
).split()

# Detectar credentials.json en ubicaciones comunes
_CANDIDATES = [
    Path(settings.BASE_DIR) / "credentials.json",                    # raíz del proyecto (junto a manage.py)
    Path(settings.BASE_DIR) / "mibandejagmail" / "credentials.json", # dentro del paquete del proyecto
    Path(__file__).resolve().parent / "credentials.json",            # junto a este archivo (views.py)
]
_found = next((p for p in _CANDIDATES if p.exists()), None)
if not _found:
    raise ImproperlyConfigured(
        "No se encontró credentials.json. Probé en:\n" + "\n".join(str(p) for p in _CANDIDATES)
    )
CLIENT_SECRETS_FILE = str(_found)

SESSION_CREDS = "google_credentials"
SESSION_STATE = "oauth_state"


def _redirect_uri(request):
    """Construye el redirect URI exacto según el host con el que entraste."""
    uri = request.build_absolute_uri(reverse("google_callback")).rstrip("/")
    print("Redirect URI usado →", uri)  # DEBUG
    return uri


def logout_view(request):
    request.session.flush()  # Elimina todas las claves de sesión
    return redirect('home')
def home(request):
    return redirect("inbox")


def google_login(request):
    flow = Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE,
        scopes=GMAIL_SCOPES,
        redirect_uri=_redirect_uri(request),
    )
    auth_url, state = flow.authorization_url(
        access_type="offline",          # para obtener refresh_token
        include_granted_scopes="true",
        prompt="consent",               # útil en testing
    )
    request.session[SESSION_STATE] = state
    request.session.modified = True     # asegura que la cookie de sesión se escriba
    print("STATE guardado →", state)    # DEBUG
    return redirect(auth_url)


def google_callback(request):
    print("STATE recibido (query) →", request.GET.get("state"))  # DEBUG
    state = request.session.get(SESSION_STATE)
    if not state:
        return HttpResponseBadRequest("Falta estado de OAuth.")

    flow = Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE,
        scopes=GMAIL_SCOPES,
        state=state,
        redirect_uri=_redirect_uri(request),
    )
    try:
        flow.fetch_token(authorization_response=request.build_absolute_uri())
    except Exception as e:
        return HttpResponseBadRequest(f"No se pudo obtener el token: {e}")

    creds = flow.credentials
    request.session[SESSION_CREDS] = _creds_to_dict(creds)
    request.session.modified = True
    return redirect("inbox")


def inbox(request):
    creds = _load_creds_from_session(request)
    if not creds:
        return render(request, "gmailbox/inbox.html", {
            "needs_login": True,
            "messages": [],
            "query": "",
        })

    service = build("gmail", "v1", credentials=creds, cache_discovery=False)

    resp = service.users().messages().list(
        userId="me",
        labelIds=["INBOX"],
        maxResults=25,
        q=request.GET.get("q", None),
    ).execute()

    messages = []
    for item in resp.get("messages", []):
        msg = service.users().messages().get(
            userId="me", id=item["id"], format="metadata",
            metadataHeaders=["From", "Subject", "Date"]
        ).execute()
        headers = _headers_to_dict(msg.get("payload", {}).get("headers", []))
        messages.append({
            "id": msg["id"],
            "from": headers.get("From", ""),
            "subject": headers.get("Subject", "(sin asunto)"),
            "date": headers.get("Date", ""),
            "snippet": msg.get("snippet", ""),
        })

    return render(request, "gmailbox/inbox.html", {
        "needs_login": False,
        "messages": messages,
        "query": request.GET.get("q", ""),
    })


def message_detail(request, msg_id: str):
    creds = _load_creds_from_session(request)
    if not creds:
        return redirect("google_login")

    service = build("gmail", "v1", credentials=creds, cache_discovery=False)
    try:
        msg = service.users().messages().get(userId="me", id=msg_id, format="full").execute()
    except Exception:
        raise Http404("Mensaje no encontrado")

    headers = _headers_to_dict(msg.get("payload", {}).get("headers", []))
    body_text, body_html = _extract_message_body(msg.get("payload", {}))

    return render(request, "gmailbox/message_detail.html", {
        "id": msg_id,
        "headers": headers,
        "body_text": body_text,
        "body_html": body_html,
    })


# ---------- Helpers ----------
def _creds_to_dict(creds: Credentials):
    return {
        "token": creds.token,
        "refresh_token": creds.refresh_token,
        "token_uri": creds.token_uri,
        "client_id": creds.client_id,
        "client_secret": creds.client_secret,
        "scopes": creds.scopes,
        "expiry": creds.expiry.isoformat() if getattr(creds, "expiry", None) else None,
    }


def _load_creds_from_session(request):
    data = request.session.get(SESSION_CREDS)
    if not data:
        return None
    return Credentials(
        token=data.get("token"),
        refresh_token=data.get("refresh_token"),
        token_uri=data.get("token_uri"),
        client_id=data.get("client_id"),
        client_secret=data.get("client_secret"),
        scopes=data.get("scopes"),
    )


def _headers_to_dict(headers_list):
    d = {}
    for h in headers_list:
        n, v = h.get("name"), h.get("value")
        if n:
            d[n] = v
    return d


def _extract_message_body(payload):
    """Devuelve (text, html). Decodifica Base64 url-safe."""
    def _decode(body):
        data = body.get("data", "")
        if not data:
            return ""
        return base64.urlsafe_b64decode(data.encode("utf-8")).decode("utf-8", errors="ignore")

    mt = payload.get("mimeType")
    if mt == "text/plain":
        return _decode(payload.get("body", {})), ""
    if mt == "text/html":
        return "", _decode(payload.get("body", {}))

    parts = payload.get("parts", []) or []
    text, html = "", ""
    for p in parts:
        pmt = p.get("mimeType")
        if pmt == "text/plain" and not text:
            text = _decode(p.get("body", {}))
        elif pmt == "text/html" and not html:
            html = _decode(p.get("body", {}))
    return text, html


import csv
import io
import html as htmlmod
import re
from django.http import HttpResponse

def _html_to_text(html_str: str) -> str:
    """Convierte HTML a texto plano; usa bleach si está instalado, si no regex simple."""
    if not html_str:
        return ""
    try:
        import bleach
        return bleach.clean(html_str, tags=[], attributes={}, styles=[], strip=True)
    except Exception:
        # Fallback rápido sin bleach
        text = re.sub(r"<[^>]+>", "", html_str)
        return htmlmod.unescape(text)

def export_csv(request):
    """Descarga un CSV con correos del INBOX (aplica 'q' si se pasa)."""
    creds = _load_creds_from_session(request)
    if not creds:
        return redirect('google_login')

    service = build('gmail', 'v1', credentials=creds, cache_discovery=False)

    # parámetros
    q = request.GET.get('q')  # misma sintaxis que Gmail: is:unread, newer_than:7d, from:...
    try:
        max_rows = int(request.GET.get('max', 200))  # por defecto trae 200 correos
        max_rows = max(1, min(max_rows, 2000))       # límite de seguridad
    except ValueError:
        max_rows = 200

    # HttpResponse + BOM para que Excel abra en UTF-8
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="inbox.csv"'
    response.write('\ufeff')  # BOM

    writer = csv.writer(response)
    writer.writerow([
        'id', 'threadId', 'date', 'from', 'to', 'cc', 'bcc',
        'subject', 'labels', 'snippet', 'body_text'
    ])

    # paginación
    fetched = 0
    page_token = None
    while fetched < max_rows:
        batch_size = min(100, max_rows - fetched)
        lst = service.users().messages().list(
            userId='me',
            labelIds=['INBOX'],
            q=q,
            maxResults=batch_size,
            pageToken=page_token
        ).execute()

        ids = lst.get('messages', [])
        if not ids:
            break

        for item in ids:
            if fetched >= max_rows:
                break

            msg = service.users().messages().get(
                userId='me', id=item['id'], format='full'
            ).execute()

            headers = _headers_to_dict(msg.get('payload', {}).get('headers', []))
            body_text, body_html = _extract_message_body(msg.get('payload', {}))
            body = body_text or _html_to_text(body_html)

            labels = ",".join(msg.get('labelIds', []))

            writer.writerow([
                msg.get('id', ''),
                msg.get('threadId', ''),
                headers.get('Date', ''),
                headers.get('From', ''),
                headers.get('To', ''),
                headers.get('Cc', ''),
                headers.get('Bcc', ''),
                headers.get('Subject', ''),
                labels,
                msg.get('snippet', ''),
                body.replace('\r\n', '\n').replace('\r', '\n'),
            ])
            fetched += 1

        page_token = lst.get('nextPageToken')
        if not page_token:
            break

    return response
