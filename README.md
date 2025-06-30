# Card Event Automation

這個專案會自動執行卡片活動的相關操作，包括登入和提交表單。

## GitHub Actions 自動化設定

此專案已設定 GitHub Actions，會在每天下午 3 點（台灣時間）自動執行。

### 設定 GitHub Secrets

為了讓 GitHub Actions 正常運作，您需要在 GitHub repository 中設定以下 Secrets：

1. 前往您的 GitHub repository
2. 點選 **Settings** 標籤
3. 在左側選單中點選 **Secrets and variables** > **Actions**
4. 點選 **New repository secret** 並添加以下 secrets：

| Secret Name | 描述 |
|-------------|------|
| `API_KEY_2CAPTCHA` | 2captcha API 金鑰 |
| `SID` | 系統 ID |
| `BIRTH` | 生日資訊 |
| `RECIPIENT_EMAIL` | 收件者信箱 |
| `SENDER_EMAIL` | 寄件者信箱 |
| `SMTP_SERVER` | SMTP 伺服器 |
| `SMTP_PORT` | SMTP 埠號 |
| `SMTP_USER` | SMTP 使用者名稱 |
| `SMTP_PASSWORD` | SMTP 密碼 |

### 手動觸發

除了定時執行外，您也可以手動觸發工作流程：

1. 前往 **Actions** 標籤
2. 選擇 **Daily Card Event Automation** 工作流程
3. 點選 **Run workflow** 按鈕

### 查看執行結果

- 執行歷史和日誌可在 **Actions** 標籤中查看
- 如果有產生日誌檔案，會自動上傳為 artifacts
- 日誌檔案會保留 7 天

## 本地執行

### 安裝依賴

```bash
pip install -r requirements.txt
playwright install chromium
```

### 設定環境變數

複製 `.env.example` 到 `.env` 並填入相關資訊。

### 執行程式

```bash
# 無頭模式執行（預設）
python main.py --headless

# 有介面模式執行
python main.py --no-headless
```

## 專案結構

```
├── main.py              # 主程式入口
├── requirements.txt     # Python 依賴套件
├── .env                # 環境變數設定
├── detector/           # 驗證碼偵測模組
├── login/              # 登入功能模組
├── submit/             # 提交功能模組
├── utils/              # 工具模組
└── logs/               # 日誌檔案
```
