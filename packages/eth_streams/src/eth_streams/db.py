from importlib.util import find_spec
from typing import Optional

from tortoise import Tortoise


async def init_db(
    load_schema: bool = False,
    db_url: str = "sqlite://db.sqlite3",
    modules: Optional[list[str]] = None,
):
    if not modules:
        spec = find_spec("__main__")
        if spec:
            modules = [spec.name.replace("__main__", "models")]
        else:
            modules = []

    await Tortoise.init(
        db_url=db_url,
        modules={
            "models": [
                "eth_streams.models",
                *modules,
            ],
        },
    )
    if load_schema:
        await Tortoise.generate_schemas()
