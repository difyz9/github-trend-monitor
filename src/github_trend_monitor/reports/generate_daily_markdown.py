from datetime import datetime
from pathlib import Path

import pandas as pd


DATA_DIR = Path("data")
REPORTS_DIR = Path("reports")
REPOSITORY_COLUMNS = [
    "id", "name", "description", "url", "stars", "forks", "language",
    "topics", "created_at", "first_seen", "is_active", "domains",
]


def load_repositories() -> pd.DataFrame:
    repository_file = DATA_DIR / "all_repos.csv"
    if not repository_file.exists():
        return pd.DataFrame()

    repositories = pd.read_csv(repository_file)
    if "stars" not in repositories.columns:
        repositories = pd.read_csv(repository_file, header=None, names=REPOSITORY_COLUMNS)
    return repositories.sort_values("stars", ascending=False).head(20)


def format_repository_row(repository: pd.Series) -> str:
    name = repository.get("name", "Unknown")
    stars = repository.get("stars", 0)
    domain = repository.get("domains", repository.get("domain", "Uncategorized"))
    url = repository.get("url", "")
    if isinstance(url, str) and url:
        return f"| [{name}]({url}) | {stars} | {domain} |"
    return f"| {name} | {stars} | {domain} |"


def main() -> None:
    generated_at = datetime.now().astimezone()
    repositories = load_repositories()
    REPORTS_DIR.mkdir(exist_ok=True)
    report_path = REPORTS_DIR / f"daily-trends-{generated_at:%Y-%m-%d}.md"

    lines = [
        "# GitHub AI Trend Daily Report",
        "",
        f"Generated: {generated_at:%Y-%m-%d %H:%M %Z}",
        "",
        "## Top Repositories",
        "",
    ]

    if repositories.empty:
        lines.append("No repository data is available yet.")
    else:
        lines.extend([
            "| Repository | Stars | Domain |",
            "| --- | ---: | --- |",
            *(format_repository_row(repository) for _, repository in repositories.iterrows()),
        ])

    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Daily Markdown report written to {report_path}")


if __name__ == "__main__":
    main()