import requests
import json
import datetime
import base64

today = datetime.datetime.now().strftime("%Y-%m-%d")
timenow = datetime.datetime.now().strftime("%H:%M")

class oauth2:
    def __init__(self, access_token, refresh_token, client_id, curdir):
        self.acctoken = access_token
        self.reftoken = refresh_token
        self.clntid = client_id
        self.curdir = curdir

        # client_secret の読み込み（新仕様対応）
        with open(f"{curdir}Config.json", "r") as f:
            self.client_secret = json.load(f)["CLIENT_SECRET"]

    def create_header(self):
        return {
            "Authorization": f"Bearer {self.acctoken}"
        }

    def refresh(self):
        url = "https://api.fitbit.com/oauth2/token"
        auth_header = base64.b64encode(f"{self.clntid}:{self.client_secret}".encode()).decode()
        headers = {
            "Authorization": f"Basic {auth_header}",
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json"
        }
        data = {
            "grant_type": "refresh_token",
            "refresh_token": self.reftoken
        }

        try:
            res = requests.post(url, headers=headers, data=data)
            res_data = res.json()
        except Exception as e:
            print(f"Failed to refresh token: {e}")
            return

        if res.status_code != 200:
            print(f"Token refresh failed. Status: {res.status_code}")
            print(res_data)
            return

        with open(f"{self.curdir}Token.json", "w", encoding="utf-8") as f:
            json.dump(res_data, f, indent=2)

        # Update tokens in memory
        self.acctoken = res_data["access_token"]
        self.reftoken = res_data["refresh_token"]

    def is_expired(self, resObj) -> bool:
        errors = resObj.get("errors")
        if not errors:
            return False
        return any(err.get("errorType") == "expired_token" for err in errors)

    def request(self, method, url, **kw):
        if "headers" not in kw:
            kw["headers"] = self.create_header()

        res = method(url, **kw)
        try:
            res_data = res.json()
        except Exception:
            return res  # 非JSONレスポンスはそのまま返す

        if self.is_expired(res_data):
            self.refresh()
            kw["headers"] = self.create_header()
            res = method(url, **kw)

        return res

class app(oauth2):

    # Get AZM Time Series by Date
    def AZMTimeSeriesByDate(self, date: str = "today", period: str = "1d"):
        url = f"https://api.fitbit.com/1/user/-/activities/active-zone-minutes/date/{date}/{period}.json"
        headers = super().create_header()
        res = super().request(requests.get, url, headers=headers)

        return json.loads(res.text)
    
    # Get AZM Time Series by Interval
    def AZMTimeSeriesByInterval(self, startdate: str = "today", enddate: str = "today"):
        url = f"https://api.fitbit.com/1/user/-/activities/active-zone-minutes/date/{startdate}/{enddate}.json"
        headers = super().create_header()
        res = super().request(requests.get, url, headers=headers)

        return json.loads(res.text)
    
    # Get Activity Goals
    def ActivityGoals(self, period: str = "daily"):
        url = f"https://api.fitbit.com/1/user/-/activities/goals/{period}.json"
        headers = super().create_header()
        res = super().request(requests.get, url, headers=headers)

        return json.loads(res.text)
    
    # Get Activity Log List
    def GetActivityLogList(self, selectDate: str = "before", beforeDate: str = today, afterDate: str = today, sort: str = "asc", limit: str = 1, offset: str = 0):
        if selectDate == "before":
            url = f"https://api.fitbit.com/1/user/-/activities/list.json?beforeDate={beforeDate}&sort={sort}&limit={limit}&offset={offset}"
        elif selectDate == "after":
            url = f"https://api.fitbit.com/1/user/-/activities/list.json?afterDate={afterDate}&sort={sort}&limit={limit}&offset={offset}"
        headers = super().create_header()
        res = super().request(requests.get, url, headers=headers)

        return json.loads(res.text)
    
