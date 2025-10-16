import os
import json
from datetime import datetime
from typing import Optional
import pandas as pd
import jquantsapi
from mcp.server.fastmcp import FastMCP

mcp_server = FastMCP("JQuants-MCP-server")

_client: Optional[jquantsapi.Client] = None

def get_client() -> jquantsapi.Client:
    """
    Get or create J-Quants API client with authentication.

    Authentication priority:
    1. Use JQUANTS_REFRESH_TOKEN if available
    2. Fall back to JQUANTS_MAIL_ADDRESS and JQUANTS_PASSWORD

    Returns:
        jquantsapi.Client: Authenticated client instance

    Raises:
        ValueError: If neither refresh token nor email/password are provided
    """
    global _client

    if _client is not None:
        return _client

    refresh_token = os.environ.get("JQUANTS_REFRESH_TOKEN", "")
    mail_address = os.environ.get("JQUANTS_MAIL_ADDRESS", "")
    password = os.environ.get("JQUANTS_PASSWORD", "")

    if refresh_token:
        _client = jquantsapi.Client(refresh_token=refresh_token)
    elif mail_address and password:
        _client = jquantsapi.Client(mail_address=mail_address, password=password)
    else:
        raise ValueError(
            "Authentication credentials not found. "
            "Please set either JQUANTS_REFRESH_TOKEN or both "
            "JQUANTS_MAIL_ADDRESS and JQUANTS_PASSWORD environment variables."
        )

    return _client


def _convert_df_to_json(df: pd.DataFrame, key: str) -> str:
    """
    Convert pandas DataFrame to JSON string with proper serialization.

    Handles pandas Timestamp objects by converting them to ISO format strings.

    Args:
        df: DataFrame to convert
        key: Top-level key name for the JSON response

    Returns:
        JSON string with proper formatting
    """
    # Convert DataFrame to list of dicts with default date serialization
    data_list = df.to_dict(orient='records')

    # Convert any pandas Timestamp objects to ISO format strings
    for record in data_list:
        for k, v in record.items():
            if isinstance(v, pd.Timestamp):
                record[k] = v.isoformat()
            elif pd.isna(v):
                record[k] = None

    response = {key: data_list}
    return json.dumps(response, ensure_ascii=False, default=str)


