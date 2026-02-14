import pytest
from fastapi import status, Request
from fastapi.responses import JSONResponse
from pydantic import ValidationError
import json

from src.core.errors import CustomError
from src.core.errors.handlers import (
    exception_handler,
    validation_exception_handler,
    custom_error_handler,
    exception_handlers,
)


@pytest.fixture
def decoded_response():
    """Helper fixture to decode JSONResponse body."""

    def _decode_response(response: JSONResponse) -> dict:
        # response.body returns bytes, decode to string then parse JSON
        return json.loads(response.body.decode())

    return _decode_response


class TestExceptionHandler:
    """Tests for the base exception handler."""

    @pytest.mark.asyncio
    async def test_exception_handler_returns_500_response(self, mock_request):
        """Test that exception handler returns 500 status code."""
        exc = Exception("Test exception")

        response = await exception_handler(mock_request, exc)

        assert isinstance(response, JSONResponse)
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR

    @pytest.mark.asyncio
    async def test_exception_handler_returns_internal_server_error_message(self, mock_request, decoded_response):
        """Test that exception handler returns 'Internal Server Error' message."""
        exc = Exception("Test exception")

        response = await exception_handler(mock_request, exc)
        content = decoded_response(response)

        assert "detail" in content
        assert content["detail"] == "Internal Server Error"

    @pytest.mark.asyncio
    async def test_exception_handler_does_not_return_exception_details(self, mock_request, decoded_response):
        """Test that exception handler does not expose internal exception details."""
        exc = Exception("Sensitive internal error")

        response = await exception_handler(mock_request, exc)
        content = decoded_response(response)

        assert "Sensitive internal error" not in str(content)
        assert content["detail"] == "Internal Server Error"

    @pytest.mark.asyncio
    async def test_exception_handler_with_different_exception_types(self, mock_request, decoded_response):
        """Test that exception handler works with any exception type."""
        test_exceptions = [
            Exception("Test"),
            ValueError("Value error"),
            KeyError("Key error"),
            TypeError("Type error"),
            RuntimeError("Runtime error")
        ]

        for exc in test_exceptions:
            response = await exception_handler(mock_request, exc)
            content = decoded_response(response)
            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
            assert content["detail"] == "Internal Server Error"


class TestValidationExceptionHandler:
    """Tests for the Pydantic validation exception handler."""

    @pytest.mark.asyncio
    async def test_validation_handler_returns_422_response(self, mock_request):
        """Test that validation handler returns 422 status code."""
        # Create a simple validation error
        error_line = ValidationError.from_exception_data("Test validation error", [])

        response = await validation_exception_handler(mock_request, error_line)

        assert isinstance(response, JSONResponse)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    @pytest.mark.asyncio
    async def test_validation_handler_returns_error_details(self, mock_request, decoded_response):
        """Test that validation handler returns validation error details."""
        # Create a validation error with specific details
        try:
            from pydantic import BaseModel

            class TestModel(BaseModel):
                name: str
                age: int

            TestModel(name=123, age="invalid")
        except ValidationError as exc:
            response = await validation_exception_handler(mock_request, exc)
            content = decoded_response(response)

            assert "detail" in content
            assert isinstance(content["detail"], list)
            assert len(content["detail"]) > 0

            # Check that error details are present
            error_detail = content["detail"][0]
            assert "type" in error_detail
            assert "loc" in error_detail
            assert "msg" in error_detail
            assert "input" in error_detail

    @pytest.mark.asyncio
    async def test_validation_handler_with_multiple_errors(self, mock_request, decoded_response):
        """Test validation handler with multiple validation errors."""
        try:
            from pydantic import BaseModel, field_validator

            class TestModel(BaseModel):
                name: str
                age: int

                @field_validator('age')
                def validate_age(cls, v):
                    if v < 0:
                        raise ValueError('Age must be positive')
                    if v > 150:
                        raise ValueError('Age must be less than 150')
                    return v

            TestModel(name=123, age=200)
        except ValidationError as exc:
            response = await validation_exception_handler(mock_request, exc)
            content = decoded_response(response)

            assert len(content["detail"]) >= 2  # Should have at least 2 errors

    @pytest.mark.asyncio
    async def test_validation_handler_response_is_json_encodable(self, mock_request, decoded_response):
        """Test that validation handler response can be JSON encoded."""
        try:
            from pydantic import BaseModel

            class TestModel(BaseModel):
                name: str
                age: int

            TestModel(name=123, age="invalid")
        except ValidationError as exc:
            response = await validation_exception_handler(mock_request, exc)
            content = decoded_response(response)

            # Should not raise an exception
            json_str = json.dumps(content)
            assert isinstance(json_str, str)