#    # Get Activity TCX
#    def ActivityTCX(self, logid: str = ""):
#        url = f"https://api.fitbit.com/1/user/-/activities/{logid}.tcx"
#        headers = super().create_header()
#        res = super().request(requests.get, url, headers=headers)
#
#        return json.loads(res.text)

    # Get Activity Type
    def ActivityType(self, activityid: str = ""):
        url = f"https://api.fitbit.com/1/user/-/activities/{activityid}.json"
        headers = super().create_header()
        res = super().request(requests.get, url, headers=headers)

        return json.loads(res.text)
    
    # Get All Activity Types
    def AllActivityTypes(self):
        url = f"https://api.fitbit.com/1/user/-/activities.json"
        headers = super().create_header()
        res = super().request(requests.get, url, headers=headers)

        return json.loads(res.text)
    
    # Get Daily Activity Summary
    def DailyActivitySummary(self, date: str = today):
        url = f"https://api.fitbit.com/1/user/-/activities/date/{date}.json"
        headers = super().create_header()
        res = super().request(requests.get, url, headers=headers)

        return json.loads(res.text)
    
#    # Get Favorite Activities
#    def FavoriteActivities(self):
#        url = f"https://api.fitbit.com/1/user/-/activities/favorite.json"
#        headers = super().create_header()
#        res = super().request(requests.get, url, headers=headers)
#
#        return json.loads(res.text)

#    # Get Frequent Activities
#    def FrequentActivities(self):
#        url = f"https://api.fitbit.com/1/user/-/activities/frequent.json"
#        headers = super().create_header()
#        res = super().request(requests.get, url, headers=headers)
#
#        return json.loads(res.text)
    
    # Get Lifetime Stats
    def LifetimeStats(self):
        url = f"https://api.fitbit.com/1/user/-/activities.json"
        headers = super().create_header()
        res = super().request(requests.get, url, headers=headers)

        return json.loads(res.text)
    
#    # Get Recent Activity Types
#    def RecentActivityTypes(self):
#        url = f"https://api.fitbit.com/1/user/-/activities/recent.json"
#        headers = super().create_header()
#        res = super().request(requests.get, url, headers=headers)
#
#        return json.loads(res.text)

    # Get Activity Time Series by Date
    def ActivityTimeSeriesByDate(self, resourcepath: str = "activityCalories", date: str = "today", period: str = "1d"):
        url = f"https://api.fitbit.com/1/user/-/activities/{resourcepath}/date/{date}/{period}.json"
        headers = super().create_header()
        res = super().request(requests.get, url, headers=headers)

        return json.loads(res.text)
    
    # Get Activity Time Series by Date Range
    def ActivityTimeSeriesByDateRange(self, resourcepath: str = "activityCalories", startdate: str = "today", enddate: str = "today"):
        url = f"https://api.fitbit.com/1/user/-/activities/{resourcepath}/date/{startdate}/{enddate}.json"
        headers = super().create_header()
        res = super().request(requests.get, url, headers=headers)

        return json.loads(res.text)
    
    # Get Body Goals
    def BodyGoals(self, goaltype: str = "weight"):
        url = f"https://api.fitbit.com/1/user/-/body/log/{goaltype}/goal.json"
        headers = super().create_header()
        res = super().request(requests.get, url, headers=headers)

        return json.loads(res.text)
    
    # Get Body Fat Log
    def BodyFatLog(self, date: str = today):
        url = f"https://api.fitbit.com/1/user/-/body/log/fat/date/{date}.json"
        headers = super().create_header()
        res = super().request(requests.get, url, headers=headers)

        return json.loads(res.text)
    
    # Get Weight Log
    def WeightLog(self, date: str = today):
        url = f"https://api.fitbit.com/1/user/-/body/log/weight/date/{date}.json"
        headers = super().create_header()
        res = super().request(requests.get, url, headers=headers)

        return json.loads(res.text)

    # Get Body Time Series by Date
    def BodyTimeSeriesByDate(self, resource: str = "bmi", date: str = "today", period: str = "1d"):
        url = f"https://api.fitbit.com/1/user/-/body/{resource}/date/{date}/{period}.json"
        headers = super().create_header()
        res = super().request(requests.get, url, headers=headers)

        return json.loads(res.text)

    # Get Body Time Series by Date Range
    def BodyTimeSeriesByDateRange(self, resource: str = "bmi", begindate: str = "today", enddate: str = "today"):
        url = f"https://api.fitbit.com/1/user/-/body/{resource}/date/{begindate}/{enddate}.json"
        headers = super().create_header()
        res = super().request(requests.get, url, headers=headers)

        return json.loads(res.text)
    
    # Get Body Fat Time Series by Date
    def BodyFatTimeSeriesByDate(self, date: str = "today", period: str = "1d"):
        url = f"https://api.fitbit.com/1/user/-/body/log/fat/date/{date}/{period}.json"
        headers = super().create_header()
        res = super().request(requests.get, url, headers=headers)

        return json.loads(res.text)
    
    # Get Body Fat Time Series by Date Range
    def BodyFatTimeSeriesByDateRange(self, startdate: str = "today", enddate: str = "today"):
        url = f"https://api.fitbit.com/1/user/-/body/log/fat/date/{startdate}/{enddate}.json"
        headers = super().create_header()
        res = super().request(requests.get, url, headers=headers)

        return json.loads(res.text)
    
    # Get Weight Time Series by Date
    def WeightTimeSeriesByDate(self, date: str = "today", period: str = "1d"):
        url = f"https://api.fitbit.com/1/user/-/body/log/weight/date/{date}/{period}.json"
        headers = super().create_header()
        res = super().request(requests.get, url, headers=headers)

        return json.loads(res.text)
    
    # Get Weight Time Series by Date Range
    def WeightTimeSeriesByDateRange(self, startdate: str = "today", enddate: str = "today"):
        url = f"https://api.fitbit.com/1/user/-/body/log/weight/date/{startdate}/{enddate}.json"
        headers = super().create_header()
        res = super().request(requests.get, url, headers=headers)

        return json.loads(res.text)

    # Get Breathing Rate Summary by Date
    def BreathingRateSummaryByDate(self, date: str = "today"):
        url = f"https://api.fitbit.com/1/user/-/br/date/{date}.json"
        headers = super().create_header()
        res = super().request(requests.get, url, headers=headers)

        return json.loads(res.text)

    # Get Breathing Rate Summary by Interval
    def BreathingRateSummaryByInterval(self, startdate: str = "today", enddate: str = "today"):
        url = f"https://api.fitbit.com/1/user/-/br/date/{startdate}/{enddate}.json"
        headers = super().create_header()
        res = super().request(requests.get, url, headers=headers)

        return json.loads(res.text)
    
    # Get VO2 Max Summary by Date
    def VO2MaxSummaryByDate(self, date: str = "today"):
        url = f"https://api.fitbit.com/1/user/-/cardioscore/date/{date}.json"
        headers = super().create_header()
        res = super().request(requests.get, url, headers=headers)

        return json.loads(res.text)
    
    # Get VO2 Max Summary by Interval
    def VO2MaxSummaryByInterval(self, startdate: str = "today", enddate: str = "today") :
        url = f"https://api.fitbit.com/1/user/-/cardioscore/date/{startdate}/{enddate}.json"
        headers = super().create_header()
        res = super().request(requests.get, url, headers=headers)

        return json.loads(res.text)
    
