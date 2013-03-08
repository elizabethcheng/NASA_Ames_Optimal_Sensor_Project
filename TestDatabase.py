#Test Database Creation
import sqlite3
from sqlite3 import dbapi2 as sqlite3
connection = sqlite3.connect('test.db')
memoryConnection = sqlite3.connect(':memory:')
cursor = connection.cursor()
