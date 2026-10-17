from pydantic import SecretStr

from echovault.config import Settings


def test_settings_defaults() -> None:
    settings = Settings(app_env="development")
    assert settings.app_name == "EchoVault"
    assert settings.app_version == "0.1.0"
    assert settings.is_development is True
    assert settings.is_testing is False
    assert settings.is_production is False


def test_settings_environment_flags() -> None:
    test_settings = Settings(app_env="testing")
    assert test_settings.is_testing is True
    assert test_settings.is_development is False
    assert test_settings.is_production is False

    prod_settings = Settings(app_env="production")
    assert prod_settings.is_production is True
    assert prod_settings.is_development is False
    assert prod_settings.is_testing is False


def test_secrets_masked_in_repr_and_str() -> None:
    secret_val = "super-secret-service-role-key-987"
    settings = Settings(
        supabase_service_role_key=SecretStr(secret_val),
        supabase_jwt_secret=SecretStr("super-secret-jwt"),
        llm_api_key=SecretStr("super-secret-llm"),
    )

    # Raw value is retrievable via .get_secret_value()
    assert settings.supabase_service_role_key.get_secret_value() == secret_val

    # String representations must mask the secret
    assert secret_val not in str(settings)
    assert secret_val not in repr(settings)
    assert "super-secret-jwt" not in repr(settings)
    assert "super-secret-llm" not in repr(settings)
