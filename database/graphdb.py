import config
import neomodel

url = getattr(getattr(config.cfg, 'neo4j'), 'DATABASE_URL', None)

if url is not None:
    neomodel.config.DATABASE_URL = url
else:
    raise RuntimeError('neo4j url not config')