#    # Get Alarms
#    def Alarms(self, trackerid: str = "") :
#        url = f"https://api.fitbit.com/1/user/-/devices/tracker/{trackerid}/alarms.json"
#        headers = super().create_header()
#        res = super().request(requests.get, url, headers=headers)
#
#        return json.loads(res.text)
    
#    # Get Devices
#    def Devices(self) :
#        url = f"https://api.fitbit.com/1/user/-/devices.json"
#        headers = super().create_header()
#        res = super().request(requests.get, url, headers=headers)
#
#        return json.loads(res.text)

    # Get ECG Log List
    def ECGLogList(self, selectDate: str = "before", beforeDate: str = today, afterDate: str = today, sort: str = "asc", limit: str = 1, offset: str = 0):
        if selectDate == "before":
            url = f"https://api.fitbit.com/1/user/-/ecg/list.json?beforeDate={beforeDate}&sort={sort}&limit={limit}&offset={offset}"
        elif selectDate == "after":
            url = f"https://api.fitbit.com/1/user/-/ecg/list.json?afterDate={afterDate}&sort={sort}&limit={limit}&offset={offset}"
        headers = super().create_header()
        res = super().request(requests.get, url, headers=headers)

        return json.loads(res.text)

    # Get Friends
    def Friends(self):
        url = f"https://api.fitbit.com/1/user/-/friends.json"
        headers = super().create_header()
        res = super().request(requests.get, url, headers=headers)

        return json.loads(res.text)
    
    # Get Friends Leaderboard
    def FriendsLeaderboard(self):
        url = f"https://api.fitbit.com/1/user/-/leaderboard/friends.json"
        headers = super().create_header()
        res = super().request(requests.get, url, headers=headers)

        return json.loads(res.text)

    # Get Heart Rate Time Series by Date    
    def HeartRateTimeSeriesByDate(self, date: str = "today", period: str = "1d"):
        url = f"https://api.fitbit.com/1/user/-/activities/heart/date/{date}/{period}.json"
        headers = super().create_header()
        res = super().request(requests.get, url, headers=headers)

        return json.loads(res.text)
    
    # Get Heart Rate Time Series by Date Range
    def HeartRateTimeSeriesByDateRange(self, startdate: str = "today", enddate: str = "today"):
        url = f"https://api.fitbit.com/1/user/-/activities/heart/date/{startdate}/{enddate}.json"
        headers = super().create_header()
        res = super().request(requests.get, url, headers=headers)

        return json.loads(res.text)
    
    # Get HRV Summary by Date
    def HRVSummaryByDate(self, date: str = "today"):
        url = f"https://api.fitbit.com/1/user/-/hrv/date/{date}.json"
        headers = super().create_header()
        res = super().request(requests.get, url, headers=headers)

        return json.loads(res.text)
    
    # Get HRV Summary by Interval
    def HRVSummaryByInterval(self, startDate: str = "today", endDate: str = "today"):
        url = f"https://api.fitbit.com/1/user/-/hrv/date/{startDate}/{endDate}.json"
        headers = super().create_header()
        res = super().request(requests.get, url, headers=headers)

        return json.loads(res.text)
    
    # Get AZM Intraday by Date
    def AZMIntradayByDate(self, mode: str = "nomal", date: str = "today", detaillevel: str = "1min", starttime: str = timenow, endtime: str = timenow):
        if mode == "nomal":
            url = f"https://api.fitbit.com/1/user/-/activities/active-zone-minutes/date/{date}/1d/{detaillevel}.json"
        if mode == "selecttime":
            url = f"https://api.fitbit.com/1/user/-/activities/active-zone-minutes/date/{date}/1d/{detaillevel}/time/{starttime}/{endtime}.json"
        headers = super().create_header()
        res = super().request(requests.get, url, headers=headers)

        return json.loads(res.text)
    
    # Get AZM Intraday by Interval
    def AZMIntradayByInterval(self, mode: str = "nomal", startdate: str = "today", enddate: str = "today" , detaillevel: str = "1min", starttime: str = timenow, endtime: str = timenow):
        if mode == "nomal":
            url = f"https://api.fitbit.com/1/user/-/activities/active-zone-minutes/date/{startdate}/{enddate}/{detaillevel}.json"
        if mode == "selecttime":
            url = f"https://api.fitbit.com/1/user/-/activities/active-zone-minutes/date/{startdate}/{enddate}/{detaillevel}/time/{starttime}/{endtime}.json"
        headers = super().create_header()
        res = super().request(requests.get, url, headers=headers)

        return json.loads(res.text)

    # Get Activity Intraday by Date
    def ActivityIntradayByDate(self, mode: str = "nomal", resource: str = "calories", date: str = "today", detaillevel: str = "1min", startdate: str = "today", enddate: str = "today" , starttime: str = timenow, endtime: str = timenow):
        if mode == "nomal":
            url = f"https://api.fitbit.com/1/user/-/activities/{resource}/date/{date}/1d/{detaillevel}.json"
        if mode == "selecttime":
            url = f"https://api.fitbit.com/1/user/-/activities/{resource}/date/{date}/1d/{detaillevel}/time/{starttime}/{endtime}.json"
        headers = super().create_header()
        res = super().request(requests.get, url, headers=headers)

        return json.loads(res.text)
    
    # Get Activity Intraday by Interval
    def ActivityIntradayByInterval(self, mode: str = "nomal", resource: str = "calories", startdate: str = "today", enddate: str = "today", detaillevel: str = "1min", starttime: str = timenow, endtime: str = timenow):
        if mode == "nomal":
            url = f"https://api.fitbit.com/1/user/-/activities/{resource}/date/{startdate}/{enddate}/{detaillevel}.json"
        if mode == "selecttime":
            url = f"https://api.fitbit.com/1/user/-/activities/{resource}/date/{startdate}/{enddate}/{detaillevel}/time/{starttime}/{endtime}.json"
        headers = super().create_header()
        res = super().request(requests.get, url, headers=headers)

        return json.loads(res.text)
    
    # Get Breathing Rate Intraday by Date
    def BreathingRateIntradayByDate(self, date: str = "today"):
        url = f"https://api.fitbit.com/1/user/-/br/date/{date}/all.json"
        headers = super().create_header()
        res = super().request(requests.get, url, headers=headers)

        return json.loads(res.text)
    
    # Get Breathing Rate Intraday by Interval
    def BreathingRateIntradayByInterval(self, startdate: str = "today", enddate: str = "today"):
        url = f"https://api.fitbit.com/1/user/-/br/date/{startdate}/{enddate}/all.json"
        headers = super().create_header()
        res = super().request(requests.get, url, headers=headers)

        return json.loads(res.text)
    
    # Get Heart Rate Intraday by Date
    def HeartRateIntradayByDate(self, mode: str = "nomal", date: str = "today", detaillevel: str = "1sec", starttime: str = timenow, endtime: str = timenow):
        if mode == "nomal":
            url = f"https://api.fitbit.com/1/user/-/activities/heart/date/{date}/1d/{detaillevel}.json"
        elif mode == "selecttime":
            url = f"https://api.fitbit.com/1/user/-/activities/heart/date/{date}/1d/{detaillevel}/time/{starttime}/{endtime}.json"
        headers = super().create_header()
        res = super().request(requests.get, url, headers=headers)

        return json.loads(res.text)
    
    # Get Heart Rate Intraday by Interval
    def HeartRateIntradayByInterval(self, mode: str = "nomal", startdate: str = "today", enddate: str = "today", detaillevel: str = "1sec", starttime: str = timenow, endtime: str = timenow):
        if mode == "nomal":
            url = f"https://api.fitbit.com/1/user/-/activities/heart/date/{startdate}/{enddate}/{detaillevel}.json"
        elif mode == "selecttime":
            url = f"https://api.fitbit.com/1/user/-/activities/heart/date/{startdate}/{enddate}/{detaillevel}/time/{starttime}/{endtime}.json"
        headers = super().create_header()
        res = super().request(requests.get, url, headers=headers)

        return json.loads(res.text)
    
    # Get HRV Intraday by Date
    def HRVIntradayByDate(self, date: str = "today"):
        url = f"https://api.fitbit.com/1/user/-/hrv/date/{date}/all.json"
        headers = super().create_header()
        res = super().request(requests.get, url, headers=headers)

        return json.loads(res.text)
    
    # Get HRV Intraday by Interval
    def HRVIntradayByDate(self, startDate: str = "today", endDate: str = "today"):
        url = f"https://api.fitbit.com/1/user/-/hrv/date/{startDate}/{endDate}/all.json"
        headers = super().create_header()
        res = super().request(requests.get, url, headers=headers)

        return json.loads(res.text)
    
    # Get SpO2 Intraday by Date
    def SpO2IntradayByDate(self, date: str = "today"):
        url = f"https://api.fitbit.com/1/user/-/spo2/date/{date}/all.json"
        headers = super().create_header()
        res = super().request(requests.get, url, headers=headers)

        return json.loads(res.text)
    
    # Get SpO2 Intraday by Interval
    def SpO2IntradayByInterval(self, startdate: str = "today", enddate: str = "today"):
        url = f"https://api.fitbit.com/1/user/-/spo2/date/{startdate}/{enddate}/all.json"
        headers = super().create_header()
        res = super().request(requests.get, url, headers=headers)

        return json.loads(res.text)
    
