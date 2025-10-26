Digital-Fact-Collector
======================

一個從 Zen Quotes（https://zenquotes.io）取得隨機名言並儲存在本機 JSON 的小工具。

目錄
-----
- `quote_collector.py` — 主程式，會呼叫公開的 Useless Facts API 並在控制台輸出事實。
- `requirements.txt` — 專案相依（本次實作使用標準庫 urllib，無需額外安裝，但 `requests` 仍列在此檔以便其他實作）。
- `run.ps1` — 一鍵建立 venv、安裝相依並執行（供 Windows 使用者快速上手）。
# Digital-Fact-Collector

一個簡單示範專案：從公開 API 取得隨機事實並顯示到控制台。這個範例展示如何以 Python 與線上服務互動、處理 JSON、與基本的 SSL 驗證策略。

目前實作
- `quote_collector.py` — 主程式，會呼叫 Useless Facts API（https://uselessfacts.jsph.pl/random.json?language=en）並在控制台輸出事實與來源連結。預設使用 Python 標準庫 `urllib` 並透過 `certifi` 的 CA bundle 做 SSL 驗證。
- `requirements.txt` — 專案相依（包含 `requests` 與 `certifi`）。
- `run.ps1` —（可選）Windows 一鍵腳本，用來建立 venv、安裝相依並執行程式（視專案是否包含而定）。

快速上手（Windows / PowerShell）
---------------------------------

建議使用虛擬環境隔離：

```powershell
# 建立 venv
python -m venv .venv

# 啟用 venv（本專案的 venv 在 Windows 上使用 .venv\bin 下的啟動腳本）
Test-Path .\.venv\Scripts\Activate.ps1   # Windows 標準位置
Test-Path .\.venv\bin\Activate.ps1       # 有些系統會用 bin

# 啟用（選擇存在的檔案）
.\.venv\Scripts\Activate.ps1
# 或
.\.venv\bin\Activate.ps1

# 安裝相依並執行
python -m pip install -r requirements.txt
python .\quote_collector.py
```

若你不想啟用 venv，也可以直接使用系統 Python（不過不建議在系統環境安裝套件）：

```powershell
pip install --user -r requirements.txt
python .\quote_collector.py
```

執行範例輸出

```text
🔎 Fetching a random fact from uselessfacts.jsph.pl...

— Random Fact —
Giraffes have no vocal cords.

Source: https://uselessfacts.jsph.pl/api/v2/facts/aa973c0e0e06fd41ec814afd33252c81
```

關於 SSL 驗證與 certifi
-----------------------

在某些 Windows 或 Python 安裝上，系統可能缺少可供 OpenSSL 驗證憑證鏈的 CA bundle，導致出現類似：

```
<urlopen error [SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1010)>
```

為了在不同環境下都能穩定且安全地驗證 HTTPS，`quote_collector.py` 預設使用 `certifi` 提供的 CA bundle（`ssl.create_default_context(cafile=certifi.where())`）。

如果你只是在開發環境短暫測試且確認網路可靠，也可以用環境變數暫時跳過驗證（僅用於開發）：

PowerShell:

```powershell
$env:DEBUG_SKIP_SSL='1'
python .\quote_collector.py
```

注意：跳過 SSL 驗證會降低安全性，請勿在生產或不受信任的網路上使用。

進階/未來改進
----------------
- 將取得的事實儲存到 `quotes.json`（避免重複並保留時間戳）；
- 提供 CLI 參數（例如 `--save` 或 `--count`）；
- 新增單元測試與 CI（模擬 API 回應）；
- 若偏好使用 `requests` 可將實作切換回 `requests`，但目前使用標準庫以降低外部依賴（同時使用 certifi 做驗證）。

貢獻
----
歡迎提出 Issue 或 PR。若要在本地貢獻，請先建立虛擬環境並遵照上方「快速上手」步驟。

