from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError
import ssl
import certifi
import os
import json
import sys
import time

API_URL = "https://uselessfacts.jsph.pl/random.json?language=en"
TIMEOUT = 10  # 秒
RETRIES = 1


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


def main():
    print("🔎 Fetching a random fact from uselessfacts.jsph.pl...")
    fact, link = fetch_fact()

    if fact:
        print("\n— Random Fact —")
        print(fact)
        if link:
            print(f"\nSource: {link}")
    else:
        print("\n❌ Failed to retrieve a fact. Please check your network or try again later.")
        sys.exit(1)


if __name__ == "__main__":
    main()
