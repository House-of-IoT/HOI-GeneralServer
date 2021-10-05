# How does Auto Scheduling work? 
Auto scheduling is a feature that allows you to pre-schedule actions. This feature is most-helpful when you would like to automatically control devices
without having to manually use a non-bot client to control them. A great example of this would be setting a time for an automated sprinkler system to turn on at
a specific time in the day.

# Auto Scheduling vs Chain controlling

Auto-scheduling is meant to be used by users to pre-schedule actions at different times in the day. Auto-scheduled tasks are executed once at a time in a event loop, this loop is the same loop that the main server tasks are on too which makes auto scheduling great for tasks that aren't high priority.

Chain controlling is a way that you can utilize passive data that is gathered from one device to control another. 
Example of chain controlling
