class RolRequerido(Exception):
    def __init__(self, rol_id):
        super().__init__(f"El rol {rol_id} es requerido")


class PermisoRequerido(Exception):
    def __init__(self, permiso_id):
        super().__init__(f"El permiso {permiso_id} es requerido")


class TokenJwtInvalido(Exception):
    def __init__(self, err):
        super().__init__(f"El token no es valido: {err}")
        self.err = err

class TokenJwtRequerido(Exception):
    def __init__(self):
        super().__init__("Se requiere un token JWT")

class CredencialesRequeridas(Exception):
    def __init__(self):
        super().__init__("Se requieren credenciales")