import os
import json
from datetime import datetime
from typing import Optional
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

        # Convert DataFrame to list of dicts
        all_data = df.to_dict(orient='records')

        # Filter by query (case-insensitive search in CompanyName and CompanyNameEnglish)
        filtered_data = [
            r for r in all_data
            if (
                query.lower() in str(r.get("CompanyName", "")).lower()
                or
                query.lower() in str(r.get("CompanyNameEnglish", "")).lower()
            )
        ]

        # Apply pagination
        paginated_data = filtered_data[start_position:start_position + limit]

        response = {'info': paginated_data}
        return json.dumps(response, ensure_ascii=False)

    except Exception as e:
        error_response = {"error": str(e), "status": "error"}
        return json.dumps(error_response, ensure_ascii=False)



@mcp_server.tool()
def get_daily_quotes(
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
    try:
        client = get_client()

        # Parse date strings to datetime objects
        start_dt = datetime.strptime(from_date, "%Y-%m-%d")
        end_dt = datetime.strptime(to_date, "%Y-%m-%d")

        df = client.get_prices_daily_quotes(code=code, from_date=from_date, to_date=to_date)

        # Convert DataFrame to list of dicts
        all_data = df.to_dict(orient='records')

        # Apply pagination
        paginated_data = all_data[start_position:start_position + limit]

        response = {'daily_quotes': paginated_data}
        return json.dumps(response, ensure_ascii=False)

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

        # Convert DataFrame to list of dicts
        all_data = df.to_dict(orient='records')

        # Remove empty values from each record
        filtered_data = [
            {k: v for k, v in r.items() if v != ""}
            for r in all_data
        ]

        # Apply pagination
        paginated_data = filtered_data[start_position:start_position + limit]

        response = {'statements': paginated_data}
        return json.dumps(response, ensure_ascii=False)

    except Exception as e:
        error_response = {"error": str(e), "status": "error"}
        return json.dumps(error_response, ensure_ascii=False)


@mcp_server.tool()
def get_topix_prices(
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
        pagination_key (str, optional): Pagination key for retrieving subsequent data (Note: not used with official library)
        limit (int, optional): Maximum number of results to retrieve. Defaults to 10.
        start_position (int, optional): The starting position for the search. Defaults to 0.

    Returns:
        str: API response text containing TOPIX OHLC data
    """
    try:
        client = get_client()
        df = client.get_indices_topix(from_date=from_date, to_date=to_date)

        # Convert DataFrame to list of dicts
        all_data = df.to_dict(orient='records')

        # Apply pagination
        paginated_data = all_data[start_position:start_position + limit]

        response = {'topix': paginated_data}
        return json.dumps(response, ensure_ascii=False)

    except Exception as e:
        error_response = {"error": str(e), "status": "error"}
        return json.dumps(error_response, ensure_ascii=False)


@mcp_server.tool()
def get_trades_spec(
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
        if from_date:
            kwargs['from_date'] = from_date
        if to_date:
            kwargs['to_date'] = to_date

        df = client.get_markets_trades_spec(**kwargs)

        # Convert DataFrame to list of dicts
        all_data = df.to_dict(orient='records')

        # Apply pagination
        paginated_data = all_data[start_position:start_position + limit]

        response = {'trades_spec': paginated_data}
        return json.dumps(response, ensure_ascii=False)

    except Exception as e:
        error_response = {"error": str(e), "status": "error"}
        return json.dumps(error_response, ensure_ascii=False)


def main() -> None:
    print("Starting J-Quants MCP server!")
    mcp_server.run(transport="stdio")

if __name__ == "__main__":
    main()
