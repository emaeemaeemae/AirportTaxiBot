class DatabaseWrapperError(Exception):
    pass


class MySQLWrapperError(DatabaseWrapperError):
    pass


class MySQLWrapperBehaviorError(MySQLWrapperError):
    pass


class MySQLWrapperTransactionError(MySQLWrapperError):
    pass


class MySQLWrapperContextError(MySQLWrapperError):
    pass

