import pytest
import pathlib
import yaml

SAMPLE_YAML = pathlib.Path(__file__).parent / "test_cli"
CHILD_FILES = list(SAMPLE_YAML.iterdir())

# Generate all Test Data for health checking
HEALTH_CHECK_DATA = []
for f in CHILD_FILES:
    for i in yaml.safe_load(f.read_text()):
        assert isinstance(i, dict)
        HEALTH_CHECK_DATA.append(i)

@pytest.fixture(params=CHILD_FILES)
def sample_yaml(request) -> pathlib.Path:
    """Give a sample yaml file for the health checks.

    Returns:
        pathlib.Path: Path to a sample file
    """    
    assert request.param.exists() and request.param.is_file()
    return request.param


@pytest.fixture
def sample_yaml_data(sample_yaml: pathlib.Path) -> list:
    return yaml.safe_load(sample_yaml.read_text())


@pytest.fixture(params=HEALTH_CHECK_DATA, ids=map(lambda x: x.get("name"), HEALTH_CHECK_DATA))
def health_check(request) -> dict:
    return request.param.copy()