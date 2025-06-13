# -*- coding: utf-8 -*-
# @Author : duyuxuan
# @Time : 2024/10/22 17:39
# @File : session.py
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from configs.settings import settings


engine = create_engine(
    settings.sync_db_uri,
    echo=settings.db_echo,
    pool_size=2,
    max_overflow=10,
    pool_pre_ping=True,
    pool_recycle=3600,
    poolclass=QueuePool,
)

SessionLocal = sessionmaker(bind=engine)


async_engine = create_async_engine(
    settings.async_db_uri,
    echo=settings.db_echo,
    pool_size=2,
    max_overflow=10,
    pool_pre_ping=True,
    pool_recycle=20,
)

AsyncSessionLocal = async_sessionmaker(bind=async_engine)
