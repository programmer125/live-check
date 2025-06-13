# -*- coding: utf-8 -*-
# @Author : duyuxuan
# @Time : 2024/10/22 22:26
# @File : role_crud.py
from models.role_model import Role
from crud.base_crud import CRUDBase


class CRUDRole(CRUDBase[Role]):
    pass


role = CRUDRole(Role)


if __name__ == "__main__":
    # res = role.bulk_create(
    #     data_list=[{"name": "name1"}, {"name": "name2"}, {"name": "name3"}],
    # )
    # print(res)
    # res = role.create(data={"name": "test"})
    # print(res)

    # res = role.delete_by_id(record_id=1)
    # print(res)
    # res = role.delete_by_ids(list_ids=[2, 3])
    # print(res)
    # res = role.delete_by_condition(wheres=[Role.name.like("%2%")], sort_id=0)
    # print(res)

    # res = role.update_by_id(record_id=5, data={"name": "123"})
    # print(res)
    # res = role.update_by_condition(
    #     data={"name": "123"},
    #     wheres=[Role.id > 3],
    #     sort_id=0,
    # )
    # print(res)

    # res = role.get_by_id(record_id=4)
    # print(res)
    # res = role.get_by_ids(list_ids=[4, 5])
    # print(res)
    # res = role.get_count(wheres=[Role.id > 18], sort_id=0)
    # print(res)
    # res = role.fetch_one(
    #     fields=["id", "name"],
    #     wheres=[Role.id > 5],
    #     sorts=[("id", "asc"), ("name", "desc")],
    #     sort_id=0,
    # )
    # print(res)
    # res = role.fetch_all(
    #     wheres=[Role.id > 4],
    #     sorts=[("id", "asc"), ("name", "desc")],
    #     sort_id=0,
    # )
    # print(res)

    pass
