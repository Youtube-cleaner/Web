# -- coding: UTF-8 --
from flask import Flask, render_template, request
import sqlite3 as sql
import pandas
from googleapiclient.discovery import build
import warnings
import random
import numpy as np

app = Flask(__name__)
@app.route('/hello')
def hello_world():
    return "Hello World!"

@app.route('/home')
def home():
	return render_template("index.html")

@app.route('/crawling' ,methods = ['POST','GET'])
def crawling():
	if request.method == 'POST':
		try:
			global url
			url = request.form['youtubeurl']

			api_key = 'AIzaSyDCXMCLjNhtLqpxpQqP4gMeRE4ZtOCbwq8'
			video_id = url
			comments = list()
			api_obj = build('youtube', 'v3', developerKey=api_key)
			response = api_obj.commentThreads().list(part='snippet,replies', videoId=video_id, maxResults=100).execute()

			while response:
				for item in response['items']:
					comment = item['snippet']['topLevelComment']['snippet']
					comments.append(
						[comment['textDisplay'], comment['authorDisplayName']])

				if 'relpies' in item.keys():
					for reply_item in item['replies']['comments']:
						reply = reply_item['snippet']
						comments.append([reply['textDisplay'], reply['authorDisplayName']])
				if 'nextPageToken' in response:
					response = api_obj.commentThreads().list(part='snippet,replies', videoId=video_id,
						pageToken=response['nextPageToken'], maxResults=100).execute()
				else:
					break

			df = pandas.DataFrame(comments)
		finally:
			count = int(len(df.index))
			score = []
			for i in range(count):
				rand = random.randrange(30,70)/100
				score.append(rand)
			df.insert(2,2,score)

			con = sql.connect("database.db")
			df.to_sql(url, con)
			con.row_factory  = sql.Row

			cur = con.cursor()
			cur.execute("select * from "+ url + " order by 4 ASC")
	
			rows = cur.fetchall()

			return render_template("result.html",url = url, rows=rows)
			con.close()
	
@app.route('/desc')
def desc():
	con = sql.connect("database.db")
	con.row_factory  = sql.Row

	cur = con.cursor()
	cur.execute("select * from "+ url + " order by 4 DESC")
	
	rows = cur.fetchall()

	return render_template("result.html",url = url, rows=rows)
	con.close()


@app.route('/asc')
def asc():
	con = sql.connect("database.db")
	con.row_factory  = sql.Row

	cur = con.cursor()
	cur.execute("select * from "+ url + " order by 4 ASC")
	
	rows = cur.fetchall()

	return render_template("result2.html",url = url, rows=rows)
	con.close()

if __name__ == '__main__':
	app.debug = True
	app.run(host='0.0.0.0')
