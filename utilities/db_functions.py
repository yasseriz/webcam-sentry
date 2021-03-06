import sqlite3
from sqlite3 import Error

import numpy as np
import pandas as pd
import io
import cv2
import base64
import os


def create_connection(db_file):
	'''
		this function creates a db with the db_file name
	'''

	conn = None
	db_filepath = os.path.join("dbs", db_file)
	try:
		conn = sqlite3.connect(db_filepath)
	except Error as e:
		print(e)
	finally:
		if conn:
			conn.close()


def create_creds_and_whitelist_tables(db_file):
	conn = None

	db_filepath = os.path.join("dbs", db_file)

	try:
		conn = sqlite3.connect(db_filepath, detect_types=sqlite3.PARSE_DECLTYPES)
	except Error as e:
		print(e)

	#creates a new sqlite db for the user

	sql_create_stored_creds_table = """ CREATE TABLE IF NOT EXISTS creds(
											email text NOT NULL
											); """

	sql_create_stored_whitelist_table = """ CREATE TABLE IF NOT EXISTS whitelist(
											name text NOT NULL,
											embeddings blob NOT NULL
											); """

	cursor = conn.cursor()
	cursor.execute(sql_create_stored_creds_table)
	cursor.execute(sql_create_stored_whitelist_table)

def create_houskeeper(db_file="housekeeper"):
	'''
		the function just creates the housekeeping db
		if its created then its just a noop function,
		it will do nothing
	'''

	db_filepath = os.path.join("dbs", f"{db_file}.db")
	create_connection(f"{db_file}.db")

	conn = sqlite3.connect(db_filepath)

	sql_create_housekeeper_table= """ CREATE TABLE IF NOT EXISTS keeper(
											userid text NOT NULL,
											join_date datetime NOT NULL,
											expiry_date datetime NOT NULL
											); """

	cursor = conn.cursor()
	cursor.execute(sql_create_housekeeper_table)




def select_query(db_file, cols, table):
	""" 
		db_file: from the cookie
		cols: the columns the user wants to select
		table: table to query from
	"""

	conn = None
	db_filepath = os.path.join("dbs", db_file)
	conn = sqlite3.connect(db_filepath)

	cols_string = "".join(col+" " if col==cols[-1] else col+", " for col in cols)
	query = "SELECT "+cols_string+"FROM "+table

	results = pd.read_sql(query, conn)

	return results


def insert_query(db_file, cols, values, table):
	""" 
		db_file: from the cookie
		cols: the columns the user wants to select
		values: the values to be added per cols
		table: table to query from
	"""
	
	conn = None
	db_filepath = os.path.join("dbs", db_file)
	conn = sqlite3.connect(db_filepath)


	cols_string = "".join(col if col==cols[-1] else col+", " for col in cols)
	question_mark_string = "".join("?" if col==cols[-1] else "?, " for col in cols)
	query = "INSERT INTO "+table+"("+cols_string+") " + "VALUES"+ "("+question_mark_string+")"
	
	cursor = conn.cursor()
	cursor.execute(query, values)
	conn.commit()


def clear_whitelist_from_db(db_file, table):
	conn = None
	db_filepath = os.path.join("dbs", db_file)
	conn = sqlite3.connect(db_filepath)
	cursor = conn.cursor()

	query = f"DELETE FROM {table}"
	cursor.execute(query)
	conn.commit()



def encode_arr(arr):
	base64_arr = base64.b64encode(arr)
	return base64_arr

def decode_arr(byte_data):
	byte_data = base64.b64decode(byte_data)
	nparr = np.fromstring(byte_data)
	return nparr
