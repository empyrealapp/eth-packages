from eth_streams import Stage, Transformer


class SimpleStage(Stage[Transformer]):
    async def actions(self, transformer: Transformer):
        # do nothing
        pass

    async def teardown(self, transformer: Transformer):
        # do nothing
        pass


def test_stage_creation():
    simple_stage = SimpleStage()
    assert simple_stage.name == "SimpleStage"
