import redis


class RedisDatabase(object):
    def __init__(self):
        self.pool = redis.ConnectionPool(host='localhost', port=6379)

    @property
    def conn(self):
        if not hasattr(self, '_conn'):
            self.getConnection()
        return self._conn

    def getConnection(self):
        self._conn = redis.Redis(connection_pool=self.pool)
