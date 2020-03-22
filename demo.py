""" Demo """
import logging
import asyncio
import aiopulse
import cmd
import concurrent

async def discover(prompt):
	print("Starting hub discovery")
	async for hub in aiopulse.Hub.discover():
		if hub.id not in prompt.hubs:
			prompt.add_hub(hub)

class HubPrompt(cmd.Cmd):

	def __init__(self, event_loop):
		""" Init command interface """
		self.hubs = {}
		self.event_loop = event_loop
		self.running = True
		super().__init__()

	def add_hub(self, hub):
		self.hubs[hub.id]= hub
		print("Hub added to prompt")

	def _get_roller(self, args):
		try:
			hub_id = int(args[0]) - 1
			roller_id = int(args[1]) - 1
			return list(list(self.hubs.values())[hub_id].rollers.values())[roller_id]
		except:
			print("Invalid arguments {}".format(args))
			return None		

	def do_discover(self, args):
		self.event_loop.create_task(discover(self))

	def do_update(self, args):
		for hub in self.hubs.values():
			print("Sending update command to hub {}".format(hub.id))
			self.event_loop.create_task(hub.update())
			
	def do_list(self, args):
		print("Listing hubs...")
		hid = 1
		for hub in self.hubs.values():
			print("Hub {}: Name: {}".format(hid, hub.id))
			rid = 1
			for roller in hub.rollers.values():
				print("Roller {}: Name: {}".format(rid, roller.name))
				rid += 1

	def do_moveto(self, sargs):
		print("Sending move to")
		args = sargs.split()
		roller = self._get_roller(args)
		if roller:
			position = int(args[2])
			print("Sending blind move to {}".format(roller.name))
			self.event_loop.create_task(roller.move_to(position))
		
	def do_close(self, sargs):
		args = sargs.split()
		roller = self._get_roller(args)
		if roller:
			print("Sending blind down to {}".format(roller.name))
			self.event_loop.create_task(roller.move_down())

	def do_open(self, sargs):
		args = sargs.split()
		roller = self._get_roller(args)
		if roller:
			print("Sending blind up to {}".format(roller.name))
			self.event_loop.create_task(roller.move_up())
	
	def do_stop(self, sargs):
		args = sargs.split()
		roller = self._get_roller(args)
		if roller:
			print("Sending blind stop to {}".format(roller.name))
			self.event_loop.create_task(roller.move_stop())

	def do_connect(self, sargs):
		for hub in self.hubs.values():
			self.event_loop.create_task(hub.run())

	def do_disconnect(self, sargs):
		for hub in self.hubs.values():
			self.event_loop.create_task(hub.stop())

	def do_exit(self, arg):
		print("Exiting")
		self.running = False
		return True

async def worker(prompt):
	while prompt.running:
		await asyncio.sleep(1)

async def main():
	""" test code """
	logging.basicConfig(level=logging.INFO)

	event_loop = asyncio.get_running_loop()

	executor = concurrent.futures.ThreadPoolExecutor()
	event_loop.set_default_executor(executor)

	prompt = HubPrompt(event_loop)
	prompt.prompt = '> '

	tasks = [
		worker(prompt),
		event_loop.run_in_executor(None, prompt.cmdloop),
	]

	await asyncio.wait(tasks)

if __name__ == "__main__":
	asyncio.run(main())

