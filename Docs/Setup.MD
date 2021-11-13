# Setup(Needs Improvment with graphics)

To setup a generic GeneralServer you would need to 

1. Navigate to the Config folder and run `python3 config.py` this will prompt you for special information regarding your host/port for hosting the server along 
with other default settings.
2. Move the config.py to the root directory(where main.py exists)
3. Set the following [environmental variables](https://github.com/House-of-IoT/HOI-GeneralServer/blob/master/Docs/ENV.md).
4. Navigate to the root directory(where main.py exists) and run `python3 main.py`



Tired of chasing dependencies?
Run it in a docker container by making use of the dockerfile.

You will need to bind the environmental variables to the runtime.





# Prerequisites

You will need to make sure that you have a twilio account.
