import os

from psycopg2.extensions import connection


class DBConfig:
    _dBConnection = None

    @classmethod
    def getDBConnection(cls) -> connection:
        if cls._dBConnection is None:
            raise ValueError(
                'DB connection is not specified. '
                'Please, use setDBConnection function to specify it.')
        return cls._dBConnection

    @classmethod
    def setDBConnection(cls, dBConnection: connection):
        cls._dBConnection = dBConnection


STYLES_PATH = os.path.join(os.path.dirname(
    os.path.realpath(__file__)), 'styles')
