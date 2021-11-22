# Testing
The "Testing Infastructure" for the GeneralServer is composed of integration tests and unit tests.

## Unit tests
Around the codebase you will find that each testable unit has a test file called `tests.py` these are for each specific unit.

## Integration tests
There is one main test that is carried out to gauge the correctness of the GeneralServer, it involves running:

  - One instance of the GeneralServer with the default config values set. Generate a config that matches
  these settings:
  ```JSON
  {"disconnecting": false, 
  "activating": true, 
  "deactivating": false, 
  "viewing": true,
  "host": "localhost", 
  "port": 50223, 
  "using_sql" :TRUE OR FALSE DEPENDING ON WHAT EXACTLY YOU ARE TESTING(database or memory), 
  "device_specific":true}
  ```
  - One instance of the test_bot_client which is located in TestClients
  - One instance of the test_web_client which is located in TestClients
  - [OPTIONAL] One instance of a POSTGRES SQL db, this is optional based on if you are testing the memory mode or the database mode.
  
  

## How do the integration tests gauge the correctness of the GeneralServer?

The GeneralServer has a decent amount of functionality that involves storing things in memory/db and
later retrieving that data from a client. Most of the tests use the server state data to determine 
if the server is behaving as expected after certain requests. 

For example we can determine if adding a contact is working by simply making a request to add a contact
and then making another request to determine if the contact is present in our data storage.

Most of the tests reside in  `TestClients/test_web_client.py`.

## The order in which the instances should be started.
It is important that there is a fresh instance of each for every test.
The database can't have any data associated with it, for this it is best to use a docker image without persisting data.


1. [Optional] Start the Postgres instance if you are testing the server in sql capture mode.
2. Start the GeneralServer with `main.py`.
3. Start the test bot client with `python3 TestClients/test_bot_client.py`
4. Start the test web client with `python3 TestClients/test_web_clients.py`


You should keep an eye on the test_web_client as the main source of testing.
All of these tests should pass.