class TestCustomErrorHandler:
    """Tests for the custom error handler."""

    @pytest.mark.asyncio
    async def test_custom_error_handler_returns_500_response(self, mock_request):
        """Test that custom error handler returns 500 status code."""
        exc = CustomError("Test custom error")

        response = await custom_error_handler(mock_request, exc)

        assert isinstance(response, JSONResponse)
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR

    @pytest.mark.asyncio
    async def test_custom_error_handler_returns_error_message(self, mock_request, decoded_response):
        """Test that custom error handler returns the error message."""
        error_message = "Custom error occurred"
        exc = CustomError(error_message)

        response = await custom_error_handler(mock_request, exc)
        content = decoded_response(response)

        assert "detail" in content
        assert content["detail"] == error_message

    @pytest.mark.asyncio
    async def test_custom_error_handler_with_different_messages(self, mock_request, decoded_response):
        """Test custom error handler with different error messages."""
        test_messages = [
            "Error 1",
            "Database connection failed",
            "Invalid operation",
            "Permission denied",
            "Resource not found"
        ]

        for message in test_messages:
            exc = CustomError(message)
            response = await custom_error_handler(mock_request, exc)
            content = decoded_response(response)
            assert content["detail"] == message

    @pytest.mark.asyncio
    async def test_custom_error_handler_with_empty_message(self, mock_request, decoded_response):
        """Test custom error handler with empty message."""
        exc = CustomError("")

        response = await custom_error_handler(mock_request, exc)
        content = decoded_response(response)

        assert content["detail"] == ""

    @pytest.mark.asyncio
    async def test_custom_error_handler_with_special_characters(self, mock_request, decoded_response):
        """Test custom error handler with special characters in message."""
        special_message = "Error: <>&'\"\\n\\t"
        exc = CustomError(special_message)

        response = await custom_error_handler(mock_request, exc)
        content = decoded_response(response)

        assert content["detail"] == special_message


class TestExceptionHandlersDict:
    """Tests for the exception_handlers dictionary."""

    def test_exception_handlers_contains_all_handlers(self):
        """Test that exception_handlers dict contains all expected handlers."""
        assert Exception in exception_handlers
        assert ValidationError in exception_handlers
        assert CustomError in exception_handlers

    def test_exception_handlers_maps_to_correct_functions(self):
        """Test that exception_handlers maps exceptions to correct handler functions."""
        assert exception_handlers[Exception] == exception_handler
        assert exception_handlers[ValidationError] == validation_exception_handler
        assert exception_handlers[CustomError] == custom_error_handler

    @pytest.mark.asyncio
    async def test_exception_handlers_can_be_used_with_fastapi(self, mock_request, decoded_response):
        """Test that handlers work when called through the dictionary."""
        # Test Exception handler
        exc = Exception("Test")
        response = await exception_handlers[Exception](mock_request, exc)
        content = decoded_response(response)
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert content["detail"] == "Internal Server Error"

        # Test ValidationError handler
        try:
            from pydantic import BaseModel
            class TestModel(BaseModel):
                name: str

            TestModel(name=123)
        except ValidationError as exc:
            response = await exception_handlers[ValidationError](mock_request, exc)
            content = decoded_response(response)
            assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
            assert isinstance(content["detail"], list)

        # Test CustomError handler
        exc = CustomError("Test")
        response = await exception_handlers[CustomError](mock_request, exc)
        content = decoded_response(response)
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert content["detail"] == "Test"

    def test_exception_handlers_dict_keys(self):
        """Test that exception_handlers dict contains the expected keys."""
        expected_keys = {Exception, ValidationError, CustomError}
        assert set(exception_handlers.keys()) == expected_keys


class TestIntegration:
    """Integration tests for exception handlers."""

    @pytest.mark.asyncio
    async def test_handler_selection_based_on_exception_type(self, mock_request, decoded_response):
        """Test that the correct handler is selected based on exception type."""
        test_cases = [
            (Exception("test"), exception_handler, status.HTTP_500_INTERNAL_SERVER_ERROR, "Internal Server Error"),
            (CustomError("test"), custom_error_handler, status.HTTP_500_INTERNAL_SERVER_ERROR, "test")
        ]

        # Add ValidationError test case separately since it's harder to create
        for exc, expected_handler, expected_status, expected_message in test_cases:
            handler = exception_handlers[type(exc)]
            assert handler == expected_handler

            response = await handler(mock_request, exc)
            content = decoded_response(response)
            assert response.status_code == expected_status

            if expected_message is not None:
                assert content["detail"] == expected_message

    @pytest.mark.asyncio
    async def test_validation_error_integration(self, mock_request, decoded_response):
        """Test validation error handler separately."""
        try:
            from pydantic import BaseModel
            class TestModel(BaseModel):
                name: str

            TestModel(name=123)
        except ValidationError as exc:
            handler = exception_handlers[ValidationError]
            assert handler == validation_exception_handler

            response = await handler(mock_request, exc)
            content = decoded_response(response)
            assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
            assert isinstance(content["detail"], list)

    @pytest.mark.asyncio
    async def test_all_handlers_return_json_response(self, mock_request):
        """Test that all handlers return JSONResponse objects."""
        handlers_to_test = [
            (Exception("test"), exception_handler),
            (CustomError("test"), custom_error_handler)
        ]

        for exc, handler in handlers_to_test:
            response = await handler(mock_request, exc)
            assert isinstance(response, JSONResponse)

    @pytest.mark.asyncio
    async def test_validation_handler_returns_json_response(self, mock_request):
        """Test that validation handler returns JSONResponse."""
        try:
            from pydantic import BaseModel
            class TestModel(BaseModel):
                name: str

            TestModel(name=123)
        except ValidationError as exc:
            response = await validation_exception_handler(mock_request, exc)
            assert isinstance(response, JSONResponse)
