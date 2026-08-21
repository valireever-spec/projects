#!/usr/bin/env python3
"""
Upload a rendered video to YouTube via the Data API v3.

The metadata (title / description / tags) is built from the script JSON with the
same logic as the upload sheet, and the video is gated through the same
`validate_script` check — an unverified script won't upload without --force.

One-time setup:
  1. Google Cloud Console → create a project → enable "YouTube Data API v3".
  2. APIs & Services → Credentials → Create OAuth client ID → type "Desktop app"
     → download the JSON to tools/client_secret.json.
  3. .venv-video/bin/pip install -r tools/requirements.txt

Usage:
  python tools/upload.py romanian_scripts/04_cancer_col_uterin.json
  python tools/upload.py <json> --privacy unlisted
  python tools/upload.py <json> --publish-at 2026-09-01T09:00:00Z   # scheduled public

Defaults to a PRIVATE upload so you can review and set the "Altered content"
(AI) disclosure in YouTube Studio before publishing — that flag is not settable
via the API.
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import make_video as mv  # noqa: E402  (reuse .env loader, hashtags, credits, validator)

TOOLS         = Path(__file__).resolve().parent
CLIENT_SECRET = TOOLS / "client_secret.json"
TOKEN         = TOOLS / ".youtube_token.json"
SCOPES        = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube.force-ssl",  # thumbnails.set
]
NEWS_POLITICS = "25"   # YouTube categoryId


# Title / description / tags come from the shared builder in make_video, so the
# uploaded metadata is byte-identical to the generated upload sheet.
youtube_fields = mv.youtube_fields


def get_service():
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build

    creds = None
    if TOKEN.exists():
        creds = Credentials.from_authorized_user_file(str(TOKEN), SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not CLIENT_SECRET.exists():
                raise SystemExit(
                    f"Missing {CLIENT_SECRET}. Create OAuth 'Desktop app' credentials "
                    "in Google Cloud Console (with YouTube Data API v3 enabled) and "
                    "download them there. See the header of this file.")
            flow = InstalledAppFlow.from_client_secrets_file(str(CLIENT_SECRET), SCOPES)
            creds = flow.run_local_server(port=0)   # opens a browser for consent
        TOKEN.write_text(creds.to_json())
    return build("youtube", "v3", credentials=creds)


def upload(service, mp4: Path, title: str, description: str, tags: list[str],
           privacy: str, publish_at: str | None, thumb: Path | None) -> str:
    from googleapiclient.http import MediaFileUpload

    status_body = {"privacyStatus": privacy, "selfDeclaredMadeForKids": False}
    if publish_at:                       # scheduled → must be private + publishAt
        status_body["privacyStatus"] = "private"
        status_body["publishAt"] = publish_at
    body = {
        "snippet": {"title": title, "description": description, "tags": tags,
                    "categoryId": NEWS_POLITICS,
                    "defaultLanguage": "ro", "defaultAudioLanguage": "ro"},
        "status": status_body,
    }
    media = MediaFileUpload(str(mp4), chunksize=-1, resumable=True, mimetype="video/mp4")
    request = service.videos().insert(part="snippet,status", body=body, media_body=media)

    print("  uploading...")
    response = None
    while response is None:
        progress, response = request.next_chunk()
        if progress:
            print(f"    {int(progress.progress() * 100)}%")
    video_id = response["id"]
    print(f"  video id: {video_id}")

    if thumb and thumb.exists():
        try:
            service.thumbnails().set(
                videoId=video_id, media_body=MediaFileUpload(str(thumb))).execute()
            print("  thumbnail set")
        except Exception as e:
            print(f"  thumbnail skipped (channel may need verification): {e}")
    return video_id


def main() -> None:
    ap = argparse.ArgumentParser(description="Upload a rendered video to YouTube.")
    ap.add_argument("script", help="the script JSON (its rendered .mp4 must exist in --out-dir)")
    ap.add_argument("--out-dir", default="output", help="where the .mp4 / thumbnail live")
    ap.add_argument("--privacy", default="private",
                    choices=["private", "unlisted", "public"],
                    help="default private — review + set AI disclosure before going public")
    ap.add_argument("--publish-at", default="",
                    help="ISO-8601 UTC time to auto-publish (e.g. 2026-09-01T09:00:00Z)")
    ap.add_argument("--force", action="store_true", help="upload even if validation fails")
    args = ap.parse_args()

    mv._load_dotenv()
    data    = json.loads(Path(args.script).read_text(encoding="utf-8"))
    slug    = data.get("slug", Path(args.script).stem)
    out_dir = Path(args.out_dir)
    mp4     = out_dir / f"{slug}.mp4"
    thumb   = out_dir / f"{slug}_thumb.jpg"

    if not mp4.exists():
        raise SystemExit(f"{mp4} not found — render it first (tools/make_video.py {args.script}).")

    print(f"=== {slug} ===")
    if not mv._report_validation(slug, mv.validate_script(data)) and not args.force:
        raise SystemExit("Refusing to upload — fix validation errors or pass --force.")

    title, description, tags = youtube_fields(data, out_dir, slug)
    print(f"  title: {title}")
    print(f"  privacy: {args.privacy}" + (f", publishAt {args.publish_at}" if args.publish_at else ""))

    service = get_service()
    video_id = upload(service, mp4, title, description, tags,
                      args.privacy, args.publish_at or None,
                      thumb if thumb.exists() else None)

    print(f"\nUploaded → https://studio.youtube.com/video/{video_id}/edit")
    print("⚠️ In Studio, set 'Altered content = Yes' (AI voice) — this disclosure "
          "cannot be set via the API — then review and publish.")


if __name__ == "__main__":
    main()
