from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from lineaihelper.dispatcher import CommandDispatcher


@pytest.mark.asyncio
async def test_dispatch_help():
    mock_gemini = MagicMock()
    dispatcher = CommandDispatcher(mock_gemini)

    response = await dispatcher.parse_and_execute("/help")
    assert "[LineNexus Commands]" in response
    assert "/stock" in response


@pytest.mark.asyncio
async def test_dispatch_echo():
    mock_gemini = MagicMock()
    dispatcher = CommandDispatcher(mock_gemini)

    response = await dispatcher.parse_and_execute("Hello")
    assert "LineNexus (Async) received: Hello" in response


@pytest.mark.asyncio
async def test_dispatch_chat_success():
    mock_gemini = MagicMock()
    mock_response = MagicMock()
    mock_response.text = "AI Response"
    mock_gemini.aio.models.generate_content = AsyncMock(return_value=mock_response)

    dispatcher = CommandDispatcher(mock_gemini)
    response = await dispatcher.parse_and_execute("/chat hello")

    assert response == "AI Response"
    mock_gemini.aio.models.generate_content.assert_called_once()


@pytest.mark.asyncio
async def test_dispatch_stock_success():
    mock_gemini = MagicMock()
    mock_response = MagicMock()
    mock_response.text = "Stock Analysis"
    mock_gemini.aio.models.generate_content = AsyncMock(return_value=mock_response)

    dispatcher = CommandDispatcher(mock_gemini)

    with patch("lineaihelper.dispatcher.yf.Ticker") as mock_ticker:
        mock_ticker.return_value.info = {
            "longName": "Test Stock",
            "currentPrice": 100,
            "trailingPE": 10,
            "trailingEps": 5,
            "longBusinessSummary": "Summary",
        }

        response = await dispatcher.parse_and_execute("/stock 2330")

        assert response == "Stock Analysis"
        mock_ticker.assert_called_once_with("2330.TW")
        mock_gemini.aio.models.generate_content.assert_called_once()
