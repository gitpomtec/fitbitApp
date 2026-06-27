import datetime

from conftest import assert_no_error


def test_sleep_log_yesterday(app):
    yesterday = (datetime.date.today() - datetime.timedelta(days=1)).strftime("%Y-%m-%d")
    res = app.SleepLogByDate(date=yesterday)
    assert_no_error(res)
    assert "dataPoints" in res or res == {}

    if res.get("dataPoints"):
        point = res["dataPoints"][0]
        assert "sleep" in point
        assert "interval" in point["sleep"]
        assert "summary" in point["sleep"]
