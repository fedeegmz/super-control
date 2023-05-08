# FastAPI
from fastapi.testclient import TestClient

# main
from .main import app


client = TestClient(app)


def test_verify_statuscode_from_root():
    """
    Verifica que la Path Operation root retorne un codigo de estado 200
    """
    response = client.get("/")

    assert response.status_code == 200


### USERS ### -> prefix=users

def test_correct_user_to_register():
    """
    Verifica que el usuario que se va a registrar sea correcto
    """
    fake_user = {
        "username": "ironman",
        "name": "Anthony",
        "lastname": "Stark",
        "email": "tony@starkindustries.com",
        "birth_date": "2000-12-25",
        "password": "ILoveMark40"
    }

    response = client.post(
        url = "/users/signup",
        json = fake_user
    )

    assert response.status_code == 201
    assert response.json() == fake_user

def test_incorrect_user_not_registered():
    """
    Verifica que no se registre un usuario incorrecto.
    fake_user no tiene password.
    """
    fake_user = {
        "username": "ironman",
        "name": "Anthony",
        "lastname": "Stark",
        "email": "tony@starkindustries.com"
    }

    response = client.post(
        url = "/users/signup",
        json = fake_user
    )

    assert response.status_code == 409