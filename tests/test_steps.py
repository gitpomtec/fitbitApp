from conftest import assert_no_error


def test_steps_today(app):
    res = app.Steps()
    assert_no_error(res)
    assert "rollupDataPoints" in res or res == {}
