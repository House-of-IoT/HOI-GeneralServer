# Core Supported Non-bot Clients
* [Web](https://github.com/House-of-IoT/HOI-GeneralServer)
* [Mobile](https://github.com/House-of-IoT/HOI-MobileClient)
* [Command Line Interface](https://github.com/House-of-IoT/HOI-CLI)
  * Mainly used for raw data analyzation
  * Super Administrative tool

# How to create a custom non-bot client?

You could use the [test_web_client](https://github.com/House-of-IoT/HOI-GeneralServer/blob/master/TestClients/test_web_client.py)
as an example to construct a client, it is built to be simple to modify and copy.

All clients (bots and non-bots) follow this protocol for authentication:

1.Connect to the websocket address that your server is hosted at.
2.Send user password(which is all the same for all users by server design, check [here](https://github.com/House-of-IoT/HOI-GeneralServer/blob/master/Docs/ArchitecturalDesign.MD) for more info on how authentication works).
3.Send name and type(json serialization: {name:[insert name], type : [insert type]})
4.Send outside server name(what the client names the server ,for server's records and action tracking)



