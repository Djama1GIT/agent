from types import GeneratorType
from typing import Generator

import pytest

from src.dependencies.agent import get_agent
from src.schemas.agent import AgentConfig
from src.services.agent import Agent


class TestGetAgent:
    """Тесты для зависимости get_agent"""

    def test_get_agent_returns_callable(self, mock_get_settings):
        """Проверяет, что get_agent возвращает вызываемый объект"""
        dependency = get_agent(mock_get_settings)

        assert callable(dependency)

    def test_dependency_returns_generator(self, mock_get_settings, mock_settings):
        """Проверяет, что зависимость возвращает генератор"""
        dependency = get_agent(mock_get_settings)

        result = dependency(mock_settings)

        assert isinstance(result, GeneratorType)

    def test_agent_created_with_real_settings(self, mock_get_settings, mock_settings):
        """
        Проверяет, что Agent создаётся с реальным Settings.
        """
        dependency = get_agent(mock_get_settings)

        generator = dependency(mock_settings)
        agent = next(generator)

        # Тип
        assert isinstance(agent, Agent)

        # Конфигурация
        config = agent.config

        assert isinstance(config, AgentConfig)

        assert config.model == "test-model"
        assert config.settings is mock_settings
        assert config.web_search is False

        generator.close()

    def test_generator_yields_only_once(self, mock_get_settings, mock_settings):
        """Проверяет, что генератор возвращает только одно значение"""
        dependency = get_agent(mock_get_settings)

        gen = dependency(mock_settings)

        first = next(gen)

        assert isinstance(first, Agent)

        with pytest.raises(StopIteration):
            next(gen)

    def test_each_call_creates_new_agent(self, mock_get_settings, mock_settings):
        """Проверяет, что каждый вызов создаёт нового агента"""
        dependency = get_agent(mock_get_settings)

        gen1 = dependency(mock_settings)
        gen2 = dependency(mock_settings)

        agent1 = next(gen1)
        agent2 = next(gen2)

        assert agent1 is not agent2

        gen1.close()
        gen2.close()

    def test_dependency_return_type_hint(self, mock_get_settings, mock_settings):
        """Проверяет соответствие типу Generator"""
        dependency = get_agent(mock_get_settings)

        result = dependency(mock_settings)

        assert isinstance(result, Generator)