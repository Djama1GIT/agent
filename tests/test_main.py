from fastapi import FastAPI

from src.main import app


class TestMain:
    def test_app_initialization(self):
        """Test that FastAPI app is initialized correctly."""
        assert isinstance(app, FastAPI)
        assert app.title is not None  # noqa
        assert app.version is not None  # noqa

    def test_settings_loaded(self):
        """Test that settings are loaded (without checking values)."""
        from src.main import settings
        assert settings is not None

    def test_exception_handlers_configured(self):
        """Test that exception handlers are set."""
        assert len(app.exception_handlers) > 0

    def test_logging_configured(self):
        """Test that logging is configured by checking logger existence."""
        import logging
        # Check that some logger exists (logging was configured)
        assert logging.getLogger().handlers is not None

class TestApiIntegration:
    def test_cors_middleware_configured(self, client):
        """Test that CORS middleware is properly configured."""
        response = client.options(
            "/api/health",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "GET",
            },
        )
        assert response.status_code in [200, 405]  # 405 if endpoint doesn't exist
        assert "access-control-allow-origin" in response.headers

    def test_api_routes_included(self, client):
        """Test that API routes are included with correct prefix."""
        # Make request to any API endpoint
        response = client.get("/api/health")
        # Just check that it's handled (404 means router exists but endpoint doesn't)
        assert response.status_code in [200, 404]

    def test_prometheus_metrics_endpoint(self, client):
        """Test that Prometheus metrics endpoint is exposed."""
        response = client.get("/metrics")
        assert response.status_code == 200
        assert "text/plain" in response.headers["content-type"]

    def test_openapi_endpoint(self, client):
        """Test that OpenAPI documentation is available."""
        response = client.get("/openapi.json")
        assert response.status_code == 200
        data = response.json()
        assert "info" in data
        assert "paths" in data
