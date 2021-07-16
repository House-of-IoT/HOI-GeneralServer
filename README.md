# HOI-GeneralServer
The general server for all HOI projects. Projects that need special protocols won't use this server.

# Architecture

The general server sits between all smart devices connected(bots) and visual clients(non-bots).
The visual clients are the connections made through the HOI-WebClient and the HOI-MobileClient.

## Control

The visual clients aka non-bots are the only devices that can dictate the state of connections on the 
server; Based on the configuration of the server, the visual clients may or may not be required
to be an administrator to force disconnect another connection. There is an option to control the 
configuration of the general server on the UI but will always require administrator authentication.

# Custom Clients?
//Provide steps for communicating as a client for engineers

