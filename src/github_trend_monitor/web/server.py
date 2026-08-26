import csv
import json
import os
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

PROJECT_ROOT = Path(__file__).resolve().parents[3]
DATA_DIR = PROJECT_ROOT / "data"
STATIC_DIR = Path(__file__).parent / "static"


def read_repositories():
    repositories = {}
    for csv_path in sorted(DATA_DIR.glob("*.csv")):
        if csv_path.name == "all_repos.csv":
            continue
        with csv_path.open("r", encoding="utf-8-sig", newline="") as file:
            for row in csv.DictReader(file):
                if not row.get("id") or row["id"] in repositories:
                    continue
                repositories[row["id"]] = {
                    "id": row.get("id", ""),
                    "name": row.get("name", ""),
                    "description": row.get("description", ""),
                    "url": row.get("url", ""),
                    "stars": int(row.get("stars") or 0),
                    "forks": int(row.get("forks") or 0),
                    "language": row.get("language") or "Unknown",
                    "topics": [item.strip() for item in (row.get("topics") or "").split(",") if item.strip()],
                    "created_at": row.get("created_at", ""),
                    "first_seen": row.get("first_seen", ""),
                    "is_active": str(row.get("is_active", "true")).lower() == "true",
                    "domains": [item.strip() for item in (row.get("domains") or "").split(",") if item.strip()],
                }
    return list(repositories.values())


def dashboard_payload():
    repositories = read_repositories()
    domains = sorted({domain for repo in repositories for domain in repo["domains"]})
    languages = sorted({repo["language"] for repo in repositories if repo["language"] != "Unknown"})
    return {"repositories": repositories, "domains": domains, "languages": languages}


class DashboardHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(STATIC_DIR), **kwargs)

    def do_GET(self):
        path = urlparse(self.path).path
        if path == "/api/data":
            payload = json.dumps(dashboard_payload(), ensure_ascii=False).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Cache-Control", "no-store")
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)
            return
        if path == "/":
            self.path = "/index.html"
        return super().do_GET()

    def do_POST(self):
        path = urlparse(self.path).path
        if path != "/api/insights":
            self.send_error(404)
            return

        from github_trend_monitor.analysis.ai_analyzer import generate_insights

        try:
            result = generate_insights(force=True)
            payload = json.dumps(result, ensure_ascii=False).encode("utf-8")
            self.send_response(200)
        except Exception as error:
            payload = json.dumps({"error": str(error)}, ensure_ascii=False).encode("utf-8")
            self.send_response(500)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def log_message(self, format, *args):
        print(f"[web] {self.address_string()} - {format % args}")


def main():
    port = int(os.getenv("PORT", "8070"))
    server = ThreadingHTTPServer(("127.0.0.1", port), DashboardHandler)
    print(f"GitHub Trend Monitor: http://127.0.0.1:{port}")
    print("按 Ctrl+C 停止服务")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n服务已停止")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
