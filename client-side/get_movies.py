# GET data from My API Films, parse, and write to database

import json
import requests
import sqlite3
import os



TOKEN = os.environ['myapifilms_token']
url = requests.get('https://www.myapifilms.com/imdb/inTheaters?token={}&format=json&language=en-us'.format(TOKEN))

# convert data from feed to binary
binary = url.content

# decode the json feed
output = json.loads(str(binary, 'utf-8'))

print(json.dumps(output, indent=2, sort_keys=True))

# grab the list of movies
movies = output['data']['inTheaters']

with sqlite3.connect('movies.db') as connection:
	c = connection.cursor()


	# iterate through each movie and write to the database
	for movie in movies:
		all_movies = movie['movies']
		for meta in all_movies:
			if (meta['title']):
				c.execute("""INSERT INTO new_movies VALUES(?, ?, ?, ?, ?, ?)""",
						  		(meta.get('title'), meta.get('year'), meta.get('votes'),
						   		 meta.get('releaseDate'), meta.get('metascore'),
						   		 meta.get('rating')))


	# retrieve data
	c.execute("SELECT * FROM new_movies ORDER BY title ASC")


	# fetchall() retrieves all records from the query
	rows = c.fetchall()


	# output the rows to the screen, row by row
	for r in rows:
		print(r[0], r[1], r[2], r[3], r[4], r[5])