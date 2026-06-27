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

    @staticmethod
    def _date_dict(date_str: str) -> dict:
        y, m, d = (int(x) for x in date_str.split("-"))
        return {"year": y, "month": m, "day": d}