import functools
import json

from tortoise import Model, fields
from tortoise.fields.data import JsonDumpsFunc, JsonLoadsFunc

JSON_DUMPS: JsonDumpsFunc = functools.partial(json.dumps, separators=(",", ":"))
JSON_LOADS: JsonLoadsFunc = json.loads


class Checkpoint(Model):
    id = fields.IntField(pk=True)
    pipeline_id = fields.CharField(max_length=60, unique=True)
    block_number = fields.BigIntField()
    context = fields.JSONField(encoder=JSON_DUMPS, decoder=JSON_LOADS)
