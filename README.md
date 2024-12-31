# fitbitApp
fitbit WEB API wrapper
## Preparation
### Creating a Fitbit Application
1. Access the developer page. (See reference URL)
    - If you don't have a FitBit account, create one first!
1. Application Creation
    - Create it by entering the required information from the developer page “REGISTER AN APP”. If you just want to get your own data, you can do the following.
        - Application Name ... Enter an appropriate name
        - Description ... Enter an appropriate description
        - Application Website URL ... http://localhost
        - Organization ... none
        - Organization Website URL ... http://localhost
        - Terms of Service URL ... http://localhost
        - Privacy Policy URL ... http://localhost
        - OAuth 2.0 Application Type ... Personal
        - Redirect URL ... http://localhost:8000
        - Default Access Type ... Read Only
### Obtaining an access token
1. access the Fitbit OAuth 2.0 Tutorial page
    - On the “MANAGE MY APPS” tab of the developer page, click the application you created in the Create Application section and click the OAuth 2.0 Tutorial link. 1.
Enter the following in the App Settings
    1. Client ID
        - OAuth 2.0 Client ID for the application you created. 
    1. Application Type
        - Select Client.
1. Enter the following in Getting an Access Token
    1. Step 1: Generate PKCE and State Values
        - Click GENERATE for PKCE Code Verifie
        - Click on GENERATE in State
1. Step 2: Display Authorization Page
    1. Click the URL of Authorization URL
        - On the Authorization page, select “Allow all” and click “Allow“
        - Depending on your browser, you may see “localhost connection denied. but leave it as it is to be used in the next step.
1. Step 3: Handle the Redirect
    1. in the Authorization Code, enter “localhost connection denied” as the URL of the page << Enter the value of the http://localhost:8000/?code=<here>&state=~ code= part of the URL of the page “localhost connection denied” in the Authorization Code field.
    1. In the State field, enter the value of “localhost connection denied. Enter the value of the http://localhost:8000/?code=~&state=<here> state= part of the URL on the page
1. Step 4: Get Tokens
    1. Click SUBMIT REQUEST.
        - The response should show the tokens without any errors.
        - Save the Response to a text file named Token.json (or whatever file name you want)
1. Access User Data
    1. Click SUBMIT REQUEST
        - Response should show your profile data with no errors.
### Create Config file
Create a file named Config.json with the following contents
```json:Config.json
{
    "CLIENT_ID":"Your OAuth 2.0 Client ID for the created application",
    "CLIENT_SECRET":"Your Client Secret for the created application"
}
```

