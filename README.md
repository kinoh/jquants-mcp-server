# J-Quants MCP server

[Model Context Protocol](https://modelcontextprotocol.io/introduction) (MCP) サーバーで、J-Quants APIにアクセスするための機能を提供します。

## ツール

このサーバーは以下のツールを提供しています。利用可能なツールはJ-Quants APIのプランによって異なります。

### 無料プラン以上で利用可能

- `search_company` : 日本語のテキストから、上場銘柄を検索する
- `get_daily_quotes` : 銘柄コードから、日次の株価を取得する
- `get_financial_statements` : 銘柄コードから、財務諸表を取得する
- `get_fins_announcement` : 決算発表予定を取得する

### Lightプラン以上で利用可能

- `get_trades_spec` : 投資部門別売買高データを取得する（個人・外国人・機関投資家等の売買動向）
- `get_topix_prices` : TOPIX四本値（日次データ）を取得する

### Standardプラン以上で利用可能

- `get_option_index_option` : 日経225オプション四本値を取得する
- `get_markets_weekly_margin_interest` : 信用取引残高（週次）を取得する
- `get_markets_short_selling` : 業種別空売り比率を取得する
- `get_indices` : 指数四本値を取得する
- `get_markets_short_selling_positions` : 空売り残高報告を取得する
- `get_markets_daily_margin_interest` : 信用取引残高（日次）を取得する

### Premiumプラン以上で利用可能

- `get_markets_breakdown` : 売買内訳を取得する
- `get_prices_prices_am` : 午前終値を取得する
- `get_fins_dividend` : 配当情報を取得する
- `get_fins_fs_details` : 財務諸表詳細を取得する
- `get_derivatives_futures` : 先物四本値を取得する
- `get_derivatives_options` : オプション四本値を取得する

## 使い方

### 認証設定

このサーバーを使用するには、J-Quants APIへの登録が必要です：
1. [J-Quants API](https://jpx-jquants.com/)に登録してプランを選択
2. 以下のいずれかの方法で認証情報を設定：

**方法A: リフレッシュトークンを使用（推奨）**
```bash
export JQUANTS_REFRESH_TOKEN="your_refresh_token"
```

**方法B: メールアドレスとパスワードを使用**
```bash
export JQUANTS_MAIL_ADDRESS="your_email@example.com"
export JQUANTS_PASSWORD="your_password"
```

**注意**:
- 利用できるツールはプランによって異なります。詳細は上記の「ツール」セクションを参照してください
- リフレッシュトークンはより安全ですが有効期限があります

### Claude Desktop

以下の2つの方法でセットアップできます：

#### 方法1: ローカル開発用（リポジトリをクローンした場合）

設定ファイルの場所:
- MacOS: `~/Library/Application\ Support/Claude/claude_desktop_config.json`
- Windows: `%APPDATA%/Claude/claude_desktop_config.json`

**リフレッシュトークンを使用する場合:**
```json
{
    "mcpServers": {
        "jquants": {
            "command": "uv",
            "args": [
                "--directory",
                "/path/to/jquants-mcp-server",
                "run",
                "src/jquants_mcp_server/server.py"
            ],
            "env": {
                "JQUANTS_REFRESH_TOKEN": "YOUR_REFRESH_TOKEN"
            }
        }
    }
}
```

**メールアドレス/パスワードを使用する場合:**
```json
{
    "mcpServers": {
        "jquants": {
            "command": "uv",
            "args": [
                "--directory",
                "/path/to/jquants-mcp-server",
                "run",
                "src/jquants_mcp_server/server.py"
            ],
            "env": {
                "JQUANTS_MAIL_ADDRESS": "your_email@example.com",
                "JQUANTS_PASSWORD": "your_password"
            }
        }
    }
}
```

#### 方法2: パッケージ公開後（PyPIから直接利用する場合）

**リフレッシュトークンを使用する場合:**
```json
{
    "mcpServers": {
        "jquants": {
            "command": "uvx",
            "args": [
                "jquants-mcp-server"
            ],
            "env": {
                "JQUANTS_REFRESH_TOKEN": "YOUR_REFRESH_TOKEN"
            }
        }
    }
}
```

**メールアドレス/パスワードを使用する場合:**
```json
{
    "mcpServers": {
        "jquants": {
            "command": "uvx",
            "args": [
                "jquants-mcp-server"
            ],
            "env": {
                "JQUANTS_MAIL_ADDRESS": "your_email@example.com",
                "JQUANTS_PASSWORD": "your_password"
            }
        }
    }
}
```

## 使用例

例えばClaudeに以下のような質問ができます：
- "コメダとルノアールの自己資本比率を比較して"
- "UUUMとカバーとANYCOLORの財務表を取得して、バランスシートを図にしてください。"
- "最近のTOPIXの動向を教えて"
- "外国人投資家と個人投資家の売買動向を分析して"
![sample](https://github.com/user-attachments/assets/5e480007-228f-4ff9-a834-d79f490b3360)

## ライセンス

このプロジェクトはMITライセンスの下で提供されています
 - 詳細はLICENSEファイルを参照してください。
