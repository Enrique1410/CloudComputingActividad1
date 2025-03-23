from app.authentication.dependency_injection.domain.register_controllers import (
    RegisterControllers,
)
from app.authentication.dependency_injection.domain.login_controllers import (
    LoginControllers,
)
from app.authentication.domain.persistences.exceptions import (
    WrongPasswordException,
    UserNotFoundException,
    UsernameAlreadyTakenException,
)
from fastapi import APIRouter, Body, HTTPException, Header
from pydantic import BaseModel
import uuid


router = APIRouter()

tokens = {}


class RegisterInput(BaseModel):
    username: str
    password: str
    mail: str
    year_of_birth: int


class RegisterOutput(BaseModel):
    username: str
    mail: str
    year_of_birth: int


@router.post("/register")
async def register_post(input: RegisterInput = Body()) -> dict[str, RegisterOutput]:
    register_controller = RegisterControllers.carlemany()
    try:
        user = await register_controller(
            username=input.username,
            password=input.password,
            mail=input.mail,
            year_of_birth=input.year_of_birth,
        )
    except UsernameAlreadyTakenException:
        raise HTTPException(status_code=409, detail="This username is already taken")

    output = RegisterOutput(
        username=user.username, mail=user.mail, year_of_birth=user.year_of_birth
    )
    return {"new_user": output}


class LoginInput(BaseModel):
    username: str
    password: str


@router.post("/login")
async def login(input: LoginInput = Body()) -> dict[str, str]:
    login_controller = LoginControllers.carlemany()
    try:
        token = await login_controller(username=input.username, password=input.password)
        return {"auth": token}
    except WrongPasswordException:
        raise HTTPException(status_code=403, detail="Password is not correct")
    except UserNotFoundException:
        raise HTTPException(status_code=404, detail="User not found")


class IntrospectOutput(BaseModel):
    username: str
    mail: str
    year_of_birth: int


# @router.get("/introspect")
# async def introspect_get(auth: str = Header()) -> IntrospectOutput:
#     if auth not in tokens:
#         raise HTTPException(status_code=403, detail="Forbidden")
#     current_username = tokens[auth]
#     user = users[current_username]
#     return IntrospectOutput(
#         username=user.username, mail=user.mail, year_of_birth=user.year_of_birth
#     )


@router.post("/logout")
async def logout(auth: str = Header()) -> dict[str, str]:
    if auth not in tokens:
        raise HTTPException(status_code=403, detail="Invalid or expired session token")
    del tokens[auth]
    return {"status": "You have logged out"}
