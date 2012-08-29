#!/usr/bin/env python

import cgi
import datetime
import urllib
import webapp2

from google.appengine.ext import db
from google.appengine.api import users


# This is a class that models a single event
class Event(db.Model):
	name = db.StringProperty()
	start_time = db.IntegerProperty()
	end_time = db.IntegerProperty()
	host = db.StringProperty()
	venue = db.StringProperty()
	price = db.IntegerProperty()
	# This next one might need to be a TextProperty
	desc = db.StringProperty(multiline=True)

# There's functionality for multiple calendars if that's ever a feature
# Otherwise always call this with no arguments
def get_key(event_key=None):
	return db.Key.from_path('Calendar', event_key or 'default')

# Datastore related, also handles event adding
class Calendar(webapp2.RequestHandler):
	def get(self):
		# This should be the page to post an event.
		self.response.out.write("""
			<form action="/new" method="post" name="event_form">
				Name <input type="text" name="name"></input><br>
				Start <input type="text" name="start_time"></input><br>
				End <input type="text" name="end_time"></input><br>
				Host <input type="text" name="host"></input><br>
				Venue <input type="text" name="venue"></input><br>
				Price <input type="text" name="price"></input><br>
				Desc <input type="text" name="desc"></input><br>
				<input type="submit" value="Submit"></input>
			</form>
		""")
	def post(self):
		# And this does the HTTP POST. This will create a confirmation page, unless that should be a separate URL
		new_event = Event(parent=get_key())
		new_event.name = self.request.get('name')
		new_event.start_time = int(self.request.get('start_time'))
		new_event.end_time = int(self.request.get('end_time'))
		new_event.host = self.request.get('host')
		new_event.venue = self.request.get('venue')
		new_event.price = int(self.request.get('price'))
		new_event.desc = self.request.get('desc')
		new_event.put()
		self.redirect("/")

# This code will run when someone loads index
class MainHandler(webapp2.RequestHandler):
	def get(self):
		# Write HTML directly to the page from this script. This is temporary and for testing functionality only.
		mp_events = Event.gql("WHERE ANCESTOR IS :1 ORDER BY start_time DESC LIMIT 10", get_key())

		for event in mp_events:
			self.response.out.write(event.name)

		self.response.out.write("""
			<a href="/new">Add Somethin'</a><br>
			<table>
				<tr>
					<th>
						Monday
					</th>
					<th>
						Tuesday
					</th>
					<th>
						Wednesday
					</th>
					<th>
						Thursday
					</th>
					<th>
						Friday
					</th>
					<th>
						Saturday
					</th>
					<th>
						Sunday
					</th>
				</tr>
				<tr>
					<td id="mon"></td>
					<td id="tue"></td>
					<td id="wed"></td>
					<td id="thu"></td>
					<td id="fri"></td>
					<td id="sat"></td>
					<td id="sun"></td>
				</tr>
			</table>
		""")

# The following code makes App Engine Work
# Remove debug=True when in production
app = webapp2.WSGIApplication([('/', MainHandler), ('/new', Calendar)], debug=True)

def main():
	run_wsgi_app(application)

if __name__ == '__main__':
	main()