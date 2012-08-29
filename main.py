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
	start_time = db.DateTimeProperty()
	end_time = db.DateTimeProperty()
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

				Start
				Y <input type="text" name="start_year"></input>
				M <input type="text" name="start_month"></input>
				D <input type="text" name="start_day"></input>
				H <input type="text" name="start_hour"></input>
				M <input type="text" name="start_min"></input><br>

				End
				Y <input type="text" name="end_year"></input>
				M <input type="text" name="end_month"></input>
				D <input type="text" name="end_day"></input>
				H <input type="text" name="end_hour"></input>
				M <input type="text" name="end_min"></input><br>

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
		new_event.start_time = datetime.datetime(int(self.request.get('start_year')),
												 int(self.request.get('start_month')),
												 int(self.request.get('start_day')),
												 int(self.request.get('start_hour')),
												 int(self.request.get('start_min')))
		new_event.end_time = datetime.datetime(int(self.request.get('end_year')),
											   int(self.request.get('end_month')),
											   int(self.request.get('end_day')),
											   int(self.request.get('end_hour')),
											   int(self.request.get('end_min')))
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
			table_string = """
				<table>
					<tr>
						<td>Name</td>
						<td>%s</td>
					</tr>
					<tr>
						<td>Time</td>
						<td>from %s to %s</td>
					</tr>
					<tr>
						<td>Hosted by</td>
						<td>%s</td>
					</tr>
					<tr>
						<td>Location</td>
						<td>%s</td>
					</tr>
					<tr>
						<td>Price</td>
						<td>%s</td>
					</tr>
					<tr>
						<td>Description</td>
						<td>%s</td>
					</tr>
				</table>""" % (event.name, event.start_time, event.end_time, event.host, event.venue, event.price, event.desc)
			self.response.out.write(table_string)

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
					<td class="mon"></td>
					<td class="tue"></td>
					<td class="wed"></td>
					<td class="thu"></td>
					<td class="fri"></td>
					<td class="sat"></td>
					<td class="sun"></td>
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