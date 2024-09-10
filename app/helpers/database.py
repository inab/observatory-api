import configparser
from pymongo import MongoClient
import os


def connect_DB():
    # connecting to db
    config = configparser.ConfigParser()
    # read the env variable CONFIG_FILE
    config_path = os.getenv('CONFIG_PATH')

    if config_path:
        # Read the config file from the path defined in CONFIG_PATH
        config.read(config_path)
    else:
        raise EnvironmentError("CONFIG_PATH environment variable is not set.")
        
    mongo_host = config['MONGO_DETAILS']['DBHOST']
    mongo_port = config['MONGO_DETAILS']['DBPORT']
    mongo_user = config['MONGO_DETAILS']['DBUSER']
    mongo_pass = config['MONGO_DETAILS']['DBPASS']
    mongo_auth_src = config['MONGO_DETAILS']['DBAUTHSRC']
    mongo_db = config['MONGO_DETAILS']['DATABASE']
    stats_collection_name = config['MONGO_DETAILS']['STATS']
    tools_collection_name = config['MONGO_DETAILS']['TOOLS']

    client = MongoClient(
                host=[f'{mongo_host}:{mongo_port}'],
                username=mongo_user,
                password=mongo_pass,
                authSource=mongo_auth_src,
                authMechanism='SCRAM-SHA-256'
            )
    
    tools_collection = client[mongo_db][tools_collection_name]
    stats = client[mongo_db][stats_collection_name]

    return tools_collection, stats
