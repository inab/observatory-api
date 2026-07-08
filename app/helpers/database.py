import configparser
from pymongo import MongoClient
import os


def _load_config():
    """Read the CONFIG_PATH ini file if it exists.

    Missing/unreadable files leave the parser empty (configparser.read does not raise),
    so callers must tolerate absent sections — settings are then supplied via env vars.
    """
    config = configparser.ConfigParser()
    config_path = os.getenv('CONFIG_PATH', './api-variables/dev_config_db.ini')
    if config_path:
        config.read(config_path)
    return config


def _setting(config, key, default=None):
    """Resolve one MongoDB setting.

    Precedence: environment variable (used in CI, where the gitignored ini is absent and
    values come from GitHub secrets) > the CONFIG_PATH ini file (local/dev/prod) > default.
    Env var names match the ini keys (DBHOST, DBPORT, ...). Raises if a required value is
    set nowhere so misconfiguration surfaces clearly instead of silently connecting nowhere.
    """
    val = os.getenv(key)
    if val is not None:
        return val
    if config.has_option('MONGO_DETAILS', key):
        return config.get('MONGO_DETAILS', key)
    if default is not None:
        return default
    raise EnvironmentError(
        f"Missing MongoDB setting '{key}': set it as an environment variable "
        f"or under [MONGO_DETAILS] in the CONFIG_PATH ini file."
    )


def _make_client(config):
    """Build a (lazy) MongoClient from env vars / ini.

    Host/port fall back to localhost defaults so import never fails in an unconfigured CI
    (where the tests only exercise pure functions and never actually reach the DB). Auth
    params are only passed when a username is configured; without one an anonymous client
    is built, which is fine for local Docker Mongo and for CI import.
    """
    host = _setting(config, 'DBHOST', default='localhost')
    port = _setting(config, 'DBPORT', default='27017')
    user = os.getenv('DBUSER') or (config.get('MONGO_DETAILS', 'DBUSER')
                                   if config.has_option('MONGO_DETAILS', 'DBUSER') else '')

    kwargs = {'host': [f'{host}:{port}']}
    if user:
        kwargs.update(
            username=user,
            password=_setting(config, 'DBPASS'),
            authSource=_setting(config, 'DBAUTHSRC', default='admin'),
            authMechanism='SCRAM-SHA-256',
        )
    return MongoClient(**kwargs)


# Collection/DB names are not secret; defaulting them lets the app import with zero config
# in CI while real deployments still override via the ini file or environment variables.
def connect_DB():
    config = _load_config()
    client = _make_client(config)
    mongo_db = _setting(config, 'DATABASE', default='observatory')

    tools_collection = client[mongo_db][_setting(config, 'TOOLS', default='tools')]
    stats = client[mongo_db][_setting(config, 'STATS', default='stats')]
    pubs_collection = client[mongo_db][_setting(config, 'PUBS', default='publications')]
    availability_collection = client[mongo_db][_setting(config, 'AVAILABILITY', default='availability')]

    return tools_collection, stats, pubs_collection, availability_collection


def connect_similarity_DB():
    config = _load_config()
    client = _make_client(config)
    mongo_db = _setting(config, 'DATABASE', default='observatory')

    return client[mongo_db][_setting(config, 'SIMILARITY', default='similarity')]
