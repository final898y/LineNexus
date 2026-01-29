from unittest.mock import AsyncMock, MagicMock

import pytest

from lineaihelper.dispatcher import CommandDispatcher
from lineaihelper.exceptions import ServiceError
from lineaihelper.services.base_service import BaseService


@pytest.mark.asyncio
async def test_dispatch_handling_service_error():
    # Arrange
    mock_gemini = MagicMock()
    dispatcher = CommandDispatcher(mock_gemini)

    mock_service = AsyncMock(spec=BaseService)
    # 模擬 Service 拋出業務錯誤
    mock_service.execute.side_effect = ServiceError("自定義錯誤訊息")
    dispatcher.services["/test"] = mock_service

    # Act
    response = await dispatcher.parse_and_execute("/test args")

    # Assert
    assert response == "⚠️ 自定義錯誤訊息"


@pytest.mark.asyncio
async def test_dispatch_handling_unexpected_error():
    # Arrange
    mock_gemini = MagicMock()
    dispatcher = CommandDispatcher(mock_gemini)

    mock_service = AsyncMock(spec=BaseService)
    # 模擬未預期的系統崩潰
    mock_service.execute.side_effect = RuntimeError("Crash!")
    dispatcher.services["/test"] = mock_service

    # Act
    response = await dispatcher.parse_and_execute("/test args")

    # Assert
    assert "❌ 系統發生未知錯誤" in response


@pytest.mark.asyncio
async def test_dispatch_routing_success():
    mock_gemini = MagicMock()
    dispatcher = CommandDispatcher(mock_gemini)

    mock_service = AsyncMock(spec=BaseService)
    mock_service.execute.return_value = "Success"
    dispatcher.services["/stock"] = mock_service

    response = await dispatcher.parse_and_execute("/stock 2330")
    assert response == "Success"
