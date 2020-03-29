"""Demo."""
import asyncio
import cmd
import concurrent
import logging

import aiopulse


async def discover(prompt):
    """Task to discover all hubs on the local network."""
    print("Starting hub discovery")
    async for hub in aiopulse.Hub.discover():
        if hub.id not in prompt.hubs:
            prompt.add_hub(hub)


class HubPrompt(cmd.Cmd):
    """Prompt command line class based on cmd."""

    def __init__(self, event_loop):
        """Init command interface."""
        self.hubs = {}
        self.event_loop = event_loop
        self.running = True
        super().__init__()

    def add_hub(self, hub):
        """Add a hub to the prompt."""
        self.hubs[hub.id] = hub
        print("Hub added to prompt")

    def _get_roller(self, args):
        """Return roller based on string argument."""
        try:
            hub_id = int(args[0]) - 1
            roller_id = int(args[1]) - 1
            return list(list(self.hubs.values())[hub_id].rollers.values())[roller_id]
        except Exception:
            print("Invalid arguments {}".format(args))
            return None

    def do_discover(self, args):
        """Command to discover all hubs on the local network."""
        self.event_loop.create_task(discover(self))

    def do_update(self, args):
        """Command to ask all hubs to send their information."""
        for hub in self.hubs.values():
            print("Sending update command to hub {}".format(hub.id))
            self.event_loop.create_task(hub.update())

    def do_list(self, args):
        """Command to list all hubs, rollers, rooms, and scenes."""
        print("Listing hubs...")
        hid = 1
        for hub in self.hubs.values():
            print("Hub {}: Name: {}".format(hid, hub.id))
            rid = 1
            for roller in hub.rollers.values():
                print("Roller {}: {}".format(rid, roller))
                rid += 1
            for room in hub.rooms.values():
                print("Room {}".format(room))
            for scene in hub.scenes.values():
                print("Scene {}".format(scene))

    def do_moveto(self, sargs):
        """Command to tell a roller to move a % closed."""
        print("Sending move to")
        args = sargs.split()
        roller = self._get_roller(args)
        if roller:
            position = int(args[2])
            print("Sending blind move to {}".format(roller.name))
            self.event_loop.create_task(roller.move_to(position))

    def do_close(self, sargs):
        """Command to close a roller."""
        args = sargs.split()
        roller = self._get_roller(args)
        if roller:
            print("Sending blind down to {}".format(roller.name))
            self.event_loop.create_task(roller.move_down())

    def do_open(self, sargs):
        """Command to open a roller."""
        args = sargs.split()
        roller = self._get_roller(args)
        if roller:
            print("Sending blind up to {}".format(roller.name))
            self.event_loop.create_task(roller.move_up())

    def do_stop(self, sargs):
        """Command to stop a moving roller."""
        args = sargs.split()
        roller = self._get_roller(args)
        if roller:
            print("Sending blind stop to {}".format(roller.name))
            self.event_loop.create_task(roller.move_stop())

    def do_connect(self, sargs):
        """Command to connect all hubs."""
        for hub in self.hubs.values():
            self.event_loop.create_task(hub.run())

    def do_disconnect(self, sargs):
        """Command to disconnect all connected hubs."""
        for hub in self.hubs.values():
            self.event_loop.create_task(hub.stop())

    def do_exit(self, arg):
        """Command to exit."""
        print("Exiting")
        self.running = False
        return True


async def worker(prompt):
    """Async worker thread that sleeps and wakes up periodically."""
    while prompt.running:
        await asyncio.sleep(1)


async def main():
    """Test code."""
    logging.basicConfig(level=logging.INFO)

    event_loop = asyncio.get_running_loop()

    executor = concurrent.futures.ThreadPoolExecutor()
    event_loop.set_default_executor(executor)

    prompt = HubPrompt(event_loop)
    prompt.prompt = "> "

    tasks = [
        worker(prompt),
        event_loop.run_in_executor(None, prompt.cmdloop),
    ]

    await asyncio.wait(tasks)


if __name__ == "__main__":
    asyncio.run(main())
