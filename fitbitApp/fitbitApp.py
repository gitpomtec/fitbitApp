import requests
import json
import datetime

today = datetime.datetime.now().strftime("%Y-%m-%d")


class oauth2:
    """
    Google Health API 用のOAuth2クライアント。
    旧FitbitのOAuth実装(Basic認証ヘッダー)とは異なり、
    Googleはclient_id/client_secretをリクエストボディに含める形式。
    """

    TOKEN_URL = "https://oauth2.googleapis.com/token"

    def __init__(self, access_token, refresh_token, client_id, curdir):
        self.acctoken = access_token
        self.reftoken = refresh_token
        self.clntid = client_id
        self.curdir = curdir

        with open(f"{curdir}Config.json", "r") as f:
            self.client_secret = json.load(f)["CLIENT_SECRET"]

    def create_header(self):
        return {
            "Authorization": f"Bearer {self.acctoken}",
            "Accept": "application/json",
        }

    def refresh(self):
        data = {
            "client_id": self.clntid,
            "client_secret": self.client_secret,
            "refresh_token": self.reftoken,
            "grant_type": "refresh_token",
        }

        try:
            res = requests.post(self.TOKEN_URL, data=data)
            res_data = res.json()
        except Exception as e:
            print(f"Failed to refresh token: {e}")
            return False

        if res.status_code != 200:
            print(f"Token refresh failed. Status: {res.status_code}")
            print(res_data)
            return False

        res_data.setdefault("refresh_token", self.reftoken)

        with open(f"{self.curdir}Token.json", "w", encoding="utf-8") as f:
            json.dump(res_data, f, indent=2, ensure_ascii=False)

        self.acctoken = res_data["access_token"]
        self.reftoken = res_data["refresh_token"]
        return True

    def request(self, method, url, **kw):
        if "headers" not in kw:
            kw["headers"] = self.create_header()

        res = method(url, **kw)

        if res.status_code == 401:
            if self.refresh():
                kw["headers"] = self.create_header()
                res = method(url, **kw)

        return res


