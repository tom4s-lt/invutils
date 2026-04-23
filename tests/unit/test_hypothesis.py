"""
Property-based tests using hypothesis.

Instead of writing individual cases (test_empty_id, test_whitespace_id, ...),
hypothesis generates many random inputs that satisfy a given strategy and verifies
that a stated property holds for ALL of them. If it finds a counterexample, it
shrinks it to the smallest failing input and reports that.

Key concepts demonstrated here:
  - st.one_of / st.integers / st.text / st.floats / st.lists / st.fixed_dictionaries
  - assume() — discard inputs that don't satisfy a precondition
  - @settings — control how many examples hypothesis generates
  - using patch() as a context manager inside @given tests
"""

from unittest.mock import patch

import pytest
from hypothesis import assume, given, settings
from hypothesis import strategies as st

from invutils.prices.coingecko import gecko_price_chart, gecko_price_current
from invutils.prices.defillama import llama_price_chart, llama_price_historical


# ---------------------------------------------------------------------------
# Reusable strategies
# ---------------------------------------------------------------------------

# Any Python value that is not a string — used to test TypeError guards
non_strings = st.one_of(
    st.integers(),
    st.floats(allow_nan=False),
    st.booleans(),
    st.none(),
    st.lists(st.text()),
    st.dictionaries(st.text(), st.text()),
)

# Strings that strip() to empty — use only the ASCII whitespace characters that
# Python's str.strip() removes so every generated string is valid without filtering.
whitespace_strings = st.text(alphabet=" \t\n\r\x0b\x0c", min_size=1)

# Valid-looking DefiLlama IDs (chain:address format)
defillama_ids = st.from_regex(r"[a-z]{2,12}:0x[0-9a-f]{4,40}", fullmatch=True)

# Non-integer types — used to test start/span TypeError guards on llama_price_chart.
# Excludes st.integers() and st.booleans() because both pass isinstance(x, int).
non_int = st.one_of(
    st.floats(allow_nan=False),
    st.none(),
    st.text(),
    st.lists(st.text()),
    st.dictionaries(st.text(), st.text()),
)

# Price points as DefiLlama's /chart endpoint returns them
price_points = st.fixed_dictionaries({
    "timestamp": st.integers(min_value=1_000_000_000, max_value=2_000_000_000),
    "price": st.floats(min_value=0.0, max_value=1e9, allow_nan=False, allow_infinity=False),
})


# ---------------------------------------------------------------------------
# Section 1: TypeError on non-string id
# Property: passing any non-string as id ALWAYS raises TypeError, regardless
# of what the value is. hypothesis will try integers, lists, dicts, None, etc.
# ---------------------------------------------------------------------------

class TestTypeErrorOnNonStringId:

    @given(bad_id=non_strings)
    def test_gecko_price_current(self, bad_id):
        with pytest.raises(TypeError, match="id must be a string"):
            gecko_price_current(bad_id)

    @given(bad_id=non_strings)
    def test_gecko_price_chart(self, bad_id):
        with pytest.raises(TypeError, match="id must be a string"):
            gecko_price_chart(bad_id)

    @given(bad_id=non_strings)
    def test_llama_price_historical(self, bad_id):
        with pytest.raises(TypeError, match="id must be a string"):
            llama_price_historical(bad_id)

    @given(bad_id=non_strings)
    def test_llama_price_chart(self, bad_id):
        with pytest.raises(TypeError, match="id must be a string"):
            llama_price_chart(bad_id, start=1_640_908_800, span=7)


# ---------------------------------------------------------------------------
# Section 2: ValueError on empty / whitespace-only id
# Property: any string that strips to "" ALWAYS raises ValueError.
# hypothesis generates far more whitespace variants than you'd write by hand.
# ---------------------------------------------------------------------------

class TestValueErrorOnEmptyId:

    @given(blank=whitespace_strings)
    def test_gecko_price_current(self, blank):
        with pytest.raises(ValueError, match="id cannot be empty"):
            gecko_price_current(blank)

    @given(blank=whitespace_strings)
    def test_gecko_price_chart(self, blank):
        with pytest.raises(ValueError, match="id cannot be empty"):
            gecko_price_chart(blank)

    @given(blank=whitespace_strings)
    def test_llama_price_historical(self, blank):
        with pytest.raises(ValueError, match="id cannot be empty"):
            llama_price_historical(blank)

    @given(blank=whitespace_strings)
    def test_llama_price_chart(self, blank):
        with pytest.raises(ValueError, match="id cannot be empty"):
            llama_price_chart(blank, start=1_640_908_800, span=7)


# ---------------------------------------------------------------------------
# Section 3: llama_price_chart numeric parameter guards
# Property: any non-positive integer for start or span ALWAYS raises ValueError.
# st.integers(max_value=0) generates 0, negatives, and large negatives.
# ---------------------------------------------------------------------------

class TestLlamaPriceChartNumericGuards:

    @given(bad_start=non_int)
    def test_start_type_error(self, bad_start):
        with pytest.raises(TypeError, match="start must be an integer"):
            llama_price_chart("ethereum:0x0000", start=bad_start, span=7)

    @given(bad_start=st.integers(max_value=0))
    def test_start_value_error(self, bad_start):
        with pytest.raises(ValueError, match="start must be positive"):
            llama_price_chart("ethereum:0x0000", start=bad_start, span=7)

    @given(bad_span=st.integers(max_value=0))
    def test_span_value_error(self, bad_span):
        with pytest.raises(ValueError, match="span must be positive"):
            llama_price_chart("ethereum:0x0000", start=1_640_908_800, span=bad_span)

    @given(bad_period=st.text().filter(lambda s: s not in ("5m", "15m", "30m", "1h", "4h", "1d")))
    def test_period_value_error(self, bad_period):
        # Any string that isn't a known period should raise ValueError
        assume(bad_period.strip())  # skip empty/whitespace — those hit a different guard
        with pytest.raises(ValueError, match="period must be one of"):
            llama_price_chart("ethereum:0x0000", start=1_640_908_800, span=7, period=bad_period)


