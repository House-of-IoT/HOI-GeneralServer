# Testing
The "Testing Infastructure" for the GeneralServer is composed of integration tests and unit tests.

## Unit tests
Around the codebase you will find that each testable unit has a test file called `tests.py` these are for the specific unit.

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
  
  
