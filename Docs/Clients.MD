# Core Supported Non-bot Clients
* [Web](https://github.com/House-of-IoT/HOI-GeneralServer)
* [Mobile](https://github.com/House-of-IoT/HOI-MobileClient)
* [Command Line Interface](https://github.com/House-of-IoT/HOI-CLI)
  * Mainly used for raw data analyzation
  * Super Administrative tool

# How to create a custom non-bot client?

You could use the [test_web_client](https://github.com/House-of-IoT/HOI-GeneralServer/blob/master/TestClients/test_web_client.py)
as an example to construct a client, it is built to be simple to modify and copy.

## All clients (bots and non-bots) follow this protocol for authentication:

1.Connect to the websocket address that your server is hosted at.

2.Send user password(which is all the same for all users by server design, check [here](https://github.com/House-of-IoT/HOI-GeneralServer/blob/master/Docs/ArchitecturalDesign.MD) for more info on how authentication works).

3.Send name and type(json serialization: {name:[insert name], type : [insert type]})

4.Send outside server name(what the client names the server ,for server's records and action tracking)



## All clients(non-bots only) follow the following protocols for basic actions: 

Note: Basic actions are activation,deactivation,disconnection of bots and viewing server state.

(Deactivation ,Activation, and disconnection)
1.Send 'bot_control'
2.Send the action that you would like to execute('activate' , 'deactivate', 'disconnect')
3.Send the name of the bot you are trying to control.
4.Gather response that will be in JSON formatt({server_name : "" ,action : "" ,status: "" ,bot_name: "",target: "",target_value: ""}).
  * if you get a status of "success" then no more follow up is required
  * if you get a status of "needs-admin-auth"  the client will need to provide the admin password for authentication'
  * if you get a status of "timeout" , this means the targeted bot failed to respond to the request in a timely fashion.

(viewing server state)
1.Send the correct opcode(For example, you would send "servers_banned_ips" if you would like to view the ip addresses that are currently banned)
2.Gather response that will be in JSON formatt({server_name : "" ,action : "" ,status: "" ,bot_name: "",target: "",target_value: ""}
  * if you get a status of "success" then no more follow up is required and the data will be located in target_value
  * if you get a status of "needs-admin-auth"  the client will need to provide the admin password for authentication'
  * if you get a status of "timeout" , this means the client failed to respond to the request in a timely fashion.

