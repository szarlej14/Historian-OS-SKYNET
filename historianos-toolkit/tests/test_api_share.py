import tempfile
from pathlib import Path

import api_server


def write_record(base, name, content):
    p = base / name
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")


def main():
    with tempfile.TemporaryDirectory() as tmp:
        base = Path(tmp)
        write_record(base, "40 Fakty/fakt.md", "type: fakt\nname: Test\n")
        write_record(base, "20 Wydarzenia/event.md", "type: wydarzenie\nname: Zdarzenie\nstart: 1000-01-01\n")
        write_record(base, "10 Miejsca/place.md", "type: miejsce\nname: Gniezno\nlat: 52.5348\nlon: 17.5826\n")
        assert api_server.stats(base)["fakt"] == 1
        assert len(api_server.timeline(base)) == 1
        assert api_server.map_items(base)[0]["lat"] == 52.5348
        payload = api_server.share_payload("test-vault", base)
        assert payload["share_url"] == "/vault/test-vault"
        assert payload["dashboard_url"].endswith("?vault=test-vault")
        assert payload["export_url"].endswith("/export")

    print("HistorianOS API share/embed unit smoke: PASS")


if __name__ == "__main__":
    main()
