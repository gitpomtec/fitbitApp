from conftest import assert_no_error


def test_heart_rate_intraday_today(app):
    res = app.HeartRateIntradayByDate()
    assert_no_error(res)
    assert "dataPoints" in res or res == {}

    if res.get("dataPoints"):
        point = res["dataPoints"][0]
        assert "dataSource" in point
        assert "heartRate" in point
        assert "beatsPerMinute" in point["heartRate"]
