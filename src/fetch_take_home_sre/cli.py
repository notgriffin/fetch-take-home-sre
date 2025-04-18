import asyncio
from datetime import datetime, timedelta
from typing import IO
from pydantic import ValidationError

import click
import yaml

from . import endpoint_monitoring, models


@click.command()
@click.option(
    "-f",
    "--health-check-frequency",
    type=int,
    default=15,
    help="Frequency with which to check health in seconds.",
)
@click.option(
    "-r",
    "--run-duration",
    type=int,
    default=None,
    help="Length of time to run program in seconds.",
)
@click.argument("config_file_path", type=click.File("r"))
def monitor(
    health_check_frequency: int, run_duration: int, config_file_path: IO
) -> None:
    """Monitor hosts provided in a config file

    Args:
        health_check_frequency (int): Frequency with which to check health in seconds.
        run_duration (int): Length of time to run program in seconds.
        config_file_path (IO): A file buffer passed in from Click.
    """
    config = yaml.safe_load(config_file_path)
    try:
        health_check_data = [
            models.EndpointHealthCheckConfig.model_validate(i) for i in config
        ]
    except ValidationError as e:
        print(f"Error: Input file is malformed - {e}")
        exit(1)
        
    run_until = (
        (datetime.now() + timedelta(seconds=run_duration)) if run_duration else None
    )
    try:
        asyncio.run(
            endpoint_monitoring.monitor_endpoints(
                health_check_data, run_until, health_check_frequency
            )
        )
    except KeyboardInterrupt:
        endpoint_monitoring.print_statistics()
        print("\nMonitoring stopped by user.")
    else:
        print("Run complete!")


if __name__ == "__main__":
    monitor()