# ---------------------------------------------------------------------------
# Section 4: Data invariants
# Property: response["count"] always equals len(response["data"]).
# This tests the transformation logic, not just the validation guards.
# hypothesis generates arbitrary lists of price points to feed as mock data.
# ---------------------------------------------------------------------------

class TestResponseInvariants:

    @given(prices=st.lists(price_points, min_size=0, max_size=100))
    @settings(max_examples=50)  # fewer examples since each call involves patching
    def test_llama_price_chart_count_matches_data(self, prices):
        coin_id = "ethereum:0x0000000000000000000000000000000000000000"
        mock_response = {"coins": {coin_id: {"prices": prices}}}

        with patch("invutils.prices.defillama.handle_api_request") as mock_api:
            mock_api.return_value = mock_response
            result = llama_price_chart(coin_id, start=1_640_908_800, span=max(len(prices), 1))

        # This must hold regardless of how many price points hypothesis generated
        assert result["count"] == len(result["data"])

    @given(prices=st.lists(price_points, min_size=1, max_size=100))
    @settings(max_examples=50)
    def test_gecko_price_chart_count_matches_data(self, prices):
        # CoinGecko returns [[timestamp_ms, price], ...] — convert to that shape
        cg_prices = [[p["timestamp"] * 1000, p["price"]] for p in prices]
        mock_response = {"prices": cg_prices}

        with patch("invutils.prices.coingecko.handle_api_request") as mock_api:
            mock_api.return_value = mock_response
            result = gecko_price_chart("bitcoin", days=len(prices))

        assert result["count"] == len(result["data"])

    @given(prices=st.lists(price_points, min_size=1, max_size=100))
    @settings(max_examples=50)
    def test_gecko_price_chart_timestamps_converted_to_seconds(self, prices):
        # Property: output timestamps are always the input ms timestamps divided by 1000
        cg_prices = [[p["timestamp"] * 1000, p["price"]] for p in prices]
        mock_response = {"prices": cg_prices}

        with patch("invutils.prices.coingecko.handle_api_request") as mock_api:
            mock_api.return_value = mock_response
            result = gecko_price_chart("bitcoin", days=len(prices))

        for i, point in enumerate(result["data"]):
            assert point["timestamp"] == int(cg_prices[i][0] / 1000)


# ---------------------------------------------------------------------------
# Section 5: Large-payload tests (T6)
# Parametrized tests with realistic response sizes to verify that count,
# data length, and structure hold at pagination boundaries and beyond.
# ---------------------------------------------------------------------------

_COIN_ID = "ethereum:0x0000000000000000000000000000000000000000"
_START_TS = 1_609_459_200  # 2021-01-01 00:00 UTC


def _make_llama_points(n: int) -> list:
    """Generate n synthetic DefiLlama chart price points spaced 1 day apart."""
    return [{"timestamp": _START_TS + i * 86400, "price": float(100 + i)} for i in range(n)]


def _make_gecko_prices(n: int) -> list:
    """Generate n synthetic CoinGecko [timestamp_ms, price] pairs spaced 1 day apart."""
    return [[(_START_TS + i * 86400) * 1000, float(100 + i)] for i in range(n)]


class TestLargePayloads:

    # llama_price_chart: below chunk limit, at limit, above (two chunks), well above
    @pytest.mark.parametrize("n_points,expected_calls", [
        (365, 1),   # typical historical range, single chunk
        (500, 1),   # exactly the chunk ceiling — still one call
        (501, 2),   # one point over → must split into two chunks
        (1000, 2),  # two full 500-point chunks
    ])
    def test_llama_price_chart_large_payload(self, n_points, expected_calls):
        points = _make_llama_points(n_points)
        # Each chunk call returns points; we make handle_api_request return a
        # response whose prices list covers all points so accumulation can be verified.
        mock_response = {"coins": {_COIN_ID: {"prices": points}}}

        with patch("invutils.prices.defillama.handle_api_request") as mock_api:
            mock_api.return_value = mock_response
            result = llama_price_chart(_COIN_ID, start=_START_TS, span=n_points)

        assert mock_api.call_count == expected_calls
        assert result["status"] == "success"
        # Each chunk call returns the full points list; accumulated count = calls × n_points
        assert result["count"] == expected_calls * n_points
        assert len(result["data"]) == result["count"]
        for point in result["data"]:
            assert "timestamp" in point
            assert "price" in point

    # gecko_price_chart: no pagination, just verify transformation at scale
    @pytest.mark.parametrize("n_points", [90, 180, 365])
    def test_gecko_price_chart_large_payload(self, n_points):
        cg_prices = _make_gecko_prices(n_points)
        mock_response = {"prices": cg_prices}

        with patch("invutils.prices.coingecko.handle_api_request") as mock_api:
            mock_api.return_value = mock_response
            result = gecko_price_chart("bitcoin", days=n_points)

        assert result["status"] == "success"
        assert result["count"] == n_points
        assert len(result["data"]) == n_points
        # Timestamps must be in seconds (not milliseconds)
        for i, point in enumerate(result["data"]):
            assert point["timestamp"] == int(cg_prices[i][0] / 1000)
            assert point["price"] == cg_prices[i][1]
