import pytest

from lineaihelper.services.help_service import HelpService


@pytest.mark.asyncio
async def test_help_service_execute() -> None:
    service = HelpService()
    response = await service.execute("")

    assert "[LineNexus Commands]" in response
    assert ".stock" in response
    assert ".price" in response
    assert ".chat" in response
