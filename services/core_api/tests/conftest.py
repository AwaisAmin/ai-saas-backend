import pytest
from django.test import override_settings

@pytest.fixture(autouse=True)
def disable_throttling(settings):
    settings.REST_FRAMEWORK['DEFAULT_THROTTLE_CLASSES'] = []
    settings.REST_FRAMEWORK['DEFAULT_THROTTLE_RATES'] = {}
