from sqlalchemy import Column, String, Integer, select
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy import create_engine

from sqlalchemy.orm import sessionmaker, relationship

Base = declarative_base()


class IndexDb(Base):
    __tablename__ = "indexDb"
    id = Column("id", String, primary_key=True)
    # download status
    download_status = Column(Integer, default=-1)
    transactionId = Column("transactionId", String, index=True)
    page = Column("page", String)
    author = Column("author", String)
    title = Column("title", String)
    tlData = Column("tlData", String)


class DownloadDb(Base):
    __tablename__ = "dwnloads"
    id = Column("id", Integer, primary_key=True)
    path = Column("path", String, default=None)
    download_status = Column(Integer, default=-1)
    title = Column("title", String, index=True)
    chat_id = Column("chat_id", String, index=True)
    message_id = Column("message_id", String, index=True)
    links = Column("files", String, default=None)
    # page = Column("page", String)
    downloads = Column("downloads", String)
    gid = Column("gid", String, index=True)
    # image = Column("image", String)
    # author = Column("author", String)
    status = Column("status", String, default=None, index=True)


engine = create_async_engine(
    f"sqlite+aiosqlite:///./Audioboosk.db", connect_args={"check_same_thread": False}
)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def init_database():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


async def commit():
    async with async_session() as session:
        async with session.begin():
            await session.commit()


async def deleteRow(data):
    async with async_session() as session:
        async with session.begin():
            await session.delete(data)


async def addRow(data):
    async with async_session() as session:
        async with session.begin():
            session.add(data)


async def query(statement, qtype="all"):
    async with async_session() as session:
        result = await session.execute(statement)
        if qtype == "all":
            return result.scalars()
        if qtype == "one":
            return result.scalar()


# Base.metadata.drop_all(engine)
# Base.metadata.create_all(engine)
# print("database is ready")
