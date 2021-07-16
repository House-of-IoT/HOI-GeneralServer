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

# Alerts

The alerts are controlled directly by the general server on arrival of data from the smart devices connected.
Dispatch alerts are sent as text messages by using a twilio account, which removes the need for push notifications
but unfortunately requires a twilio account/number. Real-time alerts are dispatched to all connected non-bot clients
and based on the client(if it isn't custom) there will be an alerting sound. By default both "Dispatch" and "Real-time" alerts 
are enabled per config settings.

# Custom Clients?
//Provide steps for communicating as a client for engineers


