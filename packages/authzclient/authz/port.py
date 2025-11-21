import abc
from typing import Optional

from model import Rol


class AuthorizationPort(abc.ABC):
    @abc.abstractmethod
    def get_permisos_rol(self, rol_id: str) -> list[str]:
        raise NotImplementedError

    @abc.abstractmethod
    def get_roles_principal(self, principal: str) -> list[Rol]:
        raise NotImplementedError

    @abc.abstractmethod
    def asignar_rol_principal(self, principal: str, rol_id: str, ambito: Optional[str] = None):
        raise NotImplementedError

    @abc.abstractmethod
    def eliminar_rol_principal(self, principal: str, rol_id: str, ambito: Optional[str] = None):
        raise NotImplementedError