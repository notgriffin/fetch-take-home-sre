from src.fetch_take_home_sre import endpoint_monitoring, models
import pytest
import pytest_asyncio


@pytest_asyncio.fixture()
async def aiosession():
    import aiohttp
    timeout = aiohttp.ClientTimeout(total=15, sock_read=0.5)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        yield session


@pytest.mark.asyncio
async def test_check_health(health_check: dict, aiosession):
    status = endpoint_monitoring.StatusEnum.DOWN if health_check.get("name", "").casefold().endswith("down".casefold()) else endpoint_monitoring.StatusEnum.UP
    _, r = await endpoint_monitoring.check_health(aiosession, health_check.pop("url"), **health_check)
    assert r == status


@pytest.mark.asyncio
async def test_check_health_failure(aiosession):
    _, r = await endpoint_monitoring.check_health(aiosession, "http://localhost:9999", "test")
    assert r == endpoint_monitoring.StatusEnum.DOWN


@pytest.mark.asyncio
async def test_check_health_degraded(health_check: dict, aiosession, mocker):
    mocker.patch("src.fetch_take_home_sre.endpoint_monitoring.time.perf_counter", side_effect=[0, 0.5])
    status = endpoint_monitoring.StatusEnum.DOWN if health_check.get("name", "").casefold().endswith("down".casefold()) else endpoint_monitoring.StatusEnum.DEGRADED
    _, r = await endpoint_monitoring.check_health(aiosession, health_check.pop("url"), **health_check)
    assert r == status


def test_print_statistics():
    from unittest.mock import patch
    with patch.dict(endpoint_monitoring.RUNTIME_HEALTH_STATUS, {"test": endpoint_monitoring.HealthStatus()}):
        endpoint_monitoring.RUNTIME_HEALTH_STATUS["test"].up += 1
        endpoint_monitoring.print_statistics(1)

@pytest.mark.parametrize("status", endpoint_monitoring.StatusEnum)
def test_record_health(status):
    from unittest.mock import patch
    with patch.dict(endpoint_monitoring.RUNTIME_HEALTH_STATUS, {"test": endpoint_monitoring.HealthStatus()}):
        assert endpoint_monitoring.RUNTIME_HEALTH_STATUS["test"].count() == 0
        endpoint_monitoring.record_health("test", status)
        assert endpoint_monitoring.RUNTIME_HEALTH_STATUS["test"].count() == 1


@pytest.mark.asyncio
async def test_monitor_endpoints(sample_yaml_data):
    from datetime import datetime, timedelta
    test_data = [models.EndpointHealthCheckConfig.model_validate(i) for i in sample_yaml_data]
    run_until = datetime.now() + timedelta(seconds=0.5)
    result = await endpoint_monitoring.monitor_endpoints(test_data, run_until, 1)
    assert result == 1


