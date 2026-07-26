import json, os, time
from pathlib import Path
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from openai import OpenAI
from .config import LLM_API_KEY, LLM_BASE_URL, LLM_MODEL, CONFIG, ROOT

SCOPES = ["https://www.googleapis.com/auth/blogger"]
CLIENT_SECRET = ROOT / "client_secret.json"
BLOG_ID = os.environ.get("BLOG_ID", "")
try:
    BLOG_ID = str(int(float(BLOG_ID)))
except (ValueError, TypeError):
    pass


def _token_path() -> Path:
    return ROOT / "token_blogger.json"


def _get_service():
    token_path = _token_path()
    creds = None
    if token_path.exists():
        creds = Credentials.from_authorized_user_file(str(token_path), SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(str(CLIENT_SECRET), SCOPES)
            creds = flow.run_local_server(port=0)
        token_path.write_text(creds.to_json(), encoding="utf-8")
    return build("blogger", "v3", credentials=creds)


def expand_article(script_data: dict) -> dict:
    full_text = script_data.get("full_text", "")

    user_msg = (
        f"Teks video pendek berikut:\n\n{full_text}\n\n"
        f"Niche: {CONFIG['niche']}\n"
        f"Tulis artikel blog 500-700 kata dalam bahasa Indonesia berdasarkan teks di atas. "
        f"Kembangkan dengan penjelasan tambahan yang relevan, fakta pendukung, dan kesimpulan. "
        f"Gunakan format HTML paragraf (<p>). Beri judul artikel yang engaging (>40 karakter). "
        f"Jangan tambahkan informasi palsu. Kembalikan ONLY valid JSON: "
        f"{{\"title\": \"...\", \"content\": \"<p>...</p>\"}}"
    )

    client = OpenAI(api_key=LLM_API_KEY, base_url=LLM_BASE_URL)
    resp = client.chat.completions.create(
        model=LLM_MODEL,
        max_tokens=2000,
        response_format={"type": "json_object"},
        messages=[{"role": "user", "content": user_msg}],
    )
    raw = resp.choices[0].message.content
    article = json.loads(raw)

    tags = script_data.get("tags", [])
    article["tags"] = tags[:5]
    article["video_id"] = script_data.get("video_id", "")
    return article


def post(article: dict) -> str | None:
    if not BLOG_ID:
        print("    BLOG_ID not set, skipping")
        return None

    service = _get_service()

    content = article["content"]
    if article.get("video_id"):
        yt_embed = (
            '<div style="text-align:center;margin:20px 0;">'
            '<iframe width="560" height="315" '
            f'src="https://www.youtube.com/embed/{article["video_id"]}" '
            'frameborder="0" allowfullscreen></iframe></div>'
        )
        content = yt_embed + content

    body = {
        "kind": "blogger#post",
        "title": article["title"],
        "content": content,
        "labels": article.get("tags", []),
    }

    for attempt in range(3):
        try:
            result = service.posts().insert(blogId=BLOG_ID, body=body).execute()
            url = result.get("url", "")
            print(f"    blog post published: {url}")
            return url
        except Exception as e:
            if attempt < 2:
                time.sleep(2 ** attempt)
            else:
                print(f"    blog post failed: {e}")
    return None


def publish(script_data: dict) -> str | None:
    print("  Expanding script to blog article...")
    article = expand_article(script_data)
    print(f"    title: {article['title']}")
    return post(article)
