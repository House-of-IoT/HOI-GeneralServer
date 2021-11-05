
"""
Note: SQL Injection isn't a concern due to the nature of HOI.
1.Once someone has access to the general server, they can access all data
    so there is no restricted data to be accessed.
    The only people connected to the server should be trusted members of the server.
"""

class Queries:
    create_notification_table = '''
        CREATE TABLE IF NOT EXISTS notifications(
            Id INTEGER PRIMARY KEY,
            Name VARCHAR(20) NOT NULL,
            Description text NOT NULL,
            Date TIMESTAMP
        );
    '''
    #For autoscheduling only
    create_task_execution_history_table = '''
        CREATE TABLE IF NOT EXISTS tasks(
            Id INTEGER PRIMARY KEY,
            BotName VARCHAR(50) NOT NULL,
            Action VARCHAR(50) NOT NULL,
            Date TIMESTAMP
        );
    '''
    
    create_contacts_history = """
        CREATE TABLE IF NOT EXISTS contacts(
            Id INTEGER PRIMARY KEY,
            Name VARCHAR(20) NOT NULL,
            Number VARCHAR 20 NOT NULL
        );
    """

    #for users only
    create_action_execution_history = """
        CREATE TABLE IF NOT EXISTS actions(
            Id INTEGER PRIMARY KEY,
            Executor VARCHAR(20) NOT NULL,
            Action VARCHAR(50) NOT NULL,
            BotName VARCHAR(50) NOT NULL,
            Date TIMESTAMP
        );
    
    """