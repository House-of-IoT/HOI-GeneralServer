# Data Capture

The general server has two different modes for data capture:

1. In Memory
2. Database

Things are stored in memory if the server is configured to run without a database.
Things are stored in a database if the server is configured to run with a database.


There are multiple different options on how to run the server in terms of data capture because
not all server host machines will be able to support a database or some of the systems that require 
a large amount of resources.

For example, there are some people who will decide to use a micro computer for hosting.


## What if my server is configured to run with a database but loses connection?

The current server logic:

If the server can't reconnect after 5 attempts it will enter in memory mode and try to reconnect every
30 minutes.

The server will send a notification to all connected clients and to all cached phone numbers
regarding the connection status right after the in memory mode activation.

## What happens when connection is regained to the database after temporarily being in memory mode?
The server will execute "catch up" which will insert all new records(contacts,action execution etc.) to the database
and the server will not be out of memory mode.


## Why use database mode over in memory mode?

Database mode allows you to store a larger amount of historic data for a long period of time. 
It allows you to have a large amount of contacts and other records for your server.

Some features require a database because they require data storage.

## Why use In memory mode over database mode?

In memory mode allows you to have a light weight system that 
can be hosted on almost any device. 

In memory mode restricts
the amount of historic data being saved in memory, so you
can always still access recent history without paying the cost
for a hosted database.

In memory mode takes one less step for setup.



# Data flow diagram(In Memory)

In memory all data is stored in the "Main" Object aka Parent. 

<img src = "https://github.com/House-of-IoT/HOI-GeneralServer/blob/master/Docs/memorydiagram.png"/>

# Data flow diagram(In DB)

<img src="https://github.com/House-of-IoT/HOI-GeneralServer/blob/master/Docs/indatabase.png"/>
