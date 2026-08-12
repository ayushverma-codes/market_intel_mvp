from app.config.settings import Settings, get_settings


def test_default_settings_load_without_env_file():
    s = Settings(_env_file=None)  # ignore any local .env during this test
    assert s.llm_provider == "nvidia_nim"
    assert s.nvidia_nim_base_url == "https://integrate.api.nvidia.com/v1"
    assert s.confidence_high_threshold > s.confidence_medium_threshold


def test_get_settings_is_cached():
    assert get_settings() is get_settings()


def test_rss_feed_url_list_parses_csv():
    s = Settings(_env_file=None, rss_feed_urls="https://a.com/rss, https://b.com/rss")
    assert s.rss_feed_url_list == ["https://a.com/rss", "https://b.com/rss"]


def test_local_env_does_not_require_nim_key():
    # app_env defaults to "local", so missing API key should not raise.
    Settings(_env_file=None, app_env="local", nvidia_nim_api_key=None)
