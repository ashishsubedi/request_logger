
# Not Implemented

from request_logger.core.storage import AbstractStorage

class PostgresStorage(AbstractStorage):
    def __init__(self, db):
        self.db = db
    
    def save(self, request_data):
        raise NotImplementedError()

