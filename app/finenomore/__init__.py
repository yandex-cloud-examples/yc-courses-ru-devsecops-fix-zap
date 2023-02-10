import os
import json
import datetime
import re
import socket
import base64
import string
import random
import psycopg2
from pathlib import Path

from flask import Flask
from flask import Markup
from flask import request
from flask import jsonify
from flask import render_template

from flask_bootstrap import Bootstrap5
from flask_talisman import Talisman

def is_number(number):
  RE_NUMBER = r"[а-яА-Яa-zA-Z]\d{3}[а-яА-Яa-zA-Z]{2}\d{1,3}"
  match = re.fullmatch(RE_NUMBER, number)
  if match:
    return True
  else:
    return False

def create_app():
  app = Flask(__name__)

  app.config.from_prefixed_env()

  bootstrap = Bootstrap5(app)


  SELF = "'self'"
  talisman = Talisman(
      app,
      force_https=False,
      content_security_policy={
        'default-src': "'none'",
        'img-src': SELF,
        'script-src': [
            SELF,
            'https://cdn.jsdelivr.net',
        ],
        'style-src': [
            SELF,
            'https://cdn.jsdelivr.net',
        ],
        'object-src': "'none'",
        'connect-src': "'none'",
        'require-trusted-types-for': "'script'",
      },
      permissions_policy = {
        'geolocation': '()',
      },
  )

  def get_cursor():
    conn = psycopg2.connect(host=os.getenv("POSTGRES_HOST", "postgres"),
      database=os.getenv("POSTGRES_DB"),
      user=os.getenv("POSTGRES_USER"),
      password=os.getenv("POSTGRES_PASSWORD"))

    conn.set_session(autocommit=True)

    return conn.cursor()

  @app.route("/")
  def root():
    return render_template('index.html')

  @app.route("/api/search/", methods=["POST"])
  def api_search():
    content = request.json
    rows = []
    if 'number' in content:
      number = content['number']
      app.logger.info("Check number: %s", number)
      if not(is_number(number)):
        app.logger.warning(f"Wrong number: {number}")
        return jsonify({ "result": "Wrong number. See logs." }), 500
      cur = get_cursor()
      try:
        cur.execute(f"SELECT * FROM fines WHERE number_id IN (SELECT id FROM numbers WHERE LOWER(number) = LOWER(%s));", (number,))
        rows = cur.fetchall()
      except:
        return jsonify({ "result": "Database error" }), 500

    return jsonify({ "result": rows })

  @app.route("/number/", methods=["GET"])
  def number():
    number = request.args.get('n')
    if not(is_number(number)):
      app.logger.warning(f"Wrong number: {number}")
      return render_template('search.html', number = Markup("ERROR"), rows = [])
    rows = []
    if number:
      cur = get_cursor()
      try:
        cur.execute(f"SELECT * FROM fines WHERE number_id IN (SELECT id FROM numbers WHERE LOWER(number) = LOWER(%s));", (number,))
        rows = cur.fetchall()
      except:
        pass

    return render_template('search.html', number = Markup(number), rows = rows)

  @app.route("/status/")
  def status():
    return jsonify({ "status": "ok", "database": get_cursor().connection.status })

  return app
