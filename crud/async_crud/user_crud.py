# -*- coding: utf-8 -*-
# @Author : duyuxuan
# @Time : 2024/10/22 22:26
# @File : user_crud.py
from typing import List, Dict

from sqlalchemy import insert
from sqlalchemy.ext.asyncio import AsyncSession

from models.role_model import Role
from models.user_model import User
from crud.async_crud.base_crud import CRUDBase


class CRUDUser(CRUDBase[User]):
    async def create_with_role(
        self,
        *,
        users: List[Dict],
        roles: List[Dict],
        db_session: AsyncSession | None = None,
    ) -> List[Dict]:
        if not users or not roles:
            raise Exception("users and roles can not be none")

        db_session = db_session or self.db.session

        async with db_session.begin():
            # 插入roles
            role_response = await db_session.execute(
                insert(Role).values(roles).returning(Role)
            )
            roles = self.as_json(role_response)
            role_mappings = {role["name"]: role["id"] for role in roles}

            for user in users:
                user["role_id"] = role_mappings[user["role_name"]]
                del user["role_name"]

            user_response = await db_session.execute(
                insert(self.model).values(users).returning(self.model)
            )
            result = self.as_json(user_response)

        return result


user = CRUDUser(User)


if __name__ == "__main__":
    import asyncio
    from db.session import AsyncSessionLocal

    async def main():
        async with AsyncSessionLocal() as session:
            # roles = [
            #     {"name": "admin"},
            #     {"name": "user"},
            #     {"name": "guest"},
            # ]
            # users = [
            #     {"username": "admin", "phone": "12345678901", "role_name": "admin"},
            #     {"username": "user", "phone": "12345678902", "role_name": "user"},
            # ]
            # res = await user.create_with_role(users=users, roles=roles, db_session=session)
            # print(res)

            res = await user.fetch_all(
                model_type=Role,
                db_session=session,
                wheres=[Role.id > 0],
                sorts=[("id", "asc"), ("name", "desc")],
                sort_id=0,
            )
            print(res)

    asyncio.run(main())
