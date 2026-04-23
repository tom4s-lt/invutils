# invutils — Claude Context

Thin Python client for crypto price APIs (CoinGecko, DefiLlama). Stateless, no pandas.

## Design rules (must follow)

1. **Standardized response envelope** — every public function returns:
   `{"source": str, "fetched_at": int, "status": "success"|"error", "count": int, "data": list[dict]}`.
   Historical variants may add `coin_id`, `currency`, `period`, `requested_timestamp` as needed, but never break the five core keys.
2. **No pandas** — return plain lists of dicts. Callers (e.g. personal_finance) own the DataFrame layer.
3. **Input validation at the top of every public function** — `TypeError` for wrong types, `ValueError` for empty/invalid values. See existing funcs for the pattern.
4. **Errors are logged and swallowed** — `handle_api_request` catches HTTP/Timeout/Connection/JSON errors and returns `None`. Callers detect failure via `status == "error"`, not exceptions. Do not raise on network failure.
5. **No domain knowledge** — no concepts of portfolios, ledgers, wallets, fixed/tied/ffill assets. Those belong in consumers.

## Primary consumer

`personal_finance` (`/Users/tomas/tom4s/workspace/git-projects/personal_finance/`) — its ETL pipeline drives most feature requests. Changes that break its call sites need a version bump and a matching PR in that repo (see `PLAN.md` Phase A5).

## Adding a new provider

1. Create `invutils/prices/<provider>.py`.
2. Add base URL + endpoints to `invutils/config.py` (`<PROVIDER>_ENDPOINTS` dict).
3. Implement functions with the response envelope above.
4. Export from `invutils/prices/__init__.py` and `invutils/__init__.py`.
5. Unit tests in `tests/unit/test_<provider>.py` using the `responses` library (currently `@patch` — migrate in Phase C1).
6. Update README (API reference) and bump `__version__` in `invutils/__init__.py`.

## Testing

- Unit tests are mocked; they run without network and without API keys: `pytest -m "not integration"`.
- Integration tests require `COINGECKO_API_KEY` in `.env` and run against real APIs.
- Coverage target: keep the existing level or raise; never drop below.

## Version bump convention

Semver on `invutils/__init__.py::__version__`. Minor bump for new functions, patch for fixes, major for envelope-breaking changes. Tag releases `v{version}`.

## Roadmap

See `PLAN.md`.