#    # Get IRN Alerts List
#    def IRNAlertsList(self, selectDate: str = "before", beforeDate: str = today, afterDate: str = today, sort: str = "asc", limit: str = 1, offset: str = 0):
#        if selectDate == "before":
#            url = f"https://api.fitbit.com/1/user/-/irn/alerts/list.json?beforeDate={beforeDate}&sort={sort}&limit={limit}&offset={offset}"
#        elif selectDate == "after":
#            url = f"https://api.fitbit.com/1/user/-/irn/alerts/list.json?afterDate={afterDate}&sort={sort}&limit={limit}&offset={offset}"
#        headers = super().create_header()
#        res = super().request(requests.get, url, headers=headers)
#
#        return json.loads(res.text)

#    # Get IRN Profile
#    def IRNProfile(self):
#        url = f"https://api.fitbit.com/1/user/-/irn/profile.json"
#        headers = super().create_header()
#        res = super().request(requests.get, url, headers=headers)
#
#        return json.loads(res.text)

#    # Get Favorite Foods
#    def FavoriteFoods(self):
#        url = f"https://api.fitbit.com/1/user/-/foods/log/favorite.json"
#        headers = super().create_header()
#        res = super().request(requests.get, url, headers=headers)
#
#        return json.loads(res.text)

#    # Get Food
#    def Food(self, foodid: str = ""):
#        url = f"https://api.fitbit.com/1/user/-/foods/{foodid}.json"
#        headers = super().create_header()
#        res = super().request(requests.get, url, headers=headers)
#
#        return json.loads(res.text)

    # Get Food Goals
    def FoodGoals(self):
        url = f"https://api.fitbit.com/1/user/-/foods/log/goal.json"
        headers = super().create_header()
        res = super().request(requests.get, url, headers=headers)

        return json.loads(res.text)
    
