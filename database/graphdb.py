import config
import neomodel

_type = getattr(config.cfg, 'database_connect_type')
database_config = getattr(config.cfg, _type)
url = getattr(getattr(database_config, 'neo4j'), 'DATABASE_URL', None)

if url is not None:
    neomodel.config.DATABASE_URL = url
else:
    raise RuntimeError('neo4j url not config')


