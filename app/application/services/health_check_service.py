from app.ports.health_port import HealthCheckPort

class HealthCheckService:
    """Case of use: Perform a health check."""
    def __init__(self, health_port: HealthCheckPort):
        self._health_port = health_port

    def execute(self) -> bool:
        return self._health_port.health_check()
