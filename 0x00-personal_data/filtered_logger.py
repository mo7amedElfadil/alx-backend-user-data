#!/usr/bin/env python3
""" Obfuscation of log messages using regex
    Uses regex to replace occurences of certain field
    values with the redaction string
    Worth noting that the regex I use is non-greedy
    There is also a look-ahead version of the regex
    eg.
        message = re.sub(rf'{field}=.*?(?={separator})',
                          f'{field}={redaction}', message)
"""
import logging
import mysql.connector
from os import getenv
import re
from typing import List


PII_FIELDS = ('name', 'email', 'phone', 'ssn', 'password')


def filter_datum(
        fields: List[str], redaction: str, message: str, separator: str
        ) -> str:
    """ Returns the log message obfuscated
        Args:
            fields (List[str]): representing all fields to obfuscate
            redaction (str): representing the obfuscated string
            message (str): representing the log line
            separator (str): representing the separator for the fields
        Returns:
            str: the log message obfuscated
    """
    for field in fields:
        message = re.sub(rf'{field}=.+?{separator}',
                         f'{field}={redaction}{separator}', message)
    return message


class RedactingFormatter(logging.Formatter):
    """ Redacting Formatter class
    """

    REDACTION = "***"
    FORMAT = "[HOLBERTON] %(name)s %(levelname)s %(asctime)-15s: %(message)s"
    SEPARATOR = ";"

    def __init__(self, fields: List[str]):
        """ Constructor for obfuscating PII in log messages
        """
        super(RedactingFormatter, self).__init__(self.FORMAT)
        self.fields = fields

    def format(self, record: logging.LogRecord) -> str:
        """ format method that filters values in incoming log records
            Args:
                record (logging.LogRecord): the record to filter
            Returns:
                str: the log message obfuscated
        """
        return filter_datum(self.fields, self.REDACTION,
                            super().format(record), self.SEPARATOR)


def get_logger() -> logging.Logger:
    """ Returns a logging object
        logger is named user_data and has a log level of INFO
        It should not propagate messages to other loggers
        It has a StreamHandler with RedactingFormatter as formatter
        Returns:
            logging.Logger: the user_data logger
    """
    logger = logging.getLogger('user_data')
    logger.setLevel(logging.INFO)
    logger.propagate = False
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(RedactingFormatter(list(PII_FIELDS)))
    logger.addHandler(stream_handler)
    return logger


def get_db() -> mysql.connector.connection.MySQLConnection:
    """ Returns a connector to the database
    """
    return mysql.connector.connect(
        user=getenv('PERSONAL_DATA_DB_USERNAME', 'root'),
        password=getenv('PERSONAL_DATA_DB_PASSWORD', ''),
        host=getenv('PERSONAL_DATA_DB_HOST', 'localhost'),
        database=getenv('PERSONAL_DATA_DB_NAME')
    )


def main():
    """ Main function
        Connects to the database and retrieves all rows from the users table
        Logs each row in the users table in a specific format
    """
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users;")
    logger = get_logger()
    for row in cursor:
        logger.info(
                "; ".join([f"{key}={value}" for key, value in row.items()])
                )

    cursor.close()
    db.close()


if __name__ == '__main__':
    main()
