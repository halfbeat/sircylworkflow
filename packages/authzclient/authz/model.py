from dataclasses import dataclass
from enum import Enum
from typing import Optional, Any

from error import PermisoRequerido, RolRequerido


class Roles(Enum):
    ADM = 'INVE@ADM'
    GESTOR = 'INVE@GESTOR'
    GESTOR_SISTEMA = 'INVE@GESTOR_SISTEMA'
    CONSULTA = 'INVE@CONSULTA'


class Permisos(Enum):
    REGISTRAR_SISTEMA = 'sistemas:registrar'
    CONSULTAR_SISTEMAS = 'sistemas:consultar'
    CONSULTAR_SISTEMA = 'sistema:consultar'
    MODIFICAR_SISTEMA = 'sistema:modificar'
    ELIMINAR_SISTEMA = 'sistema:eliminar'
    ASIGNAR_SISTEMA = 'sistema:asignar'
    REGISTRAR_COMPONENTE = 'sistema:componentes:registrar'
    MODIFICAR_COMPONENTE = 'sistema:componentes:modificar'
    ELIMINAR_COMPONENTE = 'sistema:componentes:eliminar'
    CONSULTAR_DOCUMENTOS_SISTEMA = 'sistema:documentos:consultar'
    ANIADIR_DOCUMENTO_SISTEMA = 'sistema:documentos:aniadir'
    MODIFICAR_DOCUMENTO_SISTEMA = 'sistema:documentos:modificar'
    ELIMINAR_DOCUMENTO_SISTEMA = 'sistema:documentos:eliminar'
    MODIFICAR_TAG = 'tags:modificar'


@dataclass(frozen=True)
class Rol:
    rol_id: str
    ambitos: list[str]
    permisos: list[str]

    def has_permiso(self, permiso_id: Permisos) -> bool:
        for permiso in self.permisos:
            if permiso == permiso_id.value:
                return True

        return False

    def check_permiso(self, permiso_id: Permisos):
        if not self.has_permiso(permiso_id):
            raise PermisoRequerido(permiso_id)

    def __str__(self):
        return f"rol_id={self.rol_id}, ambitos={self.ambitos}, permisos={self.permisos}"


@dataclass(frozen=True)
class Usuario:
    principal: str
    roles: list[Rol]
    nombre: Optional[str]
    apellidos: Optional[str]
    email: Optional[str]
    documento_identidad: Optional[str]
    jwt_token: Optional[dict[str, Any]]

    def has_rol(self, role_id: Roles, ambito: Optional[str] = None, sin_ambitos: bool = False) -> bool:
        return self.get_rol(role_id, ambito, sin_ambitos) is not None

    def has_permiso(self, permiso_id: Permisos, ambito: Optional[str] = None) -> bool:
        for rol in self.roles:
            result = False
            if permiso_id.value not in rol.permisos:
                pass
            if not ambito:
                result = rol.has_permiso(permiso_id)
            else:
                if len(rol.ambitos) == 0:
                    result = True
                else:
                    result = ambito in rol.ambitos
            if result:
                return result

        return False

    def get_rol(self, role_id: Roles, ambito: Optional[str] = None, sin_ambitos: bool = False) -> Optional[Rol]:
        def predicate(rol: Rol) -> bool:
            res = rol.rol_id == role_id.value
            if sin_ambitos:
                res = res and (rol.ambitos is None or len(rol.ambitos) == 0)
            if ambito is not None:
                res = res and ambito in rol.ambitos
            return res

        return next(
            iter([rol for rol in self.roles if predicate(rol)]),
            None)

    def check_rol(self, rol_id: Roles):
        if not self.has_rol(rol_id):
            raise RolRequerido(rol_id)

    def check_permiso(self, permiso_id: Permisos, ambito: Optional[str] = None):
        if not self.has_permiso(permiso_id, ambito):
            raise PermisoRequerido(permiso_id)

    def __str__(self):
        return f"{self.principal}: nombre={self.nombre} {self.apellidos}, dni={self.documento_identidad} email={self.email} roles={self.roles}"

    def get_ambitos_permiso(self, permiso_id: Permisos) -> list[str]:
        res = set()
        for rol in self.roles:
            if rol.has_permiso(permiso_id):
                if rol.ambitos is None or len(rol.ambitos) == 0:
                    return []
                else:
                    res.update(rol.ambitos)
        return list(res)

