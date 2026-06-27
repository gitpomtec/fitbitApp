from conftest import assert_no_error


def test_get_identity(app):
    res = app.get_identity()
    assert_no_error(res)
    assert "legacyUserId" in res
    assert "healthUserId" in res


def test_get_profile(app):
    res = app.get_profile()
    assert_no_error(res)
    assert "name" in res


def test_get_settings(app):
    res = app.get_settings()
    assert_no_error(res)
