import redis


class RedisDatabase(object):
    def __init__(self):
        self.pool = redis.ConnectionPool(host='localhost', port=6379)

    @property
    def conn(self):
        if not hasattr(self, '_conn'):
            self.get_connection()
        return self._conn

    def get_connection(self):
        self._conn = redis.Redis(connection_pool=self.pool)