@mcp_server.tool()
def search_company(
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
    try:
        client = get_client()
        df = client.get_listed_info()

        # Filter by query (case-insensitive search in CompanyName and CompanyNameEnglish)
        mask = (
            df['CompanyName'].str.contains(query, case=False, na=False) |
            df['CompanyNameEnglish'].str.contains(query, case=False, na=False)
        )
        filtered_df = df[mask]

        # Apply pagination
        paginated_df = filtered_df.iloc[start_position:start_position + limit]

        return _convert_df_to_json(paginated_df, 'info')

    except Exception as e:
        error_response = {"error": str(e), "status": "error"}
        return json.dumps(error_response, ensure_ascii=False)



@mcp_server.tool()
def get_daily_quotes(
        code : str,
        from_yyyymmdd : str,
        to_yyyymmdd : str,
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
        from_yyyymmdd (str): Specify the start date. Example: "20231001" must be in YYYYMMDD format
        to_yyyymmdd (str): Specify the end date. Example: "20231031" must be in YYYYMMDD format
        limit (int, optional): Maximum number of results to retrieve. Defaults to 10.
        start_position (int, optional): The starting position for the search. Defaults to 0.

    Returns:
        str: API response text
    """
    try:
        client = get_client()

        df = client.get_prices_daily_quotes(
            code=code,
            from_yyyymmdd=from_yyyymmdd,
            to_yyyymmdd=to_yyyymmdd
        )

        # Apply pagination
        paginated_df = df.iloc[start_position:start_position + limit]

        return _convert_df_to_json(paginated_df, 'daily_quotes')

    except Exception as e:
        error_response = {"error": str(e), "status": "error"}
        return json.dumps(error_response, ensure_ascii=False)


@mcp_server.tool()
def get_financial_statements(
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
    try:
        client = get_client()
        df = client.get_fins_statements(code=code)

        # Apply pagination
        paginated_df = df.iloc[start_position:start_position + limit]

        # Convert to JSON with proper serialization
        json_str = _convert_df_to_json(paginated_df, 'statements')

        # Remove empty string values from the result
        data = json.loads(json_str)
        data['statements'] = [
            {k: v for k, v in record.items() if v != ""}
            for record in data['statements']
        ]

        return json.dumps(data, ensure_ascii=False)

    except Exception as e:
        error_response = {"error": str(e), "status": "error"}
        return json.dumps(error_response, ensure_ascii=False)


@mcp_server.tool()
def get_topix_prices(
        from_yyyymmdd: str,
        to_yyyymmdd: str,
        pagination_key: str = "",
        limit: int = 10,
        start_position: int = 0,
    ) -> str:
    """
    Retrieve daily TOPIX (Tokyo Stock Price Index) price data.

    Args:
        from_yyyymmdd (str): Start date in YYYYMMDD format. Example: "20231001"
        to_yyyymmdd (str): End date in YYYYMMDD format. Example: "20231031"
        pagination_key (str, optional): Pagination key for retrieving subsequent data (Note: not used with official library)
        limit (int, optional): Maximum number of results to retrieve. Defaults to 10.
        start_position (int, optional): The starting position for the search. Defaults to 0.

    Returns:
        str: API response text containing TOPIX OHLC data
    """
    try:
        client = get_client()

        df = client.get_indices_topix(
            from_yyyymmdd=from_yyyymmdd,
            to_yyyymmdd=to_yyyymmdd
        )

        # Apply pagination
        paginated_df = df.iloc[start_position:start_position + limit]

        return _convert_df_to_json(paginated_df, 'topix')

    except Exception as e:
        error_response = {"error": str(e), "status": "error"}
        return json.dumps(error_response, ensure_ascii=False)


@mcp_server.tool()
def get_trades_spec(
        section: str = "",
        from_yyyymmdd: str = "",
        to_yyyymmdd: str = "",
        pagination_key: str = "",
        limit: int = 10,
        start_position: int = 0,
    ) -> str:
    """
    Retrieve trading by type of investors (stock trading value) data.
    This provides investment sector breakdown data showing trading values by different investor types
    such as individuals, foreigners, institutions, etc.

    You can specify either 'section' or 'from_yyyymmdd/to_yyyymmdd' or both.

    Args:
        section (str, optional): Section name. Example: "TSEPrime", "TSEStandard", "TSEGrowth"
        from_yyyymmdd (str, optional): Start date in YYYYMMDD format. Example: "20231001"
        to_yyyymmdd (str, optional): End date in YYYYMMDD format. Example: "20231031"
        pagination_key (str, optional): Pagination key for retrieving subsequent data (Note: not used with official library)
        limit (int, optional): Maximum number of results to retrieve. Defaults to 10.
        start_position (int, optional): The starting position for the search. Defaults to 0.

    Returns:
        str: API response text containing trading data by investor type including individuals,
             foreigners, institutions, etc. with sales/purchase values and balances
    """
    try:
        client = get_client()

        # Build kwargs for the API call
        kwargs = {}
        if section:
            kwargs['section'] = section
        if from_yyyymmdd:
            kwargs['from_yyyymmdd'] = from_yyyymmdd
        if to_yyyymmdd:
            kwargs['to_yyyymmdd'] = to_yyyymmdd

        df = client.get_markets_trades_spec(**kwargs)

        # Apply pagination
        paginated_df = df.iloc[start_position:start_position + limit]

        return _convert_df_to_json(paginated_df, 'trades_spec')

    except Exception as e:
        error_response = {"error": str(e), "status": "error"}
        return json.dumps(error_response, ensure_ascii=False)


def main() -> None:
    print("Starting J-Quants MCP server!")
    mcp_server.run(transport="stdio")

if __name__ == "__main__":
    main()
