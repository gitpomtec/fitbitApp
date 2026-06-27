# fitbitApp

Google Health API wrapper (formerly a Fitbit Web API wrapper)

> **⚠️ Breaking change in v2.0.0**
> Google is sunsetting the legacy Fitbit Web API in **September 2026** and replacing it with the
> [Google Health API](https://developers.google.com/health). Starting from v2.0.0, this library talks
> **only** to the Google Health API. There is no backward compatibility with the old Fitbit Web API.
> If you still need the legacy implementation, pin your dependency to `fitbitApp<2.0.0`.

## 1. Preparation

### 1.1 Register your app in Google Cloud Console

1. Go to the [Google Cloud Console](https://console.cloud.google.com/) and create a new project.
2. Enable the **Google Health API** for that project.
3. Configure the **OAuth consent screen**:
    - Audience: `External` (unless you have a Google Workspace organization)
    - Add yourself under **Test users** first to verify everything works.
    - Once verified, click **Publish app** to switch the publishing status to **In production**.
      This step matters: while a project is in `Testing` status, issued refresh tokens expire after
      **7 days**, which breaks any long-running / unattended setup. Apps for personal use (not shared,
      or used by fewer than 100 people you know) are exempt from Google's verification review, so you
      can safely publish without going through the full review process.
4. Create an **OAuth 2.0 Client ID** (Application type: **Web application**). Add a redirect URI such as
   `http://localhost:8000`.
5. Note down the **Client ID** and **Client Secret**.

### 1.2 Create a Config file

```json
{
    "CLIENT_ID": "Your OAuth 2.0 Client ID",
    "CLIENT_SECRET": "Your Client Secret"
}
```

Save this as `Config.json`.

### 1.3 Obtain an access token / refresh token

A helper script is provided at [`tools/get_google_token.py`](tools/get_google_token.py). Run it from a
machine that has a web browser available (the device running your long-lived script does not need to
have a browser itself):

```bash
python3 tools/get_google_token.py
```

This opens the Google consent screen in your browser, and on completion writes the result to
`Token.json` next to the script. Copy `Config.json` and `Token.json` to wherever your script using this
library will run.

Make sure the OAuth consent screen is in **production** status (see 1.1) *before* running this script,
otherwise the refresh token you obtain will expire in 7 days.

## 2. Usage

```python
import json
import fitbitApp
import os

curdir = os.path.dirname(__file__) + "/"

with open(f"{curdir}Config.json") as f:
    CONFIG = json.load(f)
with open(f"{curdir}Token.json") as f:
    TOKEN = json.load(f)

app = fitbitApp.app(TOKEN["access_token"], TOKEN["refresh_token"], CONFIG["CLIENT_ID"], curdir)

# Identity: legacy Fitbit user ID + new Google Health user ID
print(app.get_identity())

# Profile / settings
print(app.get_profile())
print(app.get_settings())

# Convenience wrappers for the most common data types
print(app.Steps())                                  # today's steps (daily rollup)
print(app.HeartRateIntradayByDate())                 # today's intraday heart rate
print(app.SleepLogByDate(date="2026-06-27"))         # sleep ending on the given date
print(app.WeightLog())                               # today's weight log (empty dict if no entry)

# Generic access to any of the 31 supported data types
print(app.list_data_points(
    "steps",
    filter_expr='steps.interval.civil_start_time >= "2026-06-01T00:00:00"',
))
print(app.daily_roll_up(
    "weight",
    start_date={"date": {"year": 2026, "month": 6, "day": 1}, "time": {}},
    end_date={"date": {"year": 2026, "month": 6, "day": 1}, "time": {"hours": 23, "minutes": 59, "seconds": 59}},
))
```

See the [Google Health API data types reference](https://developers.google.com/health/data-types) for
the full list of supported `data_type` identifiers and which methods (`list` / `reconcile` / `rollUp` /
`dailyRollUp`) each one supports.

### Notes

- **Nutrition data is not available** in the Google Health API at this time. If your application relied
  on `FoodLog()` / `WaterLog()` from the legacy v1.x implementation, there is currently no replacement.
- Access tokens expire after **1 hour** (down from Fitbit's 8 hours). The `oauth2` class transparently
  refreshes on a `401` response, so this should not require any action on your part.

## 3. Running tests

Integration tests live under `tests/` and call the live Google Health API using your own credentials.

```bash
pip install -r requirements-dev.txt
cp Config.json Token.json tests/
pytest tests/ -v
```

`tests/Config.json` and `tests/Token.json` are excluded via `.gitignore` and should never be committed.

## 4. Changelog

- **v2.1.0**: Added convenience wrapper methods for nearly all remaining Google Health API data
  types (read-only: list/reconcile/rollUp/dailyRollUp — no create/update/delete). Methods for
  `steps`, `heart-rate`, `sleep`, `weight`, `body-fat`, `daily-heart-rate-variability`,
  `daily-resting-heart-rate`, `active-zone-minutes`, `calories-in-heart-rate-zone`, `height`, and
  `exercise` have been tested against real data. **The remaining ~28 methods follow the same
  filter patterns but have not yet been individually verified against the live API** — if you hit
  a `400 INVALID_DATA_POINT_FILTER` error, please open an issue with the response body so the
  filter can be corrected (this is exactly how the tested methods were fixed during development).
- **v2.0.0**: Full migration from the legacy Fitbit Web API to the Google Health API. Breaking change —
  no backward compatibility with v1.x.
- v1.1.0: Updated to support Fitbit Sleep API v1.2 and improved authentication logic.
- v1.0.0: Initial release with support for activity, heart rate, sleep, SpO2, weight, and other endpoints.

## 5. Reference

- Google Health API: https://developers.google.com/health
- Migration guide (Fitbit Web API → Google Health API): https://developers.google.com/health/migration
- Legacy Fitbit Web API reference (sunsetting Sept 2026): https://dev.fitbit.com/build/reference/web-api/
