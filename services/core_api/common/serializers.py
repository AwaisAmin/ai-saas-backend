from rest_framework import serializers

def validate_text_field(value: str, label: str, min_length: int = 2) -> str:
    value = value.strip()
    if len(value) < min_length:
        raise serializers.ValidationError(
            f"{label} must be at least {min_length} characters"
        )
    return value
