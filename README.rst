fitbitApp
=========

1. Overview
-----------

A Python library to retrieve various health data (sleep, heart rate, weight, etc.) from the
**Google Health API** (the successor to the Fitbit Web API).
Supports Google OAuth 2.0 authentication and automatic token refresh.
Designed for personal use with full control over tokens and data fetching.

**Breaking change in v2.0.0**: this release migrates fully from the legacy Fitbit Web API
(sunsetting September 2026) to the Google Health API. There is no backward compatibility with
the v1.x implementation. If you need the legacy behavior, pin to ``fitbitApp<2.0.0``.

2. Changelog
------------

- v2.1.1: Verified the v2.1.0 convenience methods against live data. 27 of 27 reachable methods
  worked with zero filter-syntax bugs; 6 require optional nutrition/ecg/irn scopes not requested
  during testing. See GitHub README for the full breakdown.
- v2.1.0: Added convenience wrapper methods for nearly all remaining Google Health API data types
  (read-only only). Most are based on confirmed filter patterns but not yet individually verified
  against live data; see GitHub README for details.
- v2.0.0: Full migration to the Google Health API. Breaking change, no backward compatibility with v1.x.
- v1.1.0: Updated to support Fitbit Sleep API v1.2 and improved authentication logic.
- v1.0.0: Initial release with support for activity, heart rate, sleep, SpO2, weight, and other endpoints.

3. Usage
--------

For setup instructions and API usage examples, please see the project page on GitHub:

**GitHub Repository:** https://github.com/gitpomtec/fitbitApp

4. Reference
------------

- Google Health API: https://developers.google.com/health
- Migration guide (Fitbit Web API -> Google Health API): https://developers.google.com/health/migration
- Legacy Fitbit Web API reference (sunsetting Sept 2026): https://dev.fitbit.com/build/reference/web-api/
