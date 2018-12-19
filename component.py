from autobahn.asyncio import wamp

import controller


class BrightnessComponent(wamp.ApplicationSession):
    def __init__(self, config=None):
        super().__init__(config)
        self.controller = controller.BrightnessControl(self)

    async def onJoin(self, details):
        reg = await self.register(self.controller.set_brightness, 'io.crossbar.set_brightness')
        print("registered '{}'".format(reg.procedure))

        reg2 = await self.register(self.controller.get_current_brightness_percentage, 'io.crossbar.get_brightness')
        print("registered '{}'".format(reg2.procedure))
