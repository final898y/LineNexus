from unittest.mock import AsyncMock, MagicMock
import pytest
from lineaihelper.services.chat_service import ChatService

@pytest.mark.asyncio
async def test_chat_service_execute_success():
    # Arrange
    mock_gemini = MagicMock()
    mock_response = MagicMock()
    mock_response.text = "Hello there!"
    mock_gemini.aio.models.generate_content = AsyncMock(return_value=mock_response)

    service = ChatService(mock_gemini)

    # Act
    response = await service.execute("Hi")

    # Assert
    assert response == "Hello there!"
    mock_gemini.aio.models.generate_content.assert_called_once()

@pytest.mark.asyncio
async def test_chat_service_empty_args():
    mock_gemini = MagicMock()
    service = ChatService(mock_gemini)
    
    response = await service.execute("")
    assert "Please provide content" in response

@pytest.mark.asyncio
async def test_chat_service_error():
    # Arrange
    mock_gemini = MagicMock()
    # Simulate API Error
    mock_gemini.aio.models.generate_content.side_effect = Exception("Gemini Down")
    
    service = ChatService(mock_gemini)

    # Act
    response = await service.execute("Hi")

    # Assert
    assert "AI is currently unavailable" in response
