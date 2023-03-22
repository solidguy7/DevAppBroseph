from sqlalchemy.future import select
from .connection import get_session

class Database:
    def __init__(self, model) -> None:
        self.model = model

    async def create(self):
        get_session().add(self.model)
        await get_session().commit()
        return self

    async def get(self, param):
        await get_session().get(entity=self.model, ident=param)
        return self

    async def get_all(self):
        result = await get_session().execute(select(self.model))
        return result.scalars().all()

    async def delete(self):
        await get_session().delete(self.model)
        await get_session().commit()
        return self