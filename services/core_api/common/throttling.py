from rest_framework.throttling import AnonRateThrottle

class LoginThrottle(AnonRateThrottle):
    scope = 'login'

class RegisterThrottle(AnonRateThrottle):
    scope = 'register'

class ResendVerificationThrottle(AnonRateThrottle):
    scope = 'resend_verification'