class app(oauth2):

    BASE = "https://health.googleapis.com/v4/users/me"

    def list_data_points(self, data_type: str, filter_expr: str = None,
                          page_size: int = 1000, page_token: str = None):
        url = f"{self.BASE}/dataTypes/{data_type}/dataPoints"
        params = {"pageSize": page_size}
        if filter_expr:
            params["filter"] = filter_expr
        if page_token:
            params["pageToken"] = page_token

        res = self.request(requests.get, url, headers=self.create_header(), params=params)
        return res.json()

    def reconcile_data_points(self, data_type: str, filter_expr: str = None,
                               page_size: int = 1000, page_token: str = None):
        url = f"{self.BASE}/dataTypes/{data_type}/dataPoints:reconcile"
        params = {"pageSize": page_size}
        if filter_expr:
            params["filter"] = filter_expr
        if page_token:
            params["pageToken"] = page_token

        res = self.request(requests.get, url, headers=self.create_header(), params=params)
        return res.json()

    def roll_up(self, data_type: str, start_time: str, end_time: str, window_size_seconds: int):
        url = f"{self.BASE}/dataTypes/{data_type}/dataPoints:rollUp"
        body = {
            "range": {"startTime": start_time, "endTime": end_time},
            "windowSize": f"{window_size_seconds}s",
        }
        res = self.request(requests.post, url, headers=self.create_header(), json=body)
        return res.json()

    def daily_roll_up(self, data_type: str, start_date: dict, end_date: dict, window_size_days: int = 1):
        url = f"{self.BASE}/dataTypes/{data_type}/dataPoints:dailyRollUp"
        body = {
            "range": {"start": start_date, "end": end_date},
            "windowSizeDays": window_size_days,
        }
        res = self.request(requests.post, url, headers=self.create_header(), json=body)
        return res.json()

    def delete_data_points(self, data_type: str, names: list):
        url = f"{self.BASE}/dataTypes/{data_type}/dataPoints:batchDelete"
        body = {"names": names}
        res = self.request(requests.post, url, headers=self.create_header(), json=body)
        return res.json()

    def get_identity(self):
        url = f"{self.BASE}/identity"
        res = self.request(requests.get, url, headers=self.create_header())
        return res.json()

    def get_profile(self):
        url = f"{self.BASE}/profile"
        res = self.request(requests.get, url, headers=self.create_header())
        return res.json()

    def get_settings(self):
        url = f"{self.BASE}/settings"
        res = self.request(requests.get, url, headers=self.create_header())
        return res.json()

    def get_paired_devices(self):
        url = f"{self.BASE}/pairedDevices"
        res = self.request(requests.get, url, headers=self.create_header())
        return res.json()

    def Steps(self, date: str = today):
        start = {"date": self._date_dict(date), "time": {"hours": 0, "minutes": 0, "seconds": 0}}
        end = {"date": self._date_dict(date), "time": {"hours": 23, "minutes": 59, "seconds": 59}}
        return self.daily_roll_up("steps", start, end)

    def HeartRateIntradayByDate(self, date: str = today):
        filter_expr = (
            f'heart_rate.sample_time.physical_time >= "{date}T00:00:00Z" '
            f'AND heart_rate.sample_time.physical_time < "{date}T23:59:59Z"'
        )
        return self.list_data_points("heart-rate", filter_expr=filter_expr)

    def SleepLogByDate(self, date: str = today):
        """
        date: 起床日(目が覚めた日)を指定する。
        Sleepデータタイプは civil_start_time でのフィルターをサポートしていないため、
        civil_end_time(起床時刻側)の範囲で絞り込む。
        """
        next_day = (datetime.datetime.strptime(date, "%Y-%m-%d") + datetime.timedelta(days=1)).strftime("%Y-%m-%d")
        filter_expr = (
            f'sleep.interval.civil_end_time >= "{date}T00:00:00" '
            f'AND sleep.interval.civil_end_time < "{next_day}T00:00:00"'
        )
        return self.list_data_points("sleep", filter_expr=filter_expr)

    def WeightLog(self, date: str = today):
        start = {"date": self._date_dict(date), "time": {"hours": 0, "minutes": 0, "seconds": 0}}
        end = {"date": self._date_dict(date), "time": {"hours": 23, "minutes": 59, "seconds": 59}}
        return self.daily_roll_up("weight", start, end)

    def Profile(self):
        return self.get_profile()
    
    def HRVSummaryByDate(self, date: str = today):
        """
        daily-heart-rate-variability は date(1日1点)のデータタイプ。
        date フィールドは等価比較(=)をサポートしないため、
        「指定日 <= date < 翌日」という範囲指定で絞り込む。
        旧Fitbitの dailyRmssd に近い値は averageHeartRateVariabilityMilliseconds。
        """
        next_day = (datetime.datetime.strptime(date, "%Y-%m-%d") + datetime.timedelta(days=1)).strftime("%Y-%m-%d")
        filter_expr = f'daily_heart_rate_variability.date >= "{date}" AND daily_heart_rate_variability.date < "{next_day}"'
        return self.list_data_points("daily-heart-rate-variability", filter_expr=filter_expr)

    def RestingHeartRateByDate(self, date: str = today):
        """daily-resting-heart-rate も date(1日1点)のデータタイプ。同様に範囲指定で絞り込む。"""
        next_day = (datetime.datetime.strptime(date, "%Y-%m-%d") + datetime.timedelta(days=1)).strftime("%Y-%m-%d")
        filter_expr = f'daily_resting_heart_rate.date >= "{date}" AND daily_resting_heart_rate.date < "{next_day}"'
        return self.list_data_points("daily-resting-heart-rate", filter_expr=filter_expr)

    def ActiveZoneMinutesByDate(self, date: str = today):
        """
        旧Fitbitは合計1つの値だったが、Google Health APIでは
        fat_burn / cardio / peak の3ゾーンに分かれて返る(rollupDataPoints[0].activeZoneMinutes内)。
        合算するかどうかは呼び出し側で判断する。
        """
        start = {"date": self._date_dict(date), "time": {}}
        end = {"date": self._date_dict(date), "time": {"hours": 23, "minutes": 59, "seconds": 59}}
        return self.daily_roll_up("active-zone-minutes", start, end)

    def CaloriesInHeartRateZoneByDate(self, date: str = today):
        """
        旧FitbitのDailyActivitySummary内heartRateZones(zones[1:4]の合計)に相当。
        レスポンスは rollupDataPoints[0].caloriesInHeartRateZone.caloriesInHeartRateZones[]
        というリスト(各要素に heartRateZone, kcal)で返る。合算は呼び出し側で行う。
        """
        start = {"date": self._date_dict(date), "time": {}}
        end = {"date": self._date_dict(date), "time": {"hours": 23, "minutes": 59, "seconds": 59}}
        return self.daily_roll_up("calories-in-heart-rate-zone", start, end)

    def BodyFatByDate(self, date: str = today):
        """body-fat も weight と同じ daily_roll_up パターン。"""
        start = {"date": self._date_dict(date), "time": {}}
        end = {"date": self._date_dict(date), "time": {"hours": 23, "minutes": 59, "seconds": 59}}
        return self.daily_roll_up("body-fat", start, end)
    
    def get_latest_height_meters(self):
        """
        Google Health APIにはBMIという独立したデータタイプが無いため、
        身長(height)の最新値を取得して自前でBMIを計算するために使う。
        身長はめったに変わらないため、フィルター無しでlist_data_pointsを呼び、
        (観測上)新しい記録順に返ってくる先頭を採用する。
        値が見つからない場合は None を返す。
        """
        res = self.list_data_points("height", page_size=1)
        points = res.get("dataPoints", [])
        if not points:
            return None
        height_mm = points[0].get("height", {}).get("heightMillimeters")
        if height_mm is None:
            return None
        return float(height_mm) / 1000.0

    # ============================================================
    # 共通ヘルパー(以下の全データタイプ別メソッドで使用)
    # ============================================================

    def _daily_window(self, date: str):
        """指定日の00:00:00〜23:59:59のdaily_roll_up用start/end辞書を作る"""
        start = {"date": self._date_dict(date), "time": {}}
        end = {"date": self._date_dict(date), "time": {"hours": 23, "minutes": 59, "seconds": 59}}
        return start, end

    def _date_range_filter(self, field_prefix: str, date: str) -> str:
        """
        「Daily」記録タイプ(1日1点、dateフィールドのみ)用のフィルターを作る。
        等価比較(=)は使えないため、範囲指定(>=, <)にする。
        例: field_prefix="daily_heart_rate_variability" → "daily_heart_rate_variability.date"
        """
        next_day = (datetime.datetime.strptime(date, "%Y-%m-%d") + datetime.timedelta(days=1)).strftime("%Y-%m-%d")
        return f'{field_prefix}.date >= "{date}" AND {field_prefix}.date < "{next_day}"'

    def _civil_interval_filter(self, field_prefix: str, date: str) -> str:
        """
        Session/Interval系で interval.civil_start_time が使えるデータタイプ用のフィルター。
        (Sleepのように civil_start_time が使えない例外もあるため、エラーが出たら civil_end_time に切り替える)
        """
        next_day = (datetime.datetime.strptime(date, "%Y-%m-%d") + datetime.timedelta(days=1)).strftime("%Y-%m-%d")
        return (
            f'{field_prefix}.interval.civil_start_time >= "{date}T00:00:00" '
            f'AND {field_prefix}.interval.civil_start_time < "{next_day}T00:00:00"'
        )

    def _physical_day_filter(self, field_prefix: str, sample_field: str, date: str) -> str:
        """
        Sample系(心拍のような連続データ)で sample_time.physical_time を使うフィルター。
        日付はUTC基準になる(HeartRateIntradayByDateと同じ既知の制約)。
        """
        return (
            f'{field_prefix}.{sample_field}.physical_time >= "{date}T00:00:00Z" '
            f'AND {field_prefix}.{sample_field}.physical_time < "{date}T23:59:59Z"'
        )

    # ============================================================
    # dailyRollup対応(Steps/Weight/BodyFat/ActiveZoneMinutes/CaloriesInHeartRateZoneと同パターン)
    # ============================================================

    def ActiveEnergyBurnedByDate(self, date: str = today):
        start, end = self._daily_window(date)
        return self.daily_roll_up("active-energy-burned", start, end)

    def ActiveMinutesByDate(self, date: str = today):
        start, end = self._daily_window(date)
        return self.daily_roll_up("active-minutes", start, end)

    def AltitudeByDate(self, date: str = today):
        start, end = self._daily_window(date)
        return self.daily_roll_up("altitude", start, end)

    def BloodGlucoseByDate(self, date: str = today):
        start, end = self._daily_window(date)
        return self.daily_roll_up("blood-glucose", start, end)

    def CoreBodyTemperatureByDate(self, date: str = today):
        start, end = self._daily_window(date)
        return self.daily_roll_up("core-body-temperature", start, end)

    def DistanceByDate(self, date: str = today):
        start, end = self._daily_window(date)
        return self.daily_roll_up("distance", start, end)

    def FloorsByDate(self, date: str = today):
        start, end = self._daily_window(date)
        return self.daily_roll_up("floors", start, end)

    def HydrationLogByDate(self, date: str = today):
        start, end = self._daily_window(date)
        return self.daily_roll_up("hydration-log", start, end)

    def NutritionLogByDate(self, date: str = today):
        start, end = self._daily_window(date)
        return self.daily_roll_up("nutrition-log", start, end)

    def RunVO2MaxByDate(self, date: str = today):
        start, end = self._daily_window(date)
        return self.daily_roll_up("run-vo2-max", start, end)

    def SedentaryPeriodByDate(self, date: str = today):
        start, end = self._daily_window(date)
        return self.daily_roll_up("sedentary-period", start, end)

    def SwimLengthsDataByDate(self, date: str = today):
        start, end = self._daily_window(date)
        return self.daily_roll_up("swim-lengths-data", start, end)

    def TimeInHeartRateZoneByDate(self, date: str = today):
        start, end = self._daily_window(date)
        return self.daily_roll_up("time-in-heart-rate-zone", start, end)

    def TotalCaloriesByDate(self, date: str = today):
        start, end = self._daily_window(date)
        return self.daily_roll_up("total-calories", start, end)

    # ============================================================
    # 「Daily」記録タイプ(1日1点、HRV/RHRと同パターン)
    # ============================================================

    def DailyHeartRateZonesByDate(self, date: str = today):
        filter_expr = self._date_range_filter("daily_heart_rate_zones", date)
        return self.list_data_points("daily-heart-rate-zones", filter_expr=filter_expr)

    def DailyOxygenSaturationByDate(self, date: str = today):
        filter_expr = self._date_range_filter("daily_oxygen_saturation", date)
        return self.list_data_points("daily-oxygen-saturation", filter_expr=filter_expr)

    def DailyRespiratoryRateByDate(self, date: str = today):
        filter_expr = self._date_range_filter("daily_respiratory_rate", date)
        return self.list_data_points("daily-respiratory-rate", filter_expr=filter_expr)

    def DailySleepTemperatureDerivationsByDate(self, date: str = today):
        filter_expr = self._date_range_filter("daily_sleep_temperature_derivations", date)
        return self.list_data_points("daily-sleep-temperature-derivations", filter_expr=filter_expr)

    def DailyVO2MaxByDate(self, date: str = today):
        filter_expr = self._date_range_filter("daily_vo2_max", date)
        return self.list_data_points("daily-vo2-max", filter_expr=filter_expr)

    # ============================================================
    # Session/Interval系(Exerciseと同パターン。civil_start_timeが使えるか未確認のものを含む)
    # ============================================================

    def ExerciseLogByDate(self, date: str = today):
        """動作確認済み(civil_start_timeが使える)"""
        filter_expr = self._civil_interval_filter("exercise", date)
        return self.list_data_points("exercise", filter_expr=filter_expr)

    def ActivityLevelByDate(self, date: str = today):
        filter_expr = self._civil_interval_filter("activity_level", date)
        return self.list_data_points("activity-level", filter_expr=filter_expr)

    def ElectrocardiogramByDate(self, date: str = today):
        filter_expr = self._civil_interval_filter("electrocardiogram", date)
        return self.list_data_points("electrocardiogram", filter_expr=filter_expr)

    # ============================================================
    # Sample系(HeartRateIntradayByDateと同パターン。sample_time.physical_timeを使用)
    # ============================================================

    def HeartRateVariabilityIntradayByDate(self, date: str = today):
        filter_expr = self._physical_day_filter("heart_rate_variability", "sample_time", date)
        return self.list_data_points("heart-rate-variability", filter_expr=filter_expr)

    def OxygenSaturationIntradayByDate(self, date: str = today):
        filter_expr = self._physical_day_filter("oxygen_saturation", "sample_time", date)
        return self.list_data_points("oxygen-saturation", filter_expr=filter_expr)

    def RespiratoryRateSleepSummaryByDate(self, date: str = today):
        filter_expr = self._physical_day_filter("respiratory_rate_sleep_summary", "sample_time", date)
        return self.list_data_points("respiratory-rate-sleep-summary", filter_expr=filter_expr)

    def VO2MaxIntradayByDate(self, date: str = today):
        filter_expr = self._physical_day_filter("vo2_max", "sample_time", date)
        return self.list_data_points("vo2-max", filter_expr=filter_expr)

    # ============================================================
    # その他(日付に紐づかないカタログ系・通知系)
    # ============================================================

    def FoodList(self, page_size: int = 100, page_token: str = None):
        """ユーザーが登録した食品カタログの一覧(日付では絞り込まない)"""
        return self.list_data_points("food", page_size=page_size, page_token=page_token)

    def FoodMeasurementUnitList(self, page_size: int = 100, page_token: str = None):
        return self.list_data_points("food-measurement-unit", page_size=page_size, page_token=page_token)

    def IrregularRhythmNotificationList(self, page_size: int = 100, page_token: str = None):
        """心房細動(AFib)の兆候通知。件数が少ないため日付絞り込みなしで全件取得する想定"""
        return self.list_data_points("irregular-rhythm-notification", page_size=page_size, page_token=page_token)

    @staticmethod
    def _date_dict(date_str: str) -> dict:
        y, m, d = (int(x) for x in date_str.split("-"))
        return {"year": y, "month": m, "day": d}