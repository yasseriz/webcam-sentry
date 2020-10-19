from __main__ import app

from flask import Flask, redirect, url_for, render_template, request, jsonify
import base64
import cv2
import numpy as np
import os

from email_functions import send_image
from db_functions import select_query, insert_query
from face_recognition_functions import get_face_encodings


@app.route('/setup_sentry')
def setup_sentry():
	userid = request.cookies.get('userid')
	db_file = f"{userid}.db"
	results = select_query(db_file, ["email"], "creds")
	whitelist = select_query(db_file, ["name"],"whitelist")

	whitelisted_name = whitelist["name"].values

	if len(results):
		stored_cred = results["email"].values[-1]
	else:
		stored_cred = ""

	return render_template('sentry_setup_template.html', stored_cred=stored_cred, whitelisted_name=whitelisted_name)


@app.route('/_photo_cap', methods=["GET", "POST"])
def photo_cap():
	name = request.args.get('whitelisted_name')
	receiver_email = request.args.get('sentry_email')

	#update credintials if they are different than stored
	userid = request.cookies.get('userid')
	db_file = f"{userid}.db"
	results = select_query(db_file, ["email"], "creds")
	if len(results):
		stored_cred = results["email"].values[-1]
	else:
		stored_cred = ""

	if receiver_email != stored_cred:
		values = (receiver_email,)
		insert_query(db_file, ["email"], values ,"creds")


	photo_base64 = request.args.get('photo_cap')
	header, encoded = photo_base64.split(",", 1)
	binary_data = base64.b64decode(encoded)
	image_name = f"{name}.jpg"

	nparr = np.fromstring(binary_data, np.uint8)
	img_np = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
	img_np = cv2.cvtColor(img_np, cv2.COLOR_BGR2RGB)

	whitelist_results = select_query(db_file, ["name"], "whitelist")
	whitelist_results = whitelist_results.values

	if name.lower() not in whitelist_results:
		values = (name.lower(), get_face_encodings(img_np))
		insert_query(db_file, ["name", "embeddings"], values ,"whitelist")


		with open(os.path.join("./static/images/captures",image_name), "wb") as f:
			f.write(binary_data)

		send_image( receiver_email, subject="Sentry is whitelisting this person !",
					body="Hey, you have requested to whitelist this person",
					image_name=name)

	#facial recognition operations
	response = 'whitelisted face'

	return response