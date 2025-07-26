# J-Quants MCP server

[Model Context Protocol](https://modelcontextprotocol.io/introduction) (MCP) サーバーで、J-Quants APIにアクセスするための機能を提供します。

## ツール

このサーバーは以下のツールを提供しています：

- `search_company` : 日本語のテキストから、上場銘柄を検索する
- `get_daily_quotes` : 銘柄コードから、日次の株価を取得する
- `get_financial_statements` : 銘柄コードから、財務諸表を取得する
- `get_topix_prices` : TOPIX四本値（日次データ）を取得する
- `get_trades_spec` : 投資部門別売買高データを取得する（個人・外国人・機関投資家等の売買動向）


## 使い方
このサーバーを使用するには、J-Quants APIへの登録が必要です。以下の手順で取得できます：
- [J-Quants API](https://jpx-jquants.com/)に登録
- IDトークンを取得しして、`JQUANTS_ID_TOKEN`環境変数に設定


#### Claude Desktop

- On MacOS: `~/Library/Application\ Support/Claude/claude_desktop_config.json`
- On Windows: `%APPDATA%/Claude/claude_desktop_config.json`

```json
{
    "mcpServers": {
        "jquants": {
            "command": "uv",
            "args": [
                "--directory",
                "/path/to/jquants-mcp-server",
                "run",
                "jquants-mcp-server"
            ],
            "env": {
                "JQUANTS_ID_TOKEN": "YOUR_JQUANTS_ID_TOKEN"
            }
        }
    }
}
```

```json
{
    "mcpServers": {
        "jquants": {
            "command": "uvx",
            "args": [
                "jquants-mcp-server"
            ],
            "env": {
                "JQUANTS_ID_TOKEN": "YOUR_JQUANTS_ID_TOKEN"
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
