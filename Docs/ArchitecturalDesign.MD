# Design

## Basic Terminology

`"Non-bots"` - clients that are used for human control over other devices. This is usually devices that connect to the server via WebClient or MobileClient.

`"bots"` - Smart devices that "Non-bots" control.

`"passive data"` - all "bots" usually send passive data to the "non-bots" which is displayed on the client interfaces(if they are "available").

`"available"` - This is either true of false for a "Non-bot".

`"special action"` - streaming or other actions that require back and forth communication.


## Constraints and notable information
1. Only one Non-bot can take control over a bot at a time to execute a "special action". However an unlimited amount of Non-bots can view the passive data of an unlimited amount of bots. For example if there is 100 available bots connected and 1000 non-bots connected, all 1000 non-bots will be recieving passive data from the 100 available bots.

2. Everytime a new device is created that would like to interface with the HOI-GeneralServer, the type and functionality  must be added to the Server.
3. There are no specialized users, there are only `Users,Admins,Super-Admins`. These three categories can be achieved by anyone who connects to the server if they have the passwords for each respective position. There could be an unlimited amount of each position, and each position has permissions regarding control of the server.

## How does a request look?
A request is typically made from non-bots to bots. Here are the simplified steps with the pertaining logic.
Note I will be using "You" as the non-bot and "AutomatedSprinkler" as the bot in this scenario.

So first you would like to turn off the sprinkler.

1. First you would use a client that follows the GeneralServer's Communication protocol like the HOI-GeneralServer.
2. You would connect to the GeneralServer.
3. You would see the AutomatedSprinkler connected and you would use the sprinkler's name to request a bot action from the server, something like "turn-off" by using after sending the initial op-code "bot-control".
4. The server would check to see if the device is connected and if the device is available(see above for the meaning).
5. If the device is connected and available the server will forward the "turn-off" code to the bot(which it understand from its device software implementation).
6. The server will get the response back from the bot and forward the response to the non-bot that made the request. If the response is "success", the sprinklers should have been turned off!

# Final
The HOI-GeneralServer is the connecting point all of the devices in a House of Iot System. All communication goes through the GeneralServer to and from bots/non-bots with enforced permissions by using the Auth system. The server was designed to be easy to deploy and setup. 

There are options to improve scalability and have additional features by configuring the server to run with a database.