## Let's use it
Uncomment out if necessary
```Python:TestFitbit.py
import json
import fitbitApp
import os

curdir = os.path.dirname(__file__) + "/"

config_json = open("{}Config.json".format(curdir), "r")
token_json = open("{}Token.json".format(curdir), "r")
CONFIG = json.load(config_json)
TOKEN = json.load(token_json)

access_token = TOKEN["access_token"]
refresh_token = TOKEN["refresh_token"]
client_id = CONFIG["CLIENT_ID"]

app = fitbitApp.app(access_token, refresh_token, client_id, curdir)

# Get AZM Time Series by Date
# print(app.AZMTimeSeriesByDate()) # date = yyyy-MM-dd or today , period = 1d or 7d or 30d or 1w or 1m or 3m or 6m or 1y

# Get AZM Time Series by Interval
# print(app.AZMTimeSeriesByInterval()) # startdate = yyyy-MM-dd or today , enddate = yyyy-MM-dd or today

# Get Activity Goals
# print(app.ActivityGoals()) # period = daily or weekly

# Get Activity Log List
# print(app.GetActivityLogList()) # selectDate = "before" or "after", (beforeDate = "yyyy-MM-ddTHH:mm:ss" or "yyyy-MM-dd", afterDate = "yyyy-MM-ddTHH:mm:ss" or "yyyy-MM-dd"), sort = "asc" or "desc", limit: str = 1 to 100

# Get Activity Type
# print(app.ActivityType()) # activityid = Get Activity Log List of logId

# Get All Activity Types
# print(app.AllActivityTypes())

# Get Daily Activity Summary
# print(app.DailyActivitySummary()) # date = yyyy-MM-dd

# Get Lifetime Stats
# print(app.LifetimeStats())

# Get Activity Time Series by Date
## resourcepath :
## activityCalories , calories , caloriesBMR , distance , elevation , floors , minutesSedentary , minutesLightlyActive ,
## minutesFairlyActive , minutesVeryActive , steps , swimming-strokes , tracker/activityCalories , tracker/calories ,
## tracker/distance , tracker/elevation , tracker/floors , tracker/minutesSedentary , tracker/minutesLightlyActive ,
## tracker/minutesFairlyActive , tracker/minutesVeryActive , tracker/steps
# print(app.ActivityTimeSeriesByDate()) # resourcepath = , date = yyyy-MM-dd or today , 1d or 7d or 30d or 1w or 1m or 3m or 6m or 1y

# Get Activity Time Series by Date Range
## resourcepath :
## activityCalories , calories , caloriesBMR , distance , elevation , floors , minutesSedentary , minutesLightlyActive ,
## minutesFairlyActive , minutesVeryActive , steps , swimming-strokes , tracker/activityCalories , tracker/calories ,
## tracker/distance , tracker/elevation , tracker/floors , tracker/minutesSedentary , tracker/minutesLightlyActive ,
## tracker/minutesFairlyActive , tracker/minutesVeryActive , tracker/steps
# print(app.ActivityTimeSeriesByDateRange()) # resourcepath = , startdate = yyyy-MM-dd or today , enddate = yyyy-MM-dd or today

# Get Body Goals
# print(app.BodyGoals()) # goaltype = weight or fat

# Get Body Fat Log
# print(app.BodyFatLog()) # date = yyyy-MM-dd

# Get Weight Log
# print(app.WeightLog())

# Get Body Time Series by Date
# print(app.BodyTimeSeriesByDate()) # resource = "bmi" or "fat" or "weight" , date = "yyyy-MM-dd" or "today" , period = "1d" or "7d" or "30d" or "1w" or "1m" or "3m" or "6m" or "1y" or "max"

# Get Body Time Series by Date Range
# print(app.BodyTimeSeriesByDateRange()) # resource = "bmi" or "fat" or "weight" , begindate = "yyyy-MM-dd" or "today" , enddate = "yyyy-MM-dd" or "today"

# Get Body Fat Time Series by Date
# print(app.BodyFatTimeSeriesByDate()) # date = "yyyy-MM-dd" or "today" , period = "1d" or "7d" or "30d" or "1w" or "1m"

# Get Body Fat Time Series by Date Range
# print(app.BodyFatTimeSeriesByDateRange()) # startdate = "yyyy-MM-dd" or "today" , enddate = "yyyy-MM-dd" or "today"

# Get Weight Time Series by Date
# print(app.WeightTimeSeriesByDate()) # date = "yyyy-MM-dd" or "today" , period = "1d" or "7d" or "30d" or "1w" or "1m"

# Get Weight Time Series by Date Range
# print(app.WeightTimeSeriesByDateRange()) # startdate = "yyyy-MM-dd" or "today" , enddate = "yyyy-MM-dd" or "today"

# Get Breathing Rate Summary by Date
# print(app.BreathingRateSummaryByDate()) # date = "yyyy-MM-dd" or "today"

# Get Breathing Rate Summary by Interval
# print(app.BreathingRateSummaryByInterval()) # startdate = "yyyy-MM-dd" or "today" , enddate = "yyyy-MM-dd" or "today"

# Get VO2 Max Summary by Date
# print(app.VO2MaxSummaryByDate()) # date = "yyyy-MM-dd" or "today"

# Get VO2 Max Summary by Interval
# print(app.VO2MaxSummaryByInterval()) # startdate = "yyyy-MM-dd" or "today" , enddate = "yyyy-MM-dd" or "today"

# Get ECG Log List
# print(app.ECGLogList()) # selectDate = "before" or "after", (beforeDate = "yyyy-MM-ddTHH:mm:ss" or "yyyy-MM-dd", afterDate = "yyyy-MM-ddTHH:mm:ss" or "yyyy-MM-dd"), sort = "asc" or "desc", limit: str = 1 to 100

# Get Friends
# print(app.Friends())

# Get Friends Leaderboard
# print(app.FriendsLeaderboard())

# Get Heart Rate Time Series by Date
# print(app.HeartRateTimeSeriesByDate()) # date = "yyyy-MM-dd" or "today" , period = "1d" or "7d" or "30d" or "1w" or "1m"

# Get Heart Rate Time Series by Date Range
# print(app.HeartRateTimeSeriesByDateRange()) # startdate = "yyyy-MM-dd" or "today" , enddate = "yyyy-MM-dd" or "today"

# Get HRV Summary by Date
# print(app.HRVSummaryByDate()) # date = "yyyy-MM-dd" or "today"

# Get HRV Summary by Interval
# print(app.HRVSummaryByInterval()) # startDate = "yyyy-MM-dd" or "today", endDate = "yyyy-MM-dd" or "today"

# Get AZM Intraday by Date
# print(app.AZMIntradayByDate()) # mode = "nomal" or "selecttime", date = "yyyy-MM-dd" or "today" , detaillevel = "1min" or "5min" or "15min" , (starttime = "HH:mm" , endtime = "HH:mm")

# Get AZM Intraday by Interval
# print(app.AZMIntradayByInterval()) # mode = "nomal" or "selecttime", startdate = "yyyy-MM-dd" or "today" ,enddate = "yyyy-MM-dd" or "today" ,detaillevel = "1min" or "5min" or "15min" , (starttime = "HH:mm" , endtime = "HH:mm")

# Get Activity Intraday by Date
# print(app.ActivityIntradayByDate()) # mode = "nomal" or "selecttime", resource = "calories" or "distance" or "elevation" or "floors" or "steps" or "swimming-strokes" , date = "yyyy-MM-dd" or "today" , detaillevel = "1min" or "5min" or "15min" , (starttime = "HH:mm" , endtime = "HH:mm")

# Get Activity Intraday by Interval
# print(app.ActivityIntradayByInterval()) # mode = "nomal" or "selecttime", resource = "calories" or "distance" or "elevation" or "floors" or "steps" or "swimming-strokes" , startdate = "yyyy-MM-dd" or "today" , enddate = "yyyy-MM-dd" or "today" , detaillevel = "1min" or "5min" or "15min" , (starttime = "HH:mm" , endtime = "HH:mm")

# Get Breathing Rate Intraday by Date
# print(app.BreathingRateIntradayByDate()) # date = "yyyy-MM-dd" or "today"

# Get Breathing Rate Intraday by Interval
# print(app.BreathingRateIntradayByInterval()) # startdate = "yyyy-MM-dd" or "today" , enddate = "yyyy-MM-dd" or "today"

# Get Heart Rate Intraday by Date
# print(app.HeartRateIntradayByDate()) # mode = "nomal" or "selecttime" , date = "yyyy-MM-dd" or "today" , detaillevel = "1sec" or "1min" or "5min" or "15min" , (starttime = "HH:mm" , endtime = "HH:mm")

# Get Heart Rate Intraday by Interval
# print(app.HeartRateIntradayByInterval()) # mode = "nomal" or "selecttime" , startdate = "yyyy-MM-dd" or "today" , enddate = "yyyy-MM-dd" or "today" , detaillevel = "1sec" or "1min" or "5min" or "15min" , (starttime = "HH:mm" , endtime = "HH:mm")

# Get HRV Intraday by Date
# print(app.HRVIntradayByDate()) # date = "yyyy-MM-dd" or "today"

# Get HRV Intraday by Interval
# print(app.HRVIntradayByDate()) # startDate = "yyyy-MM-dd" or "today" , endDate = "yyyy-MM-dd" or "today"

# Get SpO2 Intraday by Date
# print(app.SpO2IntradayByDate()) # date = "yyyy-MM-dd" or "today"

# Get SpO2 Intraday by Interval
# print(app.SpO2IntradayByInterval()) # startdate = "yyyy-MM-dd" or "today" , enddate = "yyyy-MM-dd" or "today"

# Get Food Goals
# print(app.FoodGoals())

# Get Food Log
# print(app.FoodLog()) # date = "yyyy-MM-dd" or "today"

# Get Meals
# print(app.Meals())

# Get Water Goal
# print(app.WaterGoal())

# Get Water Log
# print(app.WaterLog()) # date = "yyyy-MM-dd" or "today"

# Get Nutrition Time Series by Date
# print(app.NutritionTimeSeriesByDate()) # resource = "caloriesIn" or "water" , date = "yyyy-MM-dd" or "today" , period: str = "1d" or "7d" or "30d" or "1w" or "1m" or "3m" or "6m" or "1y"

# Get Nutrition Time Series by Date Range
# print(app.NutritionTimeSeriesByDateRange()) # resource = "caloriesIn" or "water" , startdate = "yyyy-MM-dd" or "today" , enddate = "yyyy-MM-dd" or "today"

# Get Sleep Goal
# print(app.SleepGoal())

# Get Sleep Log by Date
# print(app.SleepLogByDate()) # date = "yyyy-MM-dd"

# Get Sleep Log by Date Range
# print(app.SleepLogByDateRange()) # startDate = "yyyy-MM-dd" , endDate = "yyyy-MM-dd"

# Get Sleep Log List
# print(app.SleepLogList()) # selectDate = "before" or "after", (beforeDate = "yyyy-MM-ddTHH:mm:ss", afterDate = "yyyy-MM-ddTHH:mm:ss", sort = "asc" or "desc", limit = "1" to "100"

# Get SpO2 Summary by Date
# print(app.SpO2SummaryByDate()) # date = "yyyy-MM-dd" or "today"

# Get SpO2 Summary by Interval
# print(app.SpO2SummaryByInterval()) # startdate = "yyyy-MM-dd" or "today" , enddate = "yyyy-MM-dd" or "today"

# Get Subscription List
# print(app.SubscriptionList()) # collectionpath = "activities" or "body" or "foods" or "sleep" or "userRevokedAccess"

# Get Temperature (Core) Summary by Date
# print(app.TemperatureCoreSummaryByDate()) # date = "yyyy-MM-dd" or "today"

# Get Temperature (Core) Summary by Interval
# print(app.TemperatureCoreSummaryByInterval()) # startdate = "yyyy-MM-dd" or "today" , enddate = "yyyy-MM-dd" or "today"

# Get Temperature (Skin) Summary by Date
# print(app.TemperatureSkinSummaryByDate()) # date = "yyyy-MM-dd" or "today"

# Get Temperature (Skin) Summary by Interval
# print(app.TemperatureSkinSummaryByInterval()) # startdate = "yyyy-MM-dd" or "today" , enddate = "yyyy-MM-dd" or "today"

# Get Badges
# print(app.Badges())

# Get Profile
# print(app.Profile())
```

## Reference URL
- Developer Page https://dev.fitbit.com/apps
- Reference https://dev.fitbit.com/build/reference/web-api/
