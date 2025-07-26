import asyncio
import os
import json
from datetime import datetime, timedelta
from typing import Any
import httpx
from mcp.server.fastmcp import FastMCP

mcp_server = FastMCP("JQuants-MCP-server")

async def make_requests(url: str,timeout: int = 30) -> dict[str, Any]:
    """
    Function to process requests

    Args:
        url (str): URL for the request
        timeout (int, optional): Timeout in seconds. Default is 30 seconds.

    Returns:
        str: API response text
    """
    try:
        idToken = os.environ.get("JQUANTS_ID_TOKEN", "")
        if not idToken:
            return {"error": "JQUANTS_ID_TOKENが設定されていません。", "status": "id_token_error"}

        async with httpx.AsyncClient(timeout=timeout) as client:
            headers = {'Authorization': 'Bearer {}'.format(idToken)}
            response = await client.get(url, headers=headers)
            if response.status_code != 200:
                return {"error": f"APIリクエストに失敗しました。ステータスコード: {response.status_code}", "status": "request_error"}
            if response.headers.get("Content-Type") != "application/json":
                return {"error": "APIレスポンスがJSON形式ではありません。", "status": "response_format_error"}

            return json.loads(response.text)

    except Exception as e:
        if isinstance(e, httpx.TimeoutException):
            error_msg =  f"タイムアウトエラーが発生しました。現在のタイムアウト設定: {timeout}秒"
            return {"error": error_msg, "status": "timeout"}
        elif isinstance(e, httpx.ConnectError):
            error_msg = "E-Stat APIサーバーへの接続に失敗しました。ネットワーク接続を確認してください。"
            return {"error": error_msg, "status": "connection_error"}
        elif isinstance(e, httpx.HTTPStatusError):
            error_msg = f"HTTPエラー（ステータスコード: {e.response.status_code}）が発生しました。"
            return {"error": error_msg, "status": "http_error"}
        else:
            error_msg = f"予期せぬエラーが発生しました: {str(e)}"
            return {"error": error_msg, "status": "unexpected_error"}


@mcp_server.tool()
async def search_company(
        query : str,
        limit : int = 10,
        start_position : int = 0,
    ) -> str:
    """
    Search for listed stocks by company name.

    Args:
        query (str): Query parameter for searching company names. Specify a string contained in the company name.
            Example: Specifying "トヨタ" will search for stocks with "トヨタ" in the company name.
            Must be in Japanese.
        limit (int, optional): Maximum number of results to retrieve. Defaults to 10.
        start_position (int, optional): The starting position for the search. Defaults to 0.

    Returns:
        str: API response text
    """
    url = "https://api.jquants.com/v1/listed/info"
    response = await make_requests(url)
    if "error" in response:
        return json.dumps(response, ensure_ascii=False)

    response_json_list = response.get("info", [])
    response_json_list = [
        r for r in response_json_list
        if (
            query.lower() in r.get("CompanyName", "").lower()
            or
            query.lower() in r.get("CompanyNameEnglish", "").lower()
        )
    ][start_position:start_position + limit]

    response_json = {'info': response_json_list}
    return json.dumps(response_json, ensure_ascii=False)



@mcp_server.tool()
async def get_daily_quotes(
        code : str,
        from_date : str,
        to_date : str,
        limit : int = 10,
        start_position : int = 0,
    ) -> str:
    """
    Retrieve daily stock price data for a specified stock code.
    Data availability varies by plan:
    - Free plan: Past 2 years
    - Light plan: Past 5 years
    - Standard plan: Past 10 years
    - Premium plan: All available historical data

    Args:
        code (str): Specify the stock code. Example: "72030" (トヨタ自動車)
        from_date (str): Specify the start date. Example: "2023-01-01" must be in YYYY-MM-DD format
        to_date (str): Specify the end date. Example: "2023-01-31" must be in YYYY-MM-DD format
        limit (int, optional): Maximum number of results to retrieve. Defaults to 10.
        start_position (int, optional): The starting position for the search. Defaults to 0.

    Returns:
        str: API response text
    """

    url = "https://api.jquants.com/v1/prices/daily_quotes?code={}&from={}&to={}".format(
        code,
        from_date,
        to_date
    )
    response = await make_requests(url)
    if "error" in response:
        return json.dumps(response, ensure_ascii=False)
    response_json_list = response.get("daily_quotes", [])
    response_json_list = response_json_list[start_position:start_position + limit]
    response_json = {'daily_quotes': response_json_list}
    return json.dumps(response_json, ensure_ascii=False)


