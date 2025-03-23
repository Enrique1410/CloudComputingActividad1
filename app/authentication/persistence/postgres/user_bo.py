from app.authentication.domain.bo.user_bo import UserBO
from app.authentication.domain.persistences.exceptions import (
    UserNotFoundException,
    UsernameAlreadyTakenException,
)
from app.authentication.domain.persistences.user_bo_interface import UserBOInterface
from app.authentication.models import UserDB


class UserBOPostgresPersistenceService(UserBOInterface):

    async def create_user(self, user: UserBO):
        if await UserDB.get(username=user.username).exists():
            raise UsernameAlreadyTakenException
        new_user = await UserDB.create(
            username=user.username,
            password=user.password,
            mail=user.mail,
            year_of_birth=user.year_of_birth,
        )
        user.id = new_user.id

    async def get_user(self, username: str):
        user_db = await UserDB.get(username=username)
        if not await user_db.exists():
            raise UserNotFoundException
        return UserBO(
            username=user_db.username,
            password=user_db.password,
            mail=user_db.mail,
            year_of_birth=user_db.year_of_birth,
        )
