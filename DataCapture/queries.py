
"""
Note: SQL Injection isn't a concern due to the nature of HOI.
1.Once someone has access to the general server, they can access all data
    so there is no restricted data to be accessed.
    The only people connected to the server should be trusted members of the server.

    Anyone malicious connected to the server will have some form of control of the devices,
    which is a larger issue than accessing historic data.
"""

#SQLite
class PostgresQueries:
    #stores all notifications
    create_notification_table = '''
        CREATE TABLE IF NOT EXISTS notifications(
            Id INTEGER PRIMARY KEY,
            Name VARCHAR(20) NOT NULL,
            Description text NOT NULL,
            Datetime_saved TIMESTAMP
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
            Datetime_executed TIMESTAMP
        );
    
    """

    #stores connection history
    create_connection_history = """
        CREATE TABLE IF NOT EXISTS connections(
            Id INTEGER PRIMARY KEY,
            Name VARCHAR(50) NOT NULL,
            Type VARCHAR(50) NOT NULL,
            Datetime_connected TIMESTAMP
        );
    
    """

    #stores banned Ips 
    create_banned_history = """
        CREATE TABLE IF NOT EXISTS banned(
            Id INTEGER PRIMARY KEY,
            Ip VARCHAR(30) NOT NULL
        );
    """

    #insertions
    insert_notification = """
        INSERT INTO notifications (Name,Description,Datetime_saved) VALUES (?,?,?)
    """

    insert_contact = """
        INSERT INTO contacts (Name,Number) VALUES (?,?)
    """

    insert_action_execution = """
        INSERT INTO actions (Executor,Action,BotName,Type,Datetime_executed) VALUES (?,?,?,?,?)
    """

    insert_connection = """
        INSERT INTO connections (Name,Type,Datetime_connected) VALUES (?,?,?)
    """

    insert_banned = """
        INSERT INTO banned (Ip) VALUES (?)
    """

    @staticmethod
    def single_parameter_delete_query(table_name,parameter):
        Query = f""" DELETE FROM {table_name} WHERE {parameter} = ? """
        return Query

    @staticmethod
    def select_query(table_name):
        Query = f"""SELECT * FROM {table_name}"""
        return Query
        
    @staticmethod 
    def remove_expired_history_query(table_name, parameter):
        Query = f""" DELETE FROM {table_name} where {parameter}  <= ?"""

