from typing import Optional
from authzclient.model import Rol
from authzclient.port import AuthorizationPort

from sircylworkflow.domain.security import Permisos, Roles

class AuthzMock(AuthorizationPort):
    def get_permisos_rol(self, rol_id: str) -> list[str]:
        return [p.value for p in Permisos]

    def get_roles_principal(self, principal: str) -> list[Rol]:
        return [Rol(Roles.GESTOR.value, [], [p.value for p in Permisos])]

    def asignar_rol_principal(
        self, principal: str, rol_id: str, ambito: Optional[str] = None
    ):
        raise NotImplementedError

    def eliminar_rol_principal(
        self, principal: str, rol_id: str, ambito: Optional[str] = None
    ):
        raise NotImplementedError