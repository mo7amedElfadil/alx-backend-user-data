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
import re
from typing import List


def filter_datum(fields: List[str], redaction: str,
                 message: str, separator: str) -> str:
    """ Returns the log message obfuscated
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
        super(RedactingFormatter, self).__init__(self.FORMAT)
        self.fields = fields

    def format(self, record: logging.LogRecord) -> str:
        """ format method that filters values in incoming log records
        """
        return filter_datum(self.fields, self.REDACTION,
                            super().format(record), self.SEPARATOR)
