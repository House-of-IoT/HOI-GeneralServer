
"""
Note: SQL Injection isn't a concern due to the nature of HOI.
1.Once someone has access to the general server, they can access all data
    so there is no restricted data to be accessed.
    The only people connected to the server should be trusted members of the server.
"""

class Queries:

    #stores all notifications
    create_notification_table = '''
        CREATE TABLE IF NOT EXISTS notifications(
            Id INTEGER PRIMARY KEY,
            Name VARCHAR(20) NOT NULL,
            Description text NOT NULL,
            Date TIMESTAMP
        );
    '''

    #stores all contacts
    create_contacts_table = """
        CREATE TABLE IF NOT EXISTS contacts(
            Id INTEGER PRIMARY KEY,
            Name VARCHAR(20) NOT NULL,
            Number VARCHAR 20 NOT NULL
        );
    """

    #stores every action execution
    create_action_execution_history = """
        CREATE TABLE IF NOT EXISTS actions(
            Id INTEGER PRIMARY KEY,
            Executor VARCHAR(20) NOT NULL,
            Action VARCHAR(50) NOT NULL,
            BotName VARCHAR(50) NOT NULL,
            Type VARCHAR(50) NOT NULL,
            Date TIMESTAMP
        );
    
    """

    #stores connection history
    create_connection_history = """
        CREATE TABLE IF NOT EXISTS connections(
            Id INTEGER PRIMARY KEY,
            Name VARCHAR(50) NOT NULL,
            Type VARCHAR(50) NOT NULL,
            Date TIMESTAMP
        );
    
    """

    #stores banned Ips 
    create_banned_history = """
        CREATE TABLE IF NOT EXISTS banned(
            Id INTEGER PRIMARY KEY,
            Ip VARCHAR(30) NOT NULL
        );
    
    """

      #insertion
    @staticmethod
    def insert_notification():
        pass
    @staticmethod
    def insert_action_execution():
        pass
    @staticmethod
    def insert_contact():
        pass
    @staticmethod
    def insert_banned_ip():
        pass
    @staticmethod
    def insert_connection():
        pass

    #deletion
    @staticmethod
    def delete_notification():
        pass
    @staticmethod
    def delete_action_execution():
        pass
    @staticmethod
    def delete_connection_history():
        pass
    @staticmethod
    def delete_contact():
        pass    
    @staticmethod
    def delete_banned_ip():
        pass