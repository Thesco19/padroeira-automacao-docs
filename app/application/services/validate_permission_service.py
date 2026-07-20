from app.ports.permission_port import PermissionPort

class ValidatePermissionService:
    """Case of use: Validate user permission for an operation."""
    def __init__(self, permission_port: PermissionPort):
        self._permission_port = permission_port

    def execute(self, user_id: str, operation: str) -> bool:
        return self._permission_port.validate_permission(user_id, operation)
