# -*- coding: utf-8 -*-
# @Author : duyuxuan
# @Time : 2024/10/22 22:26
# @File : role_crud.py
from models.role_model import Role
from crud.async_crud.base_crud import CRUDBase


class CRUDRole(CRUDBase[Role]):
    pass


role = CRUDRole(Role)


if __name__ == "__main__":
    import asyncio
    from db.session import AsyncSessionLocal

    async def main():
        async with AsyncSessionLocal() as session:
            # res = await role.bulk_create(
            #     data_list=[{"name": "name1"}, {"name": "name2"}, {"name": "name3"}],
            #     db_session=session,
            # )
            # print(res)
            # res = await role.create(data={"name": "test"}, db_session=session)
            # print(res)

            # res = await role.delete_by_id(record_id=1, db_session=session)
            # print(res)
            # res = await role.delete_by_ids(list_ids=[2, 13], db_session=session)
            # print(res)
            # res = await role.delete_by_condition(
            #     db_session=session, wheres=[Role.name.like("%2%")], sort_id=2
            # )
            # print(res)

            # res = await role.update_by_id(
            #     record_id=15, data={"name": "123"}, db_session=session
            # )
            # print(res)
            # res = await role.update_by_condition(
            #     data={"name": "123"},
            #     db_session=session,
            #     wheres=[Role.id > 3],
            #     sort_id=0,
            # )
            # print(res)

            # res = await role.get_by_id(record_id=5, db_session=session)
            # print(res)
            # res = await role.get_by_ids(list_ids=[10, 2], db_session=session)
            # print(res)
            # res = await role.get_count(db_session=session, wheres=[Role.id > 18], sort_id=0)
            # print(res)
            # res = await role.fetch_one(
            #     db_session=session,
            #     fields=["id", "name"],
            #     wheres=[Role.id > 5],
            #     sorts=[("id", "asc"), ("name", "desc")],
            #     sort_id=0,
            # )
            # print(res)
            res = await role.fetch_all(
                db_session=session,
                wheres=[Role.id > 9],
                sorts=[("id", "asc"), ("name", "desc")],
                sort_id=0,
            )
            print(res)

    asyncio.run(main())
