Digital-Fact-Collector
======================

一個從 Zen Quotes https://zenquotes.io 取得隨機名言並儲存在本機 JSON 的小工具。

目錄
-----
- `quote_collector.py` — 主程式，會呼叫 API 並把引述儲存在 `quotes.json`。
- `requirements.txt` — 專案相依（目前：`requests`）。
- `run.ps1` — 一鍵建立 venv、安裝相依並執行（供 Windows 使用者快速上手）。

快速上手（Windows / PowerShell）
---------------------------------

下面給新使用者的推薦流程（兩種：快速方式與建議的隔離方式）。

先決條件
- 建議安裝官方 CPython（從 https://python.org/downloads/ 下載 Windows installer），安裝時勾選「Add Python to PATH」與「Install launcher for all users (recommended)」。

驗證安裝
```powershell
where python
python --version
py --version   # 若安裝了 launcher
```

選項 A — 快速（直接安裝到使用者目錄）
```powershell
# 安裝相依到使用者目錄（不需要管理員）
pip install --user -r requirements.txt

# 執行程式
python .\quote_collector.py
```

選項 B — 推薦（專案隔離，使用 venv）
```powershell
# 建立 venv
python -m venv .venv

# 檢查啟用檔案位置（Windows 可能在 Scripts 或 bin）
Test-Path .\.venv\Scripts\Activate.ps1
Test-Path .\.venv\bin\Activate.ps1

# 啟用（選存在的檔案）
.\.venv\Scripts\Activate.ps1
# 或
.\.venv\bin\Activate.ps1

# 安裝相依並執行
python -m pip install -r requirements.txt
python .\quote_collector.py
```

一鍵方式（run.ps1）
--------------------
如果你在 Windows 上，`run.ps1` 可以自動完成檢查 Python、建立或更新 `.venv`、安裝 `requirements.txt`，並執行 `quote_collector.py`：

```powershell
# 若系統允許執行腳本：
.\run.ps1

# 若被執行政策阻擋（臨時放寬）：
powershell -NoProfile -ExecutionPolicy Bypass -File .\run.ps1
```

若系統有多個 Python
--------------------
若你電腦上有多個 Python（或不想用 PATH 中的 python），可用完整路徑指定：

```powershell
& 'C:\Full\Path\To\python.exe' -m pip install --user requests
& 'C:\Full\Path\To\python.exe' .\quote_collector.py
```

常見問題（FAQ）
----------------
- 收到 `No module named pip` 或 `externally-managed-environment`：表示該 Python 被系統/發行版管理（或缺少 pip），不建議在此上面安裝套件。解法：
  - 安裝官方 CPython（會帶 pip），或
  - 使用本專案的 `.venv`（最安全），或
  - 若你了解風險可使用 `get-pip.py` 強制安裝（不推薦）。
- 找不到 `Activate.ps1`：檢查 `.venv\Scripts` 與 `.venv\bin`，或直接以 venv 內的 python 執行：
  ```powershell
  & .\.venv\Scripts\python.exe .\quote_collector.py
  # 或
  & .\.venv\bin\python.exe .\quote_collector.py
  ```

關於時間格式
-------------
程式會以 timezone-aware 的 UTC 時間儲存 `added_at`（ISO 8601），範例：
```
2025-10-26T12:34:56+00:00
```
若你偏好 `Z` 結尾，可改用：
```py
datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
```

開發者備註
-----------
- 若要將此工具包裝成可供他人一鍵安裝的 CLI，考慮使用 `pipx` 或建立小型 wheel/distribution。
- 我已加入 `run.ps1`（Windows 一鍵腳本）與 `requirements.txt`（列出 `requests`）。

