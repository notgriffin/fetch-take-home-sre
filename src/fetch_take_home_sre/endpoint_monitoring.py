import asyncio
import time
from datetime import datetime, timedelta
from enum import Enum, auto

import aiohttp
import aiohttp.client_exceptions

from .models import EndpointHealthCheckConfig


class StatusEnum(Enum):
    """Categories of all statuses possible"""

    UP = auto()
    DOWN = auto()
    DEGRADED = auto()


class HealthStatus:
    """An object for holding the context of a health status for each health check."""

    up = 0
    down = 0
    degraded = 0

    def count(self) -> int:
        """Return a total count of all health check statuses.

        Returns:
            int: Summation of all health check types.
        """
        return self.up + self.down + self.degraded

    def __repr__(self) -> str:
        """Helper function for printing objects for debugging.

        Returns:
            str: Stringified dict representation of object.
        """
        d = {"up": self.up, "down": self.down, "degraded": self.degraded}
        return str(d)


# Global Health Check object for holding historical statuses.
RUNTIME_HEALTH_STATUS: dict[str, HealthStatus] = dict()


async def check_health(
    session: aiohttp.ClientSession,
    url: str,
    name: str,
    method: str = "GET",
    headers: dict[str, str] = None,
    degraded_service_threshold: float = 0.5,
    body: str = None,
) -> tuple[str, StatusEnum]:
    """Check the health of an endpoint_url on a given session using the request method, headers, and body.

    Args:
        session (aiohttp.ClientSession): A shared session for a program context
        url (str): Target URL for the health check
        name (str): A name for the health check that is passed through to the returned value
        method (str, optional): A standard HTTP request type. Defaults to "GET".
        headers (dict[str, str], optional): Header values to send with request. Defaults to None.
        body (str, optional): Body to send with request. Defaults to None.
    """

    start_time = time.perf_counter()
    status = None

    response: aiohttp.ClientResponse
    try:
        async with session.request(method, url, headers=headers, data=body) as response:
            end_time = time.perf_counter()
            if 200 <= response.status < 300:
                if (end_time - start_time) < degraded_service_threshold:
                    # If the request succeeded in time allotted, UP
                    status = StatusEnum.UP
                else:
                    # If request succeeded outside time allotted, DEGRADED
                    status = StatusEnum.DEGRADED
            else:
                # Request Failure
                status = StatusEnum.DOWN

    except aiohttp.client_exceptions.ClientError:
        status = StatusEnum.DOWN

    return name, status


def print_statistics(total_checks: int) -> None:
    """Print statistics of global health check object using the input total checks as a shortcut for
    not having to compute the check values for each host.

    Args:
        total_checks (int): Total number of health checks done.
    """    
    global RUNTIME_HEALTH_STATUS
    print(f"Health Check Time: {datetime.now().isoformat()}")
    for k, v in RUNTIME_HEALTH_STATUS.items():
        print(
            f"{k} Health: {(v.up / total_checks):.2f}% Up | {(v.down / total_checks):.2f}% Down | {(v.degraded / total_checks):.2f}% Degraded"
        )


def record_health(name: str, health: StatusEnum):
    """Add health check info to global health check object.

    Args:
        name (str): Name of health check to reference in global health dictionary.
        health (StatusEnum): The health status of a host. 
    """    
    global RUNTIME_HEALTH_STATUS
    match health:
        case StatusEnum.UP:
            RUNTIME_HEALTH_STATUS[name].up += 1
        case StatusEnum.DOWN:
            RUNTIME_HEALTH_STATUS[name].down += 1
        case StatusEnum.DEGRADED:
            RUNTIME_HEALTH_STATUS[name].degraded += 1


async def monitor_endpoints(
    endpoints: list[EndpointHealthCheckConfig],
    run_until: datetime = None,
    frequency_seconds: int = 15,
) -> int:
    """Run health checks on given list of endpoints.

    Args:
        endpoints (list[EndpointHealthCheckConfig]): Endpoint config data to check
        run_until (datetime, optional): When to stop running the health check. Defaults to None.
        frequency_seconds (int, optional): How long between health checks. Defaults to 15.

    Returns:
        int: Number of health checks completed when exiting.
    """    
    global RUNTIME_HEALTH_STATUS

    timeout = aiohttp.ClientTimeout(total=frequency_seconds-1, sock_read=0.5)
    total_checks = 0

    RUNTIME_HEALTH_STATUS = {i.name: HealthStatus() for i in endpoints}

    # Either run continuously or until given time.
    while (not run_until) or datetime.now() < run_until:
        # Space runs evenly
        target_next_start = datetime.now() + timedelta(seconds=frequency_seconds)
        # Share a session object between all requests
        async with aiohttp.ClientSession(timeout=timeout) as session:
            # Generate futures to run parallel
            generate_tasks: list[asyncio.Future] = [
                check_health(session, i.url, i.name, i.method, i.headers, i.body)
                for i in endpoints
            ]
            # Run all health checks opportunistically and in parallel
            results = await asyncio.gather(*generate_tasks)
            # Record all results
            for result in results:
                record_health(*result)
            total_checks += 1
            print_statistics(total_checks)

        delay = (target_next_start - datetime.now()).total_seconds()
        # Wait until next frequency time is hit
        await asyncio.sleep(delay)

    return total_checks