#    # Get Food Locales
#    def FoodLocales(self):
#        url = f"https://api.fitbit.com/1/user/-/foods/locales.json"
#        headers = super().create_header()
#        res = super().request(requests.get, url, headers=headers)
#
#        return json.loads(res.text)

    # Get Food Log
    def FoodLog(self, date: str = "today"):
        url = f"https://api.fitbit.com/1/user/-/foods/log/date/{date}.json"
        headers = super().create_header()
        res = super().request(requests.get, url, headers=headers)

        return json.loads(res.text)
    
#    # Get Food Units
#    def FoodUnits(self):
#        url = f"https://api.fitbit.com/1/user/-/foods/units.json"
#        headers = super().create_header()
#        res = super().request(requests.get, url, headers=headers)
#
#        return json.loads(res.text)

#    # Get Frequent Foods
#    def FrequentFoods(self):
#        url = f"https://api.fitbit.com/1/user/-/foods/log/frequent.json"
#        headers = super().create_header()
#        res = super().request(requests.get, url, headers=headers)
#
#        return json.loads(res.text)

#    # Get Meal
#    def Meal(self, mealid: str = ""):
#        url = f"https://api.fitbit.com/1/user/-/meals/{mealid}.json"
#        headers = super().create_header()
#        res = super().request(requests.get, url, headers=headers)
#
#        return json.loads(res.text)

    # Get Meals
    def Meals(self):
        url = f"https://api.fitbit.com/1/user/-/meals.json"
        headers = super().create_header()
        res = super().request(requests.get, url, headers=headers)

        return json.loads(res.text)
    
