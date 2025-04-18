# Fetch Take Home Exercise - SRE

*Solution by Griffin Rufe*

- [Fetch Take Home Exercise - SRE](#fetch-take-home-exercise---sre)
  - [Installation](#installation)
  - [Running the Script](#running-the-script)
- [Solution Walkthrough](#solution-walkthrough)
  - [Parallel Requests](#parallel-requests)
  - [Refining Health Identification](#refining-health-identification)
  - [Maintainability](#maintainability)
    - [Runtime Environment Control](#runtime-environment-control)
    - [Command Line](#command-line)
    - [Config Validation](#config-validation)
    - [Testing](#testing)


## Installation

To install, use pip in your target python environment. This code has been validated on python>=3.13. Usage in other python versions may not work correctly.

```
pip install ./fetch-take-home-sre
```

## Running the Script

```bash
$> monitor_endpoints --help

Usage: monitor_endpoints [OPTIONS] CONFIG_FILE_PATH

  Monitor hosts provided in a config file

  Args:     health_check_frequency (int): Frequency with which to check health
  in seconds.     run_duration (int): Length of time to run program in
  seconds.     config_file_path (IO): A file buffer passed in from Click.

Options:
  -f, --health-check-frequency INTEGER
                                  Frequency with which to check health in
                                  seconds.
  -r, --run-duration INTEGER      Length of time to run program in seconds.
  --help                          Show this message and exit.
```

# Solution Walkthrough

The main challenge to overcome with the requirements is ensuring that all health checks can take place in the 15 second window required. Completing these checks sequentially can lead to a bottle neck if several of those requests take more time then might be expected.

As a minor feature, keyboard interrupts from the user lead to a final reporting of the statistics of the health check. This ensures that no information is lost when the command is stopped.

## Parallel Requests

For the solution to complete in the time required, there are several approaches that would have worked. Multithreading and multiprocessing would been workable, but there is an unnecessary memory and CPU use time addition for this approach. My approach uses async/await code for python. This approach allows for opportunistic CPU scheduling of web requests, handling their responses, and allowing for many web requests to run simultaneously while ensuring that only a single thread is consumed on the system running this script.


## Refining Health Identification

The solution requirements included failing a health check if a request took over 500ms. This is a good benchmark for determining if something is healthy or not, but leaves a less clear log if the request succeeded but took too long. 

I have included a third status type: degraded. This allows for identifying if an application is either completely unavailable or if it is unable to reach a quality of service for response times. Connectivity and availability are both important to identify what is wrong with an application to assist in forming a solution.

Utilizing this method also ensures that we can take the entire 15 second window to wait for a request. This allows the addition of logic for refining and extending the health check logic to include other conditions.

## Maintainability

### Runtime Environment Control

Using Python Poetry, the runtime environment can be specified to particular python package versions. This is important for several reasons:

1. It ensures that test and production environments are fully reproducible.
2. Package version updates will not break the re-installation process.
3. It allows for version controlling of the specific versions installed.
4. Tooling based around vulnerability detection which can read a poetry lock file can be utilized to ensure this application remains secure.

Notably, the original solution utilizes the `requests` library, which is not a default installed package for python. For running the original script, there is no indication this is a runtime dependency until an import failure would be encountered.

### Command Line

Using a standard package for reading the command line ensures good support for multiple CLI environments. `Click`, in this case, also allows for easy updating of options that significantly reduces the need for custom logic.

### Config Validation

Everyone makes mistakes. Config updates should be validated to ensure that they will work. There is base-line model validation of the YAML file using `pydantic` to ensure that there are the correct key values present. 

This is an area that could be improved if there was a requirement to. Features like URL validation could be added.

### Testing

In this case, I added comprehensive unit testing to validate the script code and sample config files.

At bare minimum, a program like this should at least have basic CLI command running validation to ensure that code syntax is correct and basic logic works.

To run tests:

1. Install [poetry](https://python-poetry.org/)
2. Open the source code directory and run `poetry install --groups test`.
3. Run `poetry run pytest` and observe the test results.

With the testing framework set up, new features can easily be validated.