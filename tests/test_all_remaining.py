import json
import os
import datetime

import fitbitApp

curdir = os.path.dirname(__file__) + "/"

with open(f"{curdir}Config.json") as f:
    CONFIG = json.load(f)
with open(f"{curdir}Token.json") as f:
    TOKEN = json.load(f)

app = fitbitApp.app(TOKEN["access_token"], TOKEN["refresh_token"], CONFIG["CLIENT_ID"], curdir)

today = datetime.datetime.now().strftime("%Y-%m-%d")
yesterday = (datetime.datetime.now() - datetime.timedelta(days=1)).strftime("%Y-%m-%d")

date_based_methods = [
    "ActiveEnergyBurnedByDate",
    "ActiveMinutesByDate",
    "AltitudeByDate",
    "BloodGlucoseByDate",
    "CoreBodyTemperatureByDate",
    "DistanceByDate",
    "FloorsByDate",
    "HydrationLogByDate",
    "NutritionLogByDate",
    "RunVO2MaxByDate",
    "SedentaryPeriodByDate",
    "SwimLengthsDataByDate",
    "TimeInHeartRateZoneByDate",
    "TotalCaloriesByDate",
    "DailyHeartRateZonesByDate",
    "DailyOxygenSaturationByDate",
    "DailyRespiratoryRateByDate",
    "DailySleepTemperatureDerivationsByDate",
    "DailyVO2MaxByDate",
    "ActivityLevelByDate",
    "ElectrocardiogramByDate",
    "HeartRateVariabilityIntradayByDate",
    "OxygenSaturationIntradayByDate",
    "RespiratoryRateSleepSummaryByDate",
    "VO2MaxIntradayByDate",
]

no_date_methods = [
    "FoodList",
    "FoodMeasurementUnitList",
    "IrregularRhythmNotificationList",
]

results = {
    "ok_with_data": [],
    "ok_empty": [],
    "api_error": [],
    "exception": [],
}

def has_data(res: dict) -> bool:
    if "dataPoints" in res:
        return len(res["dataPoints"]) > 0
    if "rollupDataPoints" in res:
        return len(res["rollupDataPoints"]) > 0
    return False

print("=" * 60)
print("date指定系メソッド(today / yesterdayの両方を試行)")
print("=" * 60)

for name in date_based_methods:
    method = getattr(app, name)
    found_data = False
    last_res = None
    error_res = None
    exc = None

    for d in (today, yesterday):
        try:
            res = method(date=d)
        except Exception as e:
            exc = e
            continue

        last_res = res
        if isinstance(res, dict) and "error" in res:
            error_res = res
            continue
        if has_data(res):
            found_data = True
            last_res = res
            break

    if exc is not None and last_res is None:
        results["exception"].append((name, str(exc)))
        print(f"[EXCEPTION] {name}: {exc}")
    elif error_res is not None and not found_data:
        results["api_error"].append((name, error_res["error"]))
        print(f"[API ERROR] {name}: {error_res['error'].get('message')}")
    elif found_data:
        results["ok_with_data"].append(name)
        print(f"[OK / データあり] {name}")
        print(f"    {last_res}")
    else:
        results["ok_empty"].append(name)
        print(f"[OK / 空] {name}")

print()
print("=" * 60)
print("date指定なしメソッド")
print("=" * 60)

for name in no_date_methods:
    method = getattr(app, name)
    try:
        res = method(page_size=5)
    except Exception as e:
        results["exception"].append((name, str(e)))
        print(f"[EXCEPTION] {name}: {e}")
        continue

    if isinstance(res, dict) and "error" in res:
        results["api_error"].append((name, res["error"]))
        print(f"[API ERROR] {name}: {res['error'].get('message')}")
    elif has_data(res):
        results["ok_with_data"].append(name)
        print(f"[OK / データあり] {name}")
        print(f"    {res}")
    else:
        results["ok_empty"].append(name)
        print(f"[OK / 空] {name}")

print()
print("=" * 60)
print("まとめ")
print("=" * 60)
print(f"データあり: {len(results['ok_with_data'])}件 -> {results['ok_with_data']}")
print(f"空(正常):  {len(results['ok_empty'])}件 -> {results['ok_empty']}")
print(f"APIエラー: {len(results['api_error'])}件 -> {[r[0] for r in results['api_error']]}")
print(f"例外:      {len(results['exception'])}件 -> {[r[0] for r in results['exception']]}")
