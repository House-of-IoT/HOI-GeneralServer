
"""
Note: SQL Injection isn't a concern due to the nature of HOI.
1.Once someone has access to the general server, they can access all data
    so there is no restricted data to be accessed.
    The only people connected to the server should be trusted members of the server.

    Anyone malicious connected to the server will have some form of control of the devices,
    which is a larger issue than accessing historic data.
"""

#SQLite
from datetime import datetime

class PostgresQueries:

    #stores all contacts
    create_contacts_table = """
        CREATE TABLE IF NOT EXISTS contacts(
            id SERIAL PRIMARY KEY,
            name VARCHAR(20) NOT NULL,
            number VARCHAR(20) NOT NULL);
    """

    #stores every action execution
    create_action_execution_history = """
        CREATE TABLE IF NOT EXISTS actions(
            Id SERIAL PRIMARY KEY,
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
            Id SERIAL PRIMARY KEY,
            Name VARCHAR(50) NOT NULL,
            Type VARCHAR(50) NOT NULL,
            Datetime_connected TIMESTAMP
        );
    
    """

    #stores banned Ips 
    create_banned_history = """
        CREATE TABLE IF NOT EXISTS banned(
            Id SERIAL PRIMARY KEY,
            Ip VARCHAR(30) NOT NULL
        );
    """

    @staticmethod 
    def insert_contact_query(name,number):
        insert_contact = f"""
            INSERT INTO contacts(name,number) VALUES('{name}','{number}');
            """
        return insert_contact
   
    @staticmethod
    def insert_action_execution_query(executor,action,botname,type_data,Datetime_executed):
        insert_action_execution = f"""
            INSERT INTO actions (Executor,Action,BotName,Type,Datetime_executed) VALUES ('{executor}','{action}','{botname}','{type_data}','{Datetime_executed}');
            """
        return insert_action_execution

    @staticmethod 
    def insert_connection_query(name,type_data,Datetime_connected):
        insert_connection = f"""
        INSERT INTO connections (Name,Type,Datetime_connected) VALUES ('{name}','{type_data}','{Datetime_connected}');
        """
        return insert_connection


    @staticmethod 
    def insert_banned_query(ip):
        banned_query = f"""
            INSERT INTO banned (Ip) VALUES ('{ip}');
        """
        return banned_query

    @staticmethod
    def single_parameter_delete_query(table_name,parameter):
        Query = f""" DELETE FROM {table_name} WHERE {parameter} = ? """
        return Query

    @staticmethod
    def select_query(table_name):
        Query = f"""SELECT * FROM {table_name}"""
        return Query

    @staticmethod 
    def remove_expired_history_query(table_name, parameter,date):
        Query = f""" DELETE FROM {table_name} where {parameter}  <= '{date}' """
        return Query