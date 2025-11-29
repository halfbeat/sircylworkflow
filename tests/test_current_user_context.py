from sircylworkflow.globals import current_user

def test_current_user_context():
    print("HOLA")
    assert current_user is not None
    assert current_user.nombre is not None
    print(current_user.nombre)