"""Pytest configuration and shared fixtures for invutils tests."""

import os
from typing import Any, Dict

import pytest
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

# ==============================================
# Configuration Fixtures
# ==============================================


@pytest.fixture(scope="session")
def coingecko_api_key() -> str:
    """
    Load CoinGecko API key from environment.

    Integration tests that require a CoinGecko API key will be skipped
    if this environment variable is not set.

    Returns:
        CoinGecko Demo API key from COINGECKO_API_KEY env var
    """
    api_key = os.getenv("COINGECKO_API_KEY")
    if not api_key:
        pytest.skip("COINGECKO_API_KEY environment variable not set")
    return api_key


@pytest.fixture(scope="session")
def skip_integration(request):
    """
    Helper fixture to skip integration tests.

    Integration tests are skipped by default unless explicitly run with:
        pytest -m integration
    """
    if request.config.getoption("-m") != "integration":
        pytest.skip("Integration tests not selected (use -m integration)")


# ==============================================
# Mock Data Fixtures
# ==============================================


@pytest.fixture
def mock_gecko_price_current_response() -> Dict[str, Any]:
    """
    Mock response for CoinGecko current price endpoint.

    Example response for bitcoin,ethereum vs usd
    """
    return {"bitcoin": {"usd": 45000.0}, "ethereum": {"usd": 2500.0}}


@pytest.fixture
def mock_gecko_price_historical_response() -> Dict[str, Any]:
    """
    Mock response for CoinGecko historical price endpoint.

    Example response with 3 data points
    """
    return {
        "prices": [
            [1640908800000, 44500.0],  # Timestamp in milliseconds
            [1640995200000, 45000.0],
            [1641081600000, 45500.0],
        ],
        "market_caps": [
            [1640908800000, 840000000000],
            [1640995200000, 850000000000],
            [1641081600000, 860000000000],
        ],
        "total_volumes": [
            [1640908800000, 30000000000],
            [1640995200000, 31000000000],
            [1641081600000, 32000000000],
        ],
    }


@pytest.fixture
def mock_llama_price_historical_response() -> Dict[str, Any]:
    """
    Mock response for DefiLlama price endpoint.

    Example response for ethereum native token
    """
    return {
        "coins": {
            "ethereum:0x0000000000000000000000000000000000000000": {
                "decimals": 18,
                "symbol": "ETH",
                "price": 2500.0,
                "timestamp": 1640908800,
                "confidence": 0.99,
            }
        }
    }


@pytest.fixture
def sample_coin_ids() -> Dict[str, Any]:
    """
    Sample coin IDs for testing.

    Returns dict with common coin IDs for different APIs.
    """
    return {
        "coingecko": {
            "single": "bitcoin",
            "multiple": "bitcoin,ethereum",
            "invalid": "invalid-coin-id-12345",
        },
        "defillama": {
            "eth_native": "ethereum:0x0000000000000000000000000000000000000000",
            "dai_token": "ethereum:0x6b175474e89094c44da98b954eedeac495271d0f",
            "multiple": "ethereum:0x0000000000000000000000000000000000000000,ethereum:0x6b175474e89094c44da98b954eedeac495271d0f",
            "invalid": "invalid:0xinvalidaddress",
        },
    }


@pytest.fixture
def sample_timestamps() -> Dict[str, int]:
    """
    Sample UNIX timestamps for testing.

    Returns dict with various timestamps for testing.
    """
    return {
        "recent": 1640908800,  # Jan 1, 2022
        "old": 1577836800,  # Jan 1, 2020
        "very_old": 1420070400,  # Jan 1, 2015
    }


# ==============================================
# Test Helper Functions
# ==============================================


def assert_success_response(response: Dict[str, Any], source: str) -> None:
    """
    Helper to assert standard success response structure.

    Args:
        response: Response dict to validate
        source: Expected source name ('coingecko' or 'defillama')
    """
    assert isinstance(response, dict), "Response should be a dict"
    assert response["source"] == source, f"Source should be {source}"
    assert response["status"] == "success", "Status should be success"
    assert "fetched_at" in response, "Response should include fetched_at timestamp"
    assert response["count"] > 0, "Count should be greater than 0 for success"
    assert isinstance(response["data"], list), "Data should be a list"
    assert len(response["data"]) == response["count"], "Data length should match count"


def assert_error_response(response: Dict[str, Any], source: str) -> None:
    """
    Helper to assert standard error response structure.

    Args:
        response: Response dict to validate
        source: Expected source name ('coingecko' or 'defillama')
    """
    assert isinstance(response, dict), "Response should be a dict"
    assert response["source"] == source, f"Source should be {source}"
    assert response["status"] == "error", "Status should be error"
    assert "fetched_at" in response, "Response should include fetched_at timestamp"
    assert response["count"] == 0, "Count should be 0 for error"
    assert isinstance(response["data"], list), "Data should be a list"
    assert len(response["data"]) == 0, "Data should be empty for error"
