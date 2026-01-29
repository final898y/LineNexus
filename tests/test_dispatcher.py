from unittest.mock import AsyncMock, MagicMock
import pytest
from lineaihelper.dispatcher import CommandDispatcher
from lineaihelper.services.base_service import BaseService

@pytest.mark.asyncio
async def test_dispatch_routing_stock():
    # Arrange
    mock_gemini = MagicMock()
    dispatcher = CommandDispatcher(mock_gemini)
    
    # 替換 dispatcher 內部的 service 實例為 Mock
    mock_stock_service = AsyncMock(spec=BaseService)
    mock_stock_service.execute.return_value = "Mock Stock Response"
    dispatcher.services["/stock"] = mock_stock_service

    # Act
    response = await dispatcher.parse_and_execute("/stock 2330")

    # Assert
    assert response == "Mock Stock Response"
    mock_stock_service.execute.assert_called_once_with("2330")

@pytest.mark.asyncio
async def test_dispatch_routing_chat():
    # Arrange
    mock_gemini = MagicMock()
    dispatcher = CommandDispatcher(mock_gemini)
    
    mock_chat_service = AsyncMock(spec=BaseService)
    mock_chat_service.execute.return_value = "Mock Chat Response"
    dispatcher.services["/chat"] = mock_chat_service

    # Act
    response = await dispatcher.parse_and_execute("/chat hello")

    # Assert
    assert response == "Mock Chat Response"
    mock_chat_service.execute.assert_called_once_with("hello")

@pytest.mark.asyncio
async def test_dispatch_unknown_command():
    mock_gemini = MagicMock()
    dispatcher = CommandDispatcher(mock_gemini)

    response = await dispatcher.parse_and_execute("/foobar")
    assert "Unknown command: /foobar" in response

@pytest.mark.asyncio
async def test_dispatch_no_command_echo():
    mock_gemini = MagicMock()
    dispatcher = CommandDispatcher(mock_gemini)

    response = await dispatcher.parse_and_execute("Just some text")
    assert "LineNexus (Async) received: Just some text" in response