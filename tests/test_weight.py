from conftest import assert_no_error


def test_weight_log_today(app):
    res = app.WeightLog()
    assert_no_error(res)
