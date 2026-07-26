import json
from datetime import datetime
import os
import sys


def empty_author(reason: str) -> dict:
    return {
        "name": "",
        "citedby": 0,
        "updated": str(datetime.now()),
        "publications": {},
        "crawler_status": "skipped",
        "crawler_message": reason,
    }


def fetch_author() -> dict:
    scholar_id = os.environ.get("GOOGLE_SCHOLAR_ID", "").strip()
    if not scholar_id:
        return empty_author("GOOGLE_SCHOLAR_ID is not configured.")

    try:
        from scholarly import scholarly

        author = scholarly.search_author_id(scholar_id)
        scholarly.fill(author, sections=["basics", "indices", "counts", "publications"])
        author["updated"] = str(datetime.now())
        author["publications"] = {
            v["author_pub_id"]: v for v in author.get("publications", [])
        }
        author["crawler_status"] = "ok"
        return author
    except Exception as exc:
        print(f"Google Scholar crawl failed: {exc}", file=sys.stderr)
        return empty_author(f"Google Scholar crawl failed: {exc}")


author = fetch_author()
print(json.dumps(author, indent=2))

os.makedirs("results", exist_ok=True)
with open("results/gs_data.json", "w", encoding="utf-8") as outfile:
    json.dump(author, outfile, ensure_ascii=False)

shieldio_data = {
    "schemaVersion": 1,
    "label": "citations",
    "message": f"{author.get('citedby', 0)}",
}
with open("results/gs_data_shieldsio.json", "w", encoding="utf-8") as outfile:
    json.dump(shieldio_data, outfile, ensure_ascii=False)
