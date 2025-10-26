from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError
import ssl
import certifi
import os
import json
import sys
import time
from datetime import datetime, timezone
import argparse

API_URL = "https://uselessfacts.jsph.pl/random.json?language=en"
TIMEOUT = 10  # 秒
RETRIES = 1
QUOTES_FILE = "quotes.json"  # 本機儲存檔案（JSON 格式）


# --------- Persistence (JSON) ---------
def load_facts(filename: str = QUOTES_FILE):
    """載入本機已儲存的事實列表。

    結構：list[{
        "text": str,
        "source": Optional[str],
        "added_at": ISO8601 datetime string (UTC)
    }]
    若檔案不存在或格式錯誤，回傳空 list。
    """
    if not os.path.exists(filename):
        return []
    try:
        with open(filename, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list):
                return data
            return []
    except (json.JSONDecodeError, OSError):
        return []


def save_facts(facts, filename: str = QUOTES_FILE):
    """將事實列表存回 JSON 檔案。"""
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(facts, f, ensure_ascii=False, indent=2)


def normalize_text(s: str) -> str:
    """用於比對重複的簡單正規化：去除前後空白並使用單一空白。"""
    if not isinstance(s, str):
        return ""
    # 簡單規則：strip + 把連續空白壓成單一空白
    return " ".join(s.strip().split())


def add_fact_if_unique(fact_text: str, source: str | None, filename: str = QUOTES_FILE):
    """如果 fact_text 尚未存在檔案中，則新增並儲存。

    回傳：
    - (True, entry)  表示新增成功
    - (False, entry) 表示已存在（不新增），entry 為既有或建議結構
    """
    facts = load_facts(filename)
    existing_texts = {normalize_text(item.get("text", "")) for item in facts}
    key = normalize_text(fact_text)

    entry = {
        "text": fact_text,
        "source": source,
        "added_at": datetime.now(timezone.utc).isoformat()
    }

    if key in existing_texts:
        return False, entry

    facts.append(entry)
    save_facts(facts, filename)
    return True, entry


def fetch_fact(url=API_URL, timeout=TIMEOUT, retries=RETRIES):
    """Fetch a single random fact from the API.

    Returns a tuple (fact_text, source_url) or (None, None) on failure.
    """
    # 預設情況下，使用 certifi 的 CA 套件
    # 僅限開發：設置環境變量 DEBUG_SKIP_SSL=1 以允許未經驗證的回退。
    allow_unverified = os.environ.get("DEBUG_SKIP_SSL", "0") == "1"
    ctx = None
    if allow_unverified:
        ctx = ssl._create_unverified_context()
    else:
        ctx = ssl.create_default_context(cafile=certifi.where())

    attempt = 0
    while attempt <= retries:
        try:
            req = Request(url, headers={"User-Agent": "python-quote-collector/1.0"})
            with urlopen(req, timeout=timeout, context=ctx) as resp:
                raw = resp.read().decode("utf-8")
                data = json.loads(raw)

                # The API returns fields like 'text' and 'permalink'
                fact = data.get("text") or data.get("fact")
                permalink = data.get("permalink") or data.get("source_url")
                return fact, permalink

        except HTTPError as e:
            print(f"⚠️ HTTP error: {e.code} {e.reason}")
            return None, None
        except URLError as e:
            msg = str(e)
            print(f"⚠️ URL error / network issue: {msg}")
        except json.JSONDecodeError:
            print("⚠️ Failed to decode JSON from API response")
            return None, None

        attempt += 1
        if attempt <= retries:
            time.sleep(1)

    return None, None


def run_once():
    print("🔎 Fetching a random fact from uselessfacts.jsph.pl...")

    # 支援以環境變數覆寫，方便測試重複檢查
    override_text = os.environ.get("FACT_OVERRIDE_TEXT")
    override_link = os.environ.get("FACT_OVERRIDE_LINK")

    if override_text:
        fact, link = override_text, override_link
    else:
        fact, link = fetch_fact()

    if not fact:
        print("\n❌ Failed to retrieve a fact. Please check your network or try again later.")
        return False

    print("\n— Random Fact —")
    print(fact)
    if link:
        print(f"\nSource: {link}")

    # 將取得的事實寫入本機存檔（避免重複）
    created, _ = add_fact_if_unique(fact, link, QUOTES_FILE)
    if created:
        print(f"\n✅ Added to {QUOTES_FILE}. Total size may have increased.")
    else:
        print(f"\n🟡 Duplicate detected. No changes to {QUOTES_FILE}.")
    return True


def main(argv=None):
    parser = argparse.ArgumentParser(description="Digital Fact Collector")
    parser.add_argument("--loop", action="store_true", help="持續運行，以固定間隔抓取新事實")
    parser.add_argument("--interval", type=int, default=600, help="循環模式下的抓取間隔秒數（預設 600 秒）")
    parser.add_argument("--max-runs", type=int, default=0, help="循環模式下最多執行次數（0 表示無限）")
    args = parser.parse_args(argv)

    if not args.loop:
        ok = run_once()
        sys.exit(0 if ok else 1)

    # 迴圈模式
    print(f"⏱️ Loop mode: interval={args.interval}s, max_runs={'∞' if args.max_runs == 0 else args.max_runs}")
    runs = 0
    try:
        while True:
            runs += 1
            print(f"\n=== Run {runs} @ {datetime.now(timezone.utc).isoformat()} ===")
            ok = run_once()
            if not ok:
                print("⚠️ This run failed to fetch a fact.")

            if args.max_runs and runs >= args.max_runs:
                print("✅ Reached max_runs. Exiting loop.")
                break

            time.sleep(max(1, args.interval))
    except KeyboardInterrupt:
        print("\n🛑 Interrupted by user. Exiting loop.")
    sys.exit(0)


if __name__ == "__main__":
    main()
