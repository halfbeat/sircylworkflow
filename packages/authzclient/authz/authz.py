import itertools
import logging
from typing import Optional

import requests
from cachetools.func import ttl_cache

from model import Rol
from port import AuthorizationPort

logger = logging.getLogger(__name__)


class AuthzAdapter(AuthorizationPort):
    def __init__(self, aplicacion: str, authz_uri: str, jwt_token: str):
        self._aplicacion = aplicacion
        self._authz_uri = authz_uri.rstrip("/")
        self._jwt_token = jwt_token

    @ttl_cache(ttl=120)
    def get_roles_principal(self, principal: str) -> list[Rol]:
        uri = f"{self._authz_uri}/usuarios/{principal}/roles?aplicacion={self._aplicacion}"
        headers = {'Accept': 'application/json', 'Authorization': f"Bearer {self._jwt_token}"}
        logger.debug('Obteniendo los roles del principal %s', principal)
        response = requests.get(uri, headers=headers)
        logger.debug('Respuesta %d', response.status_code)
        response.raise_for_status()
        data = response.json()
        if data is None:
            return []

        roles = []
        for rol_id, asignaciones in itertools.groupby(data['asignacion'], lambda x: x['idRol']):
            ambitos = set()
            for asignacion in list(asignaciones):
                ambito = asignacion.get('idAmbito')
                if ambito is not None:
                    ambitos.add(asignacion['idAmbito'])
                else:
                    ambitos = set()
                    break

            # ambitos = [a['idAmbito'] for a in list(asignaciones) if a.get('idAmbito') is not None]
            permisos = self.get_permisos_rol(rol_id)
            rol = Rol(rol_id, list(ambitos), permisos)
            roles.append(rol)

        return roles

    @ttl_cache(ttl=120)
    def get_permisos_rol(self, rol_id: str) -> list[str]:
        uri = f"{self._authz_uri}/aplicaciones/{self._aplicacion}/roles/{rol_id}"
        headers = {'Accept': 'application/json', 'Authorization': f"Bearer {self._jwt_token}"}
        logger.debug('Obteniendo los permisos del rol %s', rol_id)
        response = requests.get(uri, headers=headers)
        response.raise_for_status()
        logger.debug('Respuesta %d', response.status_code)
        data = response.json()
        if data is None or data.get('permisos') is None:
            return []
        return data['permisos']

    def asignar_rol_principal(self, principal: str, rol_id: str, ambito: Optional[str] = None):
        if principal is None:
            return
        uri = f"{self._authz_uri}/usuarios/{principal}/roles"
        headers = {'Accept': 'application/json', 'Authorization': f"Bearer {self._jwt_token}"}
        logger.debug('Asignando el rol %s con el ámbito %s al principal %s', rol_id, ambito, principal)
        peticion = {"principal": principal, "idAplicacion": self._aplicacion, "idRol": rol_id, "idAmbito": ambito}
        response = requests.put(uri, headers=headers, json=peticion)
        response.raise_for_status()
        logger.debug('Respuesta %d', response.status_code)

    def eliminar_rol_principal(self, principal: str, rol_id: str, ambito: Optional[str] = None):
        if principal is None:
            return
        asignaciones = self._get_asignaciones_rol_principal(principal, rol_id, ambito)
        for asignacion in asignaciones:
            self._eliminar_asignacion(principal, asignacion)

    def _get_asignaciones_rol_principal(self, principal: str, rol_id: str, ambito: Optional[str]) -> list[int]:
        uri = f"{self._authz_uri}/usuarios/{principal}/roles?aplicacion={self._aplicacion}&rol={rol_id}"
        if ambito:
            uri = f"{uri}&ambito={ambito}"
        headers = {'Accept': 'application/json', 'Authorization': f"Bearer {self._jwt_token}"}
        logger.debug('Obteniendo los roles del principal %s', principal)
        response = requests.get(uri, headers=headers)
        logger.debug('Respuesta %d', response.status_code)
        response.raise_for_status()
        data = response.json()
        if data is None:
            return []

        return [asgn["idAsignacion"] for asgn in data['asignacion']]

    def _eliminar_asignacion(self, principal, asignacion):
        uri = f"{self._authz_uri}/usuarios/{principal}/roles/{asignacion}"
        headers = {'Accept': 'application/json', 'Authorization': f"Bearer {self._jwt_token}"}
        logger.debug('Eliminando la asignación %d del principal %s', asignacion, principal)
        response = requests.delete(uri, headers=headers)
        response.raise_for_status()
        logger.debug('Respuesta %d', response.status_code)