@mcp_server.tool()
async def get_financial_statements(
        code : str,
        limit : int = 10,
        start_position : int = 0,
    ) -> str:
    """
    Retrieve financial statements for a specified stock code.
    Data availability varies by plan:
    - Free plan: Past 2 years
    - Light plan: Past 5 years
    - Standard plan: Past 10 years
    - Premium plan: All available historical data

    You can obtain quarterly financial summary reports and disclosure information regarding
    revisions to performance and dividend information (mainly numerical data) for listed companies.

    Args:
        code (str): Specify the stock code. Example: "72030" (トヨタ自動車)
        limit (int, optional): Maximum number of results to retrieve. Defaults to 10.
        start_position (int, optional): The starting position for the search. Defaults to 0.
    """
    url = "https://api.jquants.com/v1/fins/statements?code={}".format(code)
    response = await make_requests(url)
    if "error" in response:
        return json.dumps(response, ensure_ascii=False)
    response_json_list = response.get("statements", [])
    response_json_list = [
        {k:v for k,v in r.items() if v != ""}
        for r in response_json_list
    ][start_position:start_position + limit]
    response_json = {'statements': response_json_list}
    return json.dumps(response_json, ensure_ascii=False)


@mcp_server.tool()
async def get_topix_prices(
        from_date: str,
        to_date: str,
        pagination_key: str = "",
        limit: int = 10,
        start_position: int = 0,
    ) -> str:
    """
    Retrieve daily TOPIX (Tokyo Stock Price Index) price data.

    Args:
        from_date (str): Start date in YYYY-MM-DD format. Example: "2023-01-01"
        to_date (str): End date in YYYY-MM-DD format. Example: "2023-01-31"
        pagination_key (str, optional): Pagination key for retrieving subsequent data
        limit (int, optional): Maximum number of results to retrieve. Defaults to 10.
        start_position (int, optional): The starting position for the search. Defaults to 0.

    Returns:
        str: API response text containing TOPIX OHLC data
    """

    url = f"https://api.jquants.com/v1/indices/topix?from={from_date}&to={to_date}"
    if pagination_key:
        url += f"&pagination_key={pagination_key}"

    response = await make_requests(url)
    if "error" in response:
        return json.dumps(response, ensure_ascii=False)

    response_json_list = response.get("topix", [])
    response_json_list = response_json_list[start_position:start_position + limit]
    response_json = {'topix': response_json_list}
    return json.dumps(response_json, ensure_ascii=False)


@mcp_server.tool()
async def get_trades_spec(
        section: str = "",
        from_date: str = "",
        to_date: str = "",
        pagination_key: str = "",
        limit: int = 10,
        start_position: int = 0,
    ) -> str:
    """
    Retrieve trading by type of investors (stock trading value) data.
    This provides investment sector breakdown data showing trading values by different investor types
    such as individuals, foreigners, institutions, etc.

    You can specify either 'section' or 'from_date/to_date' or both.

    Args:
        section (str, optional): Section name. Example: "TSEPrime", "TSEStandard", "TSEGrowth"
        from_date (str, optional): Start date in YYYY-MM-DD format. Example: "2023-01-01"
        to_date (str, optional): End date in YYYY-MM-DD format. Example: "2023-01-31"
        pagination_key (str, optional): Pagination key for retrieving subsequent data
        limit (int, optional): Maximum number of results to retrieve. Defaults to 10.
        start_position (int, optional): The starting position for the search. Defaults to 0.

    Returns:
        str: API response text containing trading data by investor type including individuals, 
             foreigners, institutions, etc. with sales/purchase values and balances
    """

    url = "https://api.jquants.com/v1/markets/trades_spec"
    params = []
    if section:
        params.append(f"section={section}")
    if from_date:
        params.append(f"from={from_date}")
    if to_date:
        params.append(f"to={to_date}")
    if pagination_key:
        params.append(f"pagination_key={pagination_key}")

    if params:
        url += "?" + "&".join(params)

    response = await make_requests(url)
    if "error" in response:
        return json.dumps(response, ensure_ascii=False)

    response_json_list = response.get("trades_spec", [])
    response_json_list = response_json_list[start_position:start_position + limit]
    response_json = {'trades_spec': response_json_list}
    return json.dumps(response_json, ensure_ascii=False)


def main() -> None:
    print("Starting J-Quants MCP server!")
    mcp_server.run(transport="stdio")

if __name__ == "__main__":
    main()
