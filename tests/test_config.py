def test_get_config():
    from core.config import get_settings

    settings = get_settings()

    assert settings.DATASOURCE_HOST is not None
    assert settings.DATASOURCE_PORT is not None
    assert settings.DATASOURCE_USERNAME is not None
    assert settings.DATASOURCE_PASSWORD is not None
    assert settings.CATALOG_DB_NAME is not None
    assert settings.USER_DB_NAME is not None
    assert settings.INSIGHT_DB_NAME is not None