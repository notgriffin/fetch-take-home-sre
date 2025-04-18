from src.fetch_take_home_sre.models import EndpointHealthCheckConfig

def test_endpoint_config_model(health_check):
    EndpointHealthCheckConfig.model_validate(health_check)
