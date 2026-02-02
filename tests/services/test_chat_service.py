from unittest.mock import AsyncMock, MagicMock

import pytest

from lineaihelper.exceptions import ExternalAPIError, ServiceError
from lineaihelper.services.chat_service import ChatService


@pytest.mark.asyncio
async def test_chat_service_execute_success() -> None:
    mock_gemini = MagicMock()
    mock_response = MagicMock()
    mock_response.text = "Hello!"
    mock_gemini.aio.models.generate_content = AsyncMock(return_value=mock_response)
    service = ChatService(mock_gemini)

    response = await service.execute("Hi")
    assert response == "Hello!"


@pytest.mark.asyncio
async def test_chat_service_empty_args() -> None:
    service = ChatService(MagicMock())
    with pytest.raises(ServiceError) as excinfo:
        await service.execute("")
    assert "請提供聊天內容" in str(excinfo.value)


@pytest.mark.asyncio
async def test_chat_service_quota_error() -> None:
    mock_gemini = MagicMock()
    mock_gemini.aio.models.generate_content.side_effect = Exception("quota exceeded")
    service = ChatService(mock_gemini)

    with pytest.raises(ExternalAPIError) as excinfo:
        await service.execute("Hi")
    assert "額度已達上限" in str(excinfo.value)
