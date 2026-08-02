"""Demo."""

import asyncio
import cmd
import functools
import inspect
import logging
from collections.abc import Callable, Coroutine
from typing import Any

import aiopulse

logging.basicConfig()
_LOGGER = logging.getLogger("aiopulse.hub")


async def discover(prompt: "HubPrompt") -> None:
    """Task to discover all hubs on the local network."""
    print("Starting hub discovery")
    async for hub in aiopulse.Hub.discover():
        if hub.id not in prompt.hubs:
            prompt.add_hub(hub)


class HubPrompt(cmd.Cmd):
    """Prompt command line class based on cmd."""

    def __init__(self, event_loop: asyncio.AbstractEventLoop) -> None:
        """Init command interface."""
        self.hubs: dict[str, aiopulse.Hub] = {}
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
    ) -> asyncio.Future[Any] | None:
        """Add a job from within the event loop.

        This method must be run in the event loop.

        target: target to call.
        args: parameters for method to call.
        """
        task: asyncio.Future[Any] | None = None

        # Check for partials to properly determine if coroutine function
        check_target = target
        while isinstance(check_target, functools.partial):
            check_target = check_target.func

        if asyncio.iscoroutine(check_target):
            # target is already a coroutine object
            coro: Coroutine[Any, Any, Any] = target  # type: ignore[assignment]
            task = self.event_loop.create_task(coro)
        elif inspect.iscoroutinefunction(check_target):
            # target is a coroutine function, call it to get coroutine object
            coro = target(*args)  # type: ignore[assignment]
            task = self.event_loop.create_task(coro)
        else:
            # target is a regular function, run it in executor
            task = self.event_loop.run_in_executor(None, target, *args)

        return task

    def add_hub(self, hub: aiopulse.Hub) -> None:
        """Add a hub to the prompt."""
        if hub.id:
            self.hubs[hub.id] = hub
        hub.callback_subscribe(self.hub_update_callback)  # type: ignore[arg-type]
        print("Hub added to prompt")

    async def hub_update_callback(self, update_type: Any) -> None:
        """Called when a hub reports that its information is updated."""
        print(f"Hub {update_type.name} updated")

    def _get_roller(self, args: list[str]) -> aiopulse.Roller | None:
        """Return roller based on string argument."""
        try:
            hub_id = int(args[0]) - 1
            roller_id = int(args[1]) - 1
            return list(list(self.hubs.values())[hub_id].rollers.values())[roller_id]
        except Exception:
            print(f"Invalid arguments {args}")
            return None

    def default(self, line: str) -> None:
        """Handle unknown commands, including EOF."""
        if line == "EOF":
            print("Exiting")
            self.running = False
            return
        super().default(line)

    def do_discover(self, args: str) -> None:
        """Command to discover all hubs on the local network."""
        self.add_job(discover, self)

    def do_addhub(self, args: str) -> None:
        """Command to manually add a hub by IP address."""
        ip = args.strip()
        if not ip:
            print("Usage: addhub <ip address>")
            return
        self.add_job(self._add_hub, ip)

    async def _add_hub(self, ip: str) -> None:
        """Add a hub by IP address (runs in event loop)."""
        hub = aiopulse.Hub(ip)
        self.add_hub(hub)
        print(f"Hub at {ip} added")

    def do_update(self, args: str) -> None:
        """Command to ask all hubs to send their information."""
        for hub in self.hubs.values():
            print(f"Sending update command to hub {hub.id}")
            self.add_job(hub.update)

    def do_list(self, args: str) -> None:
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

    def do_moveto(self, sargs: str) -> None:
        """Command to tell a roller to move a % closed."""
        print("Sending move to")
        args = sargs.split()
        roller = self._get_roller(args)
        if roller:
            position = int(args[2])
            print(f"Sending blind move to {roller.name}")
            self.add_job(roller.move_to, position)

    def do_close(self, sargs: str) -> None:
        """Command to close a roller."""
        args = sargs.split()
        roller = self._get_roller(args)
        if roller:
            print(f"Sending blind down to {roller.name}")
            self.add_job(roller.move_down)

    def do_open(self, sargs: str) -> None:
        """Command to open a roller."""
        args = sargs.split()
        roller = self._get_roller(args)
        if roller:
            print(f"Sending blind up to {roller.name}")
            self.add_job(roller.move_up)

    def do_stop(self, sargs: str) -> None:
        """Command to stop a moving roller."""
        args = sargs.split()
        roller = self._get_roller(args)
        if roller:
            print(f"Sending blind stop to {roller.name}")
            self.add_job(roller.move_stop)

    def do_health(self, sargs: str) -> None:
        """Command to get health of a roller."""
        args = sargs.split()
        roller = self._get_roller(args)
        if roller:
            print(f"Sending get health to {roller.name}")
            self.add_job(roller.get_health)

    def do_connect(self, sargs: str) -> None:
        """Command to connect all hubs."""
        for hub in self.hubs.values():
            self.add_job(hub.run)

    def do_disconnect(self, sargs: str) -> None:
        """Command to disconnect all connected hubs."""
        for hub in self.hubs.values():
            self.add_job(hub.stop)

    def do_log(self, sargs: str) -> None:
        """Change logging level."""
        if sargs == "critical":
            _LOGGER.setLevel(logging.CRITICAL)
            print("Log level set to critical")
        elif sargs == "error":
            _LOGGER.setLevel(logging.ERROR)
            print("Log level set to error")
        elif sargs == "warning":
            _LOGGER.setLevel(logging.WARNING)
            print("Log level set to warning")
        elif sargs == "info":
            _LOGGER.setLevel(logging.INFO)
            print("Log level set to info")
        elif sargs == "debug":
            _LOGGER.setLevel(logging.DEBUG)
            print("Log level set to debug")
        else:
            print("Valid log levels are critical, error, warning, info, and debug.")

    def do_exit(self, arg: str) -> bool:
        """Command to exit."""
        print("Exiting")
        self.running = False
        return True

    def cmdloop(self, intro: str | None = None) -> None:
        """Override cmdloop to handle Ctrl+C and EOF."""
        try:
            super().cmdloop(intro)
        except KeyboardInterrupt:
            print("\nExiting")
            self.running = False
        except EOFError:
            print("\nExiting")
            self.running = False
            return


async def main() -> None:
    """Test code."""
    event_loop = asyncio.get_running_loop()

    prompt = HubPrompt(event_loop)
    prompt.prompt = "> "

    task = event_loop.run_in_executor(None, prompt.cmdloop)

    try:
        await task
    except asyncio.CancelledError:
        pass

    print("Program exited cleanly")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
