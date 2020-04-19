"""Demo."""
import asyncio
import cmd
import logging

import aiopulse
import functools

from typing import (
    Any,
    Callable,
    Optional,
)

from aiopulse import _LOGGER

_LOGGER.setLevel(logging.DEBUG)


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

    def add_job(self, target: Callable[..., Any], *args: Any) -> None:
        """Add job to the executor pool.

        target: target to call.
        args: parameters for method to call.
        """
        if target is None:
            raise ValueError("Don't call add_job with None")
        self.event_loop.call_soon_threadsafe(self.async_add_job, target, *args)

    def async_add_job(
        self, target: Callable[..., Any], *args: Any
    ) -> Optional[asyncio.Future]:
        """Add a job from within the event loop.

        This method must be run in the event loop.

        target: target to call.
        args: parameters for method to call.
        """
        task = None

        # Check for partials to properly determine if coroutine function
        check_target = target
        while isinstance(check_target, functools.partial):
            check_target = check_target.func

        if asyncio.iscoroutine(check_target):
            task = self.event_loop.create_task(target)  # type: ignore
        elif asyncio.iscoroutinefunction(check_target):
            task = self.event_loop.create_task(target(*args))
        else:
            task = self.event_loop.run_in_executor(  # type: ignore
                None, target, *args
            )

        return task

    def add_hub(self, hub):
        """Add a hub to the prompt."""
        self.hubs[hub.id] = hub
        hub.callback_subscribe(self.hub_update_callback)
        print("Hub added to prompt")

    def hub_update_callback(self):
        """Called when a hub reports that its information is updated."""
        print("Hub updated")

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
        self.add_job(discover, self)

    def do_update(self, args):
        """Command to ask all hubs to send their information."""
        for hub in self.hubs.values():
            print("Sending update command to hub {}".format(hub.id))
            self.add_job(hub.update)

    def do_list(self, args):
        """Command to list all hubs, rollers, rooms, and scenes."""
        print("Listing hubs...")
        hub_id = 0
        for hub in self.hubs.values():
            hub_id += 1
            print(f"Hub {hub_id}: {hub}")
            roller_id = 0
            for roller in hub.rollers.values():
                roller_id += 1
                print(f"Roller {roller_id}: {roller}")
            room_id = 0
            for room in hub.rooms.values():
                room_id += 1
                print(f"Room {room_id}: {room}")
            scene_id = 0
            for scene in hub.scenes.values():
                scene_id += 1
                print(f"Scene {scene_id}: {scene}")
            timer_id = 0
            for timer in hub.timers.values():
                timer_id += 1
                print(f"Timer {timer_id}: {timer}")

    def do_moveto(self, sargs):
        """Command to tell a roller to move a % closed."""
        print("Sending move to")
        args = sargs.split()
        roller = self._get_roller(args)
        if roller:
            position = int(args[2])
            print("Sending blind move to {}".format(roller.name))
            self.add_job(roller.move_to, position)

    def do_close(self, sargs):
        """Command to close a roller."""
        args = sargs.split()
        roller = self._get_roller(args)
        if roller:
            print("Sending blind down to {}".format(roller.name))
            self.add_job(roller.move_down)

    def do_open(self, sargs):
        """Command to open a roller."""
        args = sargs.split()
        roller = self._get_roller(args)
        if roller:
            print("Sending blind up to {}".format(roller.name))
            self.add_job(roller.move_up)

    def do_stop(self, sargs):
        """Command to stop a moving roller."""
        args = sargs.split()
        roller = self._get_roller(args)
        if roller:
            print("Sending blind stop to {}".format(roller.name))
            self.add_job(roller.move_stop)

    def do_connect(self, sargs):
        """Command to connect all hubs."""
        for hub in self.hubs.values():
            self.add_job(hub.run)

    def do_disconnect(self, sargs):
        """Command to disconnect all connected hubs."""
        for hub in self.hubs.values():
            self.add_job(hub.stop)

    def do_exit(self, arg):
        """Command to exit."""
        print("Exiting")
        self.running = False
        return True


async def main():
    """Test code."""
    logging.basicConfig(level=logging.INFO)

    event_loop = asyncio.get_running_loop()

    prompt = HubPrompt(event_loop)
    prompt.prompt = "> "

    tasks = [
        event_loop.run_in_executor(None, prompt.cmdloop),
    ]

    await asyncio.wait(tasks)


if __name__ == "__main__":
    asyncio.run(main())
