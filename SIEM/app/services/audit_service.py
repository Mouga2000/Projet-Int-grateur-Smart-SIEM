from app.repositories.audit_repo import AuditRepository
from app.core.elasticsearch import get_es

class AuditService:
    def __init__(self, audit_repo: AuditRepository):
        self.audit_repo = audit_repo
    
    async def log_login(self, user_id: str, username: str, success: bool, ip_address: str = None):
        return await self.audit_repo.log_login_attempt(user_id, username, success, ip_address)
    
    async def log_logout(self, user_id: str, username: str):
        return await self.audit_repo.log_logout(user_id, username)
    
    async def log_mfa(self, user_id: str, username: str, success: bool):
        return await self.audit_repo.log_mfa_verification(user_id, username, success)
    
    async def log_user_creation(self, admin_id: str, new_username: str):
        return await self.audit_repo.log_user_management(
            admin_id, "create_user", new_username, {"by": admin_id}
        )
    
    async def log_role_change(self, admin_id: str, target_username: str, old_role: str, new_role: str):
        return await self.audit_repo.log_user_management(
            admin_id, "update_role", target_username, {"old_role": old_role, "new_role": new_role}
        )

def get_audit_service():
    return AuditService(AuditRepository(get_es()))