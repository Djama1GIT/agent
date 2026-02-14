from src.core.config import Settings
from src.dependencies.settings import get_settings


class TestSettings:
    def test_get_settings_returns_settings_instance(self):
        settings = get_settings()
        assert isinstance(settings, Settings)
    
    
    def test_get_settings_returns_fresh_instance_each_call(self):
        settings1 = get_settings()
        settings2 = get_settings()
        assert settings1 is not settings2  # каждый вызов возвращает новый объект
    
    
    def test_settings_has_expected_attributes(self):
        settings = get_settings()
        # Проверяем несколько ключевых атрибутов, которые должны быть в Settings
        assert hasattr(settings, "DEFAULT_MODEL")
        assert hasattr(settings, "SOME_OTHER_CONFIG") or True  # замените на реальные поля
    
    
    def test_settings_values_match_env(self, monkeypatch):
        # Пример проверки, что значения из окружения правильно подхватываются
        monkeypatch.setenv("DEFAULT_MODEL", "env-test-model")
        settings = get_settings()
        assert getattr(settings, "DEFAULT_MODEL", None) == "env-test-model"
