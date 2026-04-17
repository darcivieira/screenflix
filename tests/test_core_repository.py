from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from screenflix.core.database import Base
from screenflix.core.repository import BaseRepository


class SampleModel(Base):
    __tablename__ = "sample_model_test"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50))
    rating: Mapped[int] = mapped_column(Integer)


class FakeScalarResult:
    def __init__(self, items):
        self._items = items

    def all(self):
        return self._items


class FakeExecuteResult:
    def __init__(self, items=None, scalar_value=None):
        self._items = items if items is not None else []
        self._scalar_value = scalar_value

    def scalars(self):
        return FakeScalarResult(self._items)

    def scalar(self):
        return self._scalar_value


class FakeSession:
    def __init__(self, execute_result):
        self.execute_result = execute_result
        self.last_query = None
        self.added = []
        self.deleted = []
        self.get_calls = []

    async def get(self, model, entity_id):
        self.get_calls.append((model, entity_id))
        return {"id": entity_id}

    async def execute(self, query):
        self.last_query = query
        return self.execute_result

    def add(self, entity):
        self.added.append(entity)

    async def delete(self, entity):
        self.deleted.append(entity)


async def test_base_repository_get_by_id():
    session = FakeSession(FakeExecuteResult())
    repo = BaseRepository(session, SampleModel)

    result = await repo.get_by_id(7)

    assert result == {"id": 7}
    assert session.get_calls == [(SampleModel, 7)]


async def test_base_repository_list_all_with_filters_and_order():
    session = FakeSession(FakeExecuteResult(items=[1, 2]))
    repo = BaseRepository(session, SampleModel)

    result = await repo.list_all(skip=5, limit=10, order_by="rating", desc=True, name="Neo", unknown="x")

    assert result == [1, 2]
    query_text = str(session.last_query)
    assert "WHERE" in query_text
    assert "sample_model_test.name" in query_text
    assert "ORDER BY sample_model_test.rating DESC" in query_text
    assert "LIMIT" in query_text
    assert "OFFSET" in query_text


async def test_base_repository_count_returns_zero_when_none():
    session = FakeSession(FakeExecuteResult(scalar_value=None))
    repo = BaseRepository(session, SampleModel)

    result = await repo.count(name="Neo")

    assert result == 0
    assert "count" in str(session.last_query).lower()


async def test_base_repository_add_and_delete():
    session = FakeSession(FakeExecuteResult())
    repo = BaseRepository(session, SampleModel)
    entity = {"id": 1}

    repo.add(entity)
    await repo.delete(entity)

    assert session.added == [entity]
    assert session.deleted == [entity]
