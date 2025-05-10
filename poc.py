import argparse
import subprocess
import sys
import re
import time
import urllib.parse
from html.parser import HTMLParser
from urllib.parse import urlparse

class CSRFTokenParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.csrf_token = None

    def handle_starttag(self, tag, attrs):
        attr_dict = dict(attrs)
        if tag.lower() == 'meta' and attr_dict.get('name') == 'csrf-token':
            self.csrf_token = attr_dict.get('content')

def parse_commit_url(commit_url):
    parsed = urlparse(commit_url)
    domain = f"{parsed.scheme}://{parsed.netloc}"
    match = re.search(r"/([^/]+/[^/]+)/-/commit/([a-fA-F0-9]+)", parsed.path)
    if not match:
        print("[ERROR] Could not extract namespace and commit ID from URL.")
        sys.exit(1)
    namespace, commit_id = match.groups()
    print(f"[INFO] Parsed domain: {domain}")
    print(f"[INFO] Parsed namespace: {namespace}")
    print(f"[INFO] Parsed commit ID: {commit_id}")
    return domain, namespace, commit_id

def get_csrf_token(domain, path, session):
    print(f"[INFO] Fetching CSRF token from: {domain}{path}")
    curl_cmd = [
        "curl", "-s", "-k",
        "-H", f"Cookie: _gitlab_session={session}",
        f"{domain}{path}"
    ]
    result = subprocess.run(curl_cmd, capture_output=True, text=True)
    html = result.stdout

    parser = CSRFTokenParser()
    parser.feed(html)

    if parser.csrf_token:
        print(f"[SUCCESS] CSRF Token found: {parser.csrf_token}")
    else:
        print("[ERROR] CSRF Token not found.")
        sys.exit(1)

    return parser.csrf_token

def read_note_from_file(filepath="text.txt"):
    try:
        with open(filepath, "r", encoding="utf-8") as file:
            content = file.read()
            print(f"[INFO] Loaded note from {filepath} ({len(content)} chars)")
            return content
    except Exception as e:
        print(f"[ERROR] Failed to read {filepath}: {e}")
        sys.exit(1)

def post_commit_note(domain, namespace, commit_id, session, csrf_token, note_text):
    post_url = f"{domain}/{namespace}/notes?html=true"
    encoded_note = urllib.parse.quote_plus(note_text)

    post_data = (
        f"authenticity_token={urllib.parse.quote_plus(csrf_token)}"
        f"&target_type=commit"
        f"&target_id={commit_id}"
        f"&note%5Bnote%5D={encoded_note}"
    )

    curl_cmd = [
        "curl", "-s", "-k",
        "-X", "POST",
        "-H", "Accept: application/json, text/plain, */*",
        "-H", "Content-Type: application/x-www-form-urlencoded",
        "-H", f"Cookie: _gitlab_session={session}",
        "--data", post_data,
        post_url
    ]

    print(f"[INFO] Posting comment to: {post_url}")
    try:
        result = subprocess.run(curl_cmd, capture_output=True, text=True)
        print("[INFO] Response (truncated):", result.stdout[:300], "..." if len(result.stdout) > 300 else "")
    except Exception as e:
        print(f"[ERROR] Failed to post note: {e}")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="Post GitLab commit note from file repeatedly.")
    parser.add_argument("--url", required=True, help="Full GitLab commit URL")
    parser.add_argument("--session", required=True, help="GitLab _gitlab_session cookie value")
    parser.add_argument("--file", default="text.txt", help="Path to text file for the note")
    parser.add_argument("--interval", type=int, default=60, help="Interval in seconds between posts (default: 60)")

    args = parser.parse_args()

    domain, namespace, commit_id = parse_commit_url(args.url)
    csrf_token = get_csrf_token(domain, f"/{namespace}/-/commit/{commit_id}", args.session)

    print(f"[LOOP] Starting post loop every {args.interval} seconds. Press Ctrl+C to stop.")
    try:
        while True:
            note_content = read_note_from_file(args.file)
            post_commit_note(domain, namespace, commit_id, args.session, csrf_token, note_content)
            print(f"[WAIT] Sleeping for {args.interval} seconds...\n")
            time.sleep(args.interval)
    except KeyboardInterrupt:
        print("\n[EXIT] Stopped by user.")

if __name__ == "__main__":
    main()