#    # Get Recent Foods
#    def RecentFoods(self):
#        url = f"https://api.fitbit.com/1/user/-/foods/log/recent.json"
#        headers = super().create_header()
#        res = super().request(requests.get, url, headers=headers)
#
#        return json.loads(res.text)

    # Get Water Goal
    def WaterGoal(self):
        url = f"https://api.fitbit.com/1/user/-/foods/log/water/goal.json"
        headers = super().create_header()
        res = super().request(requests.get, url, headers=headers)

        return json.loads(res.text)
    
    # Get Water Log
    def WaterLog(self, date: str = "today"):
        url = f"https://api.fitbit.com/1/user/-/foods/log/water/date/{date}.json"
        headers = super().create_header()
        res = super().request(requests.get, url, headers=headers)

        return json.loads(res.text)
    
    # Get Nutrition Time Series by Date
    def NutritionTimeSeriesByDate(self, resource: str = "caloriesIn", date: str = "today", period: str = "1d"):
        url = f"https://api.fitbit.com/1/user/-/foods/log/{resource}/date/{date}/{period}.json"
        headers = super().create_header()
        res = super().request(requests.get, url, headers=headers)

        return json.loads(res.text)
    
    # Get Nutrition Time Series by Date Range
    def NutritionTimeSeriesByDateRange(self, resource: str = "caloriesIn", startdate: str = "today", enddate: str = "today"):
        url = f"https://api.fitbit.com/1/user/-/foods/log/{resource}/date/{startdate}/{enddate}.json"
        headers = super().create_header()
        res = super().request(requests.get, url, headers=headers)

        return json.loads(res.text)
    
    # Get Sleep Goal
    def SleepGoal(self):
        url = f"https://api.fitbit.com/1.2/user/-/sleep/goal.json"
        headers = super().create_header()
        res = super().request(requests.get, url, headers=headers)

        return json.loads(res.text)
    
    # Get Sleep Log by Date
    def SleepLogByDate(self, date: str = today):
        url = f"https://api.fitbit.com/1.2/user/-/sleep/date/{date}.json"
        headers = super().create_header()
        res = super().request(requests.get, url, headers=headers)

        return json.loads(res.text)
    
    # Get Sleep Log by Date Range
    def SleepLogByDateRange(self, startDate: str = today, endDate: str = today):
        url = f"https://api.fitbit.com/1.2/user/-/sleep/date/{startDate}/{endDate}.json"
        headers = super().create_header()
        res = super().request(requests.get, url, headers=headers)

        return json.loads(res.text)
    
    # Get Sleep Log List
    def SleepLogList(self, selectDate: str = "before", beforeDate: str = today, afterDate: str = today, sort: str = "asc", limit: str = 1, offset: str = 0):
        if selectDate == "before":
            url = f"https://api.fitbit.com/1/user/-/sleep/list.json?beforeDate={beforeDate}&sort={sort}&limit={limit}&offset={offset}"
        elif selectDate == "after":
            url = f"https://api.fitbit.com/1/user/-/sleep/list.json?afterDate={afterDate}&sort={sort}&limit={limit}&offset={offset}"
        headers = super().create_header()
        res = super().request(requests.get, url, headers=headers)

        return json.loads(res.text)
    
    # Get SpO2 Summary by Date
    def SpO2SummaryByDate(self, date: str = "today"):
        url = f"https://api.fitbit.com/1/user/-/spo2/date/{date}.json"
        headers = super().create_header()
        res = super().request(requests.get, url, headers=headers)

        return json.loads(res.text)
    
    # Get SpO2 Summary by Interval
    def SpO2SummaryByInterval(self, startdate: str = "today", enddate: str = "today"):
        url = f"https://api.fitbit.com/1/user/-/spo2/date/{startdate}/{enddate}.json"
        headers = super().create_header()
        res = super().request(requests.get, url, headers=headers)

        return json.loads(res.text)
    
    # Get Subscription List
    def SubscriptionList(self, collectionpath: str = ""):
        url = f"https://api.fitbit.com/1/user/-/{collectionpath}/apiSubscriptions.json"
        headers = super().create_header()
        res = super().request(requests.get, url, headers=headers)

        return json.loads(res.text)
    
    # Get Temperature (Core) Summary by Date
    def TemperatureCoreSummaryByDate(self, date: str = "today"):
        url = f"https://api.fitbit.com/1/user/-/temp/core/date/{date}.json"
        headers = super().create_header()
        res = super().request(requests.get, url, headers=headers)

        return json.loads(res.text)
    
    # Get Temperature (Core) Summary by Interval
    def TemperatureCoreSummaryByInterval(self, startdate: str = "today", enddate: str = "today"):
        url = f"https://api.fitbit.com/1/user/-/temp/core/date/{startdate}/{enddate}.json"
        headers = super().create_header()
        res = super().request(requests.get, url, headers=headers)

        return json.loads(res.text)
    
    # Get Temperature (Skin) Summary by Date
    def TemperatureSkinSummaryByDate(self, date: str = "today"):
        url = f"https://api.fitbit.com/1/user/-/temp/skin/date/{date}.json"
        headers = super().create_header()
        res = super().request(requests.get, url, headers=headers)

        return json.loads(res.text)
    
    # Get Temperature (Skin) Summary by Interval
    def TemperatureSkinSummaryByInterval(self, startdate: str = "today", enddate: str = "today"):
        url = f"https://api.fitbit.com/1/user/-/temp/skin/date/{startdate}/{enddate}.json"
        headers = super().create_header()
        res = super().request(requests.get, url, headers=headers)

        return json.loads(res.text)
    
    # Get Badges
    def Badges(self):
        url = f"https://api.fitbit.com/1/user/-/badges.json"
        headers = super().create_header()
        res = super().request(requests.get, url, headers=headers)

        return json.loads(res.text)
    
    # Get Profile
    def Profile(self):
        url = f"https://api.fitbit.com/1/user/-/profile.json"
        headers = super().create_header()
        res = super().request(requests.get, url, headers=headers)

        return json.loads(res.text)
