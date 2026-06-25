import pytest

@pytest.fixture(autouse=True)
def disable_throttling(settings):
    settings.REST_FRAMEWORK['DEFAULT_THROTTLE_CLASSES'] = []
    settings.REST_FRAMEWORK['DEFAULT_THROTTLE_RATES'] = {
        'login': '10000/day',
        'register': '10000/day',
        'resend_verification': '10000/day',
    }
