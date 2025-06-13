# -*- coding: utf-8 -*-
# @Author : duyuxuan
# @Time : 2024/12/30 13:32
# @File : base_crud.py
from datetime import datetime
from typing import Any, Generic, TypeVar, Sequence, List, Dict, Tuple, Type

from sqlalchemy.orm import Session
from sqlalchemy.orm import load_only
from sqlalchemy import delete, func, asc, desc
from sqlalchemy import select, update, insert

from models.base_model import BaseModel as Base
from db.session import SessionLocal


ModelType = TypeVar("ModelType", bound=Base)


class CRUDBase(Generic[ModelType]):
    def __init__(self, model: type[ModelType]):
        self.model = model

    def get_session(self):
        return SessionLocal()

    def as_dict(self, obj, fields=None):
        if not fields:
            fields = [column.name for column in obj.__table__.columns]

        get_key_value = (
            lambda c: (c, getattr(obj, c).strftime("%Y-%m-%d %H:%M:%S"))
            if isinstance(getattr(obj, c), datetime)
            else (c, getattr(obj, c))
        )
        return dict(map(get_key_value, fields))

    def as_json(self, response, fields=None):
        return [self.as_dict(elm, fields) for elm in response.scalars().all()]

    def create(
        self,
        *,
        data: Dict,
        model_type: Type[ModelType] | None = None,
        db_session: Session | None = None,
    ) -> Dict:
        if not data:
            raise Exception("data can not be none")

        model_type = model_type or self.model
        db_session = db_session or self.get_session()

        result = self.bulk_create(
            data_list=[data], model_type=model_type, db_session=db_session
        )

        return result[0]

    def bulk_create(
        self,
        *,
        data_list: List[Dict],
        model_type: Type[ModelType] | None = None,
        db_session: Session | None = None,
    ) -> List[Dict]:
        if not data_list:
            raise Exception("data_list can not be none")

        model_type = model_type or self.model
        db_session = db_session or self.get_session()

        with db_session.begin():
            response = db_session.execute(
                insert(model_type).values(data_list).returning(model_type)
            )
            result = self.as_json(response)

        return result

    def delete_by_id(
        self,
        *,
        record_id: int | str,
        model_type: Type[ModelType] | None = None,
        db_session: Session | None = None,
    ) -> bool:
        if not record_id:
            raise Exception("record_id can not be none")

        model_type = model_type or self.model
        db_session = db_session or self.get_session()

        with db_session.begin():
            response = db_session.execute(
                delete(model_type).where(model_type.id == record_id)
            )
            if response.rowcount != 0:
                result = True
            else:
                result = False

        return result

    def delete_by_ids(
        self,
        *,
        list_ids: List[int | str],
        model_type: Type[ModelType] | None = None,
        db_session: Session | None = None,
    ) -> int:
        if not list_ids:
            raise Exception("list_ids can not be none")

        model_type = model_type or self.model
        db_session = db_session or self.get_session()

        with db_session.begin():
            response = db_session.execute(
                delete(model_type).where(model_type.id.in_(list_ids))
            )
            if response.rowcount != 0:
                result = True
            else:
                result = False

        return result

    def delete_by_condition(
        self,
        *,
        model_type: Type[ModelType] | None = None,
        db_session: Session | None = None,
        wheres: List[Any] = None,
        **filters,
    ) -> bool:
        model_type = model_type or self.model
        db_session = db_session or self.get_session()

        if wheres is None:
            wheres = []

        with db_session.begin():
            response = db_session.execute(
                delete(model_type).where(*wheres).filter_by(**filters),
                execution_options={"synchronize_session": False},
            )
            if response.rowcount != 0:
                result = True
            else:
                result = False

        return result

    def update_by_id(
        self,
        *,
        record_id: int | str,
        data: Dict,
        model_type: Type[ModelType] | None = None,
        db_session: Session | None = None,
    ) -> Dict | None:
        if not record_id or not data:
            raise Exception("record_id and data can not be none")

        model_type = model_type or self.model
        db_session = db_session or self.get_session()

        with db_session.begin():
            response = db_session.execute(
                update(model_type)
                .where(model_type.id == record_id)
                .values(**data)
                .returning(model_type)
            )
            result = self.as_json(response)

        if not result:
            return None
        else:
            return result[0]

    def update_by_condition(
        self,
        *,
        data: Dict,
        model_type: Type[ModelType] | None = None,
        db_session: Session | None = None,
        wheres: List[Any] = None,
        **filters,
    ) -> int:
        if not data:
            raise Exception("data can not be none")

        model_type = model_type or self.model
        db_session = db_session or self.get_session()

        if wheres is None:
            wheres = []

        with db_session.begin():
            response = db_session.execute(
                update(model_type).where(*wheres).filter_by(**filters).values(**data),
                execution_options={"synchronize_session": False},
            )
            if response.rowcount != 0:
                result = True
            else:
                result = False

        return result

    def get_by_id(
        self,
        *,
        record_id: int | str,
        model_type: Type[ModelType] | None = None,
        db_session: Session | None = None,
    ) -> Dict | None:
        if not record_id:
            raise Exception("record_id can not be none")

        model_type = model_type or self.model
        db_session = db_session or self.get_session()

        with db_session.begin():
            response = db_session.execute(
                select(model_type).where(model_type.id == record_id)
            )
            result = self.as_json(response)

        if not result:
            return None
        else:
            return result[0]

    def get_by_ids(
        self,
        *,
        list_ids: list[int | str],
        model_type: Type[ModelType] | None = None,
        db_session: Session | None = None,
    ) -> Sequence[Dict] | None:
        if not list_ids:
            raise Exception("list_ids can not be none")

        model_type = model_type or self.model
        db_session = db_session or self.get_session()

        with db_session.begin():
            response = db_session.execute(
                select(model_type).where(model_type.id.in_(list_ids))
            )
            result = self.as_json(response)

        return result

    def get_count(
        self,
        model_type: Type[ModelType] | None = None,
        db_session: Session | None = None,
        wheres: List[Any] = None,
        **filters,
    ) -> int:
        model_type = model_type or self.model
        db_session = db_session or self.get_session()

        if wheres is None:
            wheres = []

        with db_session.begin():
            response = db_session.execute(
                select(func.count())
                .select_from(model_type)
                .where(*wheres)
                .filter_by(**filters)
            )
            result = response.scalar_one()

        return result

    def fetch_one(
        self,
        *,
        model_type: Type[ModelType] | None = None,
        db_session: Session | None = None,
        fields: List[str] = None,
        wheres: List[Any] = None,
        sorts: Tuple[str, str] | List[Tuple[str, str]] = None,
        **filters,
    ):
        model_type = model_type or self.model
        db_session = db_session or self.get_session()

        result = self.fetch_all(
            model_type=model_type,
            db_session=db_session,
            fields=fields,
            wheres=wheres,
            sorts=sorts,
            limit=1,
            **filters,
        )

        if not result:
            return None
        else:
            return result[0]

    def fetch_all(
        self,
        *,
        model_type: Type[ModelType] | None = None,
        db_session: Session | None = None,
        fields: List[str] = None,
        wheres: List[Any] = None,
        limit: int = None,
        offset: int = None,
        sorts: Tuple[str, str] | List[Tuple[str, str]] = None,
        **filters,
    ):
        model_type = model_type or self.model
        db_session = db_session or self.get_session()

        if wheres is None:
            wheres = []

        query = select(model_type)
        if fields:
            attributes = [
                getattr(model_type, field)
                for field in fields
                if hasattr(model_type, field)
            ]
            query = query.options(load_only(*attributes))
        if limit:
            query = query.limit(limit)
        if offset:
            query = query.offset(offset)
        if sorts:
            if isinstance(sorts, Tuple):
                sorts = [sorts]
            for elm in sorts:
                if elm[1] == "asc":
                    query = query.order_by(asc(getattr(model_type.__table__.c, elm[0])))
                else:
                    query = query.order_by(
                        desc(getattr(model_type.__table__.c, elm[0]))
                    )

        with db_session.begin():
            response = db_session.execute(query.where(*wheres).filter_by(**filters))
            result = self.as_json(response, fields=fields)

        return result
