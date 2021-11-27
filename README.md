# Aiopulse

## Asynchronous library to control Rollease Acmeda Automate roller blinds via a version 1 Pulse Hub.

The Rollease Acmeda Pulse Hub is a WiFi hub that communicates with Rollease Acmeda Automate roller blinds via a proprietary RF protocol.
This module communicates over a local area network using a propriatery binary protocol to issues commands to the Pulse Hub.
A module that supports version 2 Pulse Hubs has been developed separately here: https://pypi.org/project/aiopulse2/
This module requires Python 3.4 or newer and uses asyncio.

### Installing
Available on PyPi here:https://pypi.org/project/aiopulse/, run `pip install aiopulse`. 
Alternatively, download and extract a release and from within the folder containing setup.py run `python setup.py install`.

### Demo.py commands:
| Command                               | Description               |
|---------------------------------------|---------------------------|
|discover                               | Find and connect to any hubs on the local network (uses udp broadcast discovery)|
|connect                                | Connect to all hubs and trigger update|
|disconnect                             | Disconnect all hubs|
|update                                 | Refresh all information from hub|
|list                                   | List currently connected hubs and their blinds, use to get the [hub id] and [blind id] for the following commands.|
|open [hub id] [blind id]               | Open blind|
|close [hub id] [blind id]              | Close blind|
|stop [hub id] [blind id]               | Stop blind|
|moveto [hub id] [blind id] [% closed]  | Open blind to percentage|
|health [hub id] [blind id]             | Update the health of the blind|
|exit                                   | Exit program|
