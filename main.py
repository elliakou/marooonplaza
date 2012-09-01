#!/usr/bin/env python

import cgi
import datetime
import urllib
import webapp2
import os
import jinja2

from google.appengine.ext import db

jinja_environment = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

# This is a class that models a single event
class Event(db.Model):
	name = db.StringProperty()
	start_time = db.DateTimeProperty()
	end_time = db.DateTimeProperty()
	host = db.StringProperty()
	venue = db.StringProperty()
	price = db.FloatProperty()
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
			<form action="/submit" method="post" name="event_form">
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
		# And this does the HTTP POST, after which it returns to the front page
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
		new_event.price = float(self.request.get('price'))
		new_event.desc = self.request.get('desc')
		new_event.put()
		self.redirect("/")


# This code will run when someone loads index
class MainHandler(webapp2.RequestHandler):
	def get(self):
		# The lower and upper bounds, i.e. today and seven days from now
		today = datetime.datetime.today()
		next_week = today + datetime.timedelta(days=7)
		# Build the query to select the events for the next seven days.

		# This is done outside of the GqlQuery call--for some reason it doesn't like format strings
		query = """
				SELECT * FROM Event
				WHERE ANCESTOR IS :1
				AND start_time >= DATE(%s, %s, %s)
				AND start_time < DATE(%s, %s, %s)
				ORDER BY start_time ASC
				""" % (today.year,today.month,today.day,next_week.year,next_week.month,next_week.day)

		# The actual query, which dumps it into a list
		mp_events = db.GqlQuery(query, get_key())

		# Create an empty list for each of the next few days
		upcoming = [[] for i in range(7)]

		# Which we then iterate over
		for event in mp_events:
			# This stores a json object with the event
			event.json = """
				{ 'name': %s,
				  'host': %s,
				  'venue': %s,
				  'start_time': %s,
				  'end_time': %s,
				  'price': %s,
				  'desc': %s
				}
			""" % (event.name, event.host, event.venue, event.start_time, event.end_time, event.price, event.desc)

			# Same as above, except it's an HTML table. This should be removed in production.
			event.table = """
				<table class="event">
					<tr><td><strong>Name</strong></td><td>%s</td></tr>
					<tr><td><strong>Host</strong></td><td>%s</td></tr>
					<tr><td><strong>Venue</strong></td><td>%s</td></tr>
					<tr><td><strong>Start-Time</strong></td><td>%s</td></tr>
					<tr><td><strong>End-Time</strong></td><td>%s</td></tr>
					<tr><td><strong>Price</strong></td><td>%s</td></tr>
					<tr><td><strong>Description</strong></td><td>%s</td></tr>
				</table>
			""" % (event.name, event.host, event.venue, event.start_time, event.end_time, event.price, event.desc)

			upcoming[(event.start_time.date() - today.date()).days].append(event)
		# -- end of for loop --

		# ISO Weekdays run from 1-7 for Monday-Sunday
		weekday = datetime.datetime.today().isoweekday()
		template_values = {
			'now': upcoming[0],
			'one_off': upcoming[1],
			'two_off': upcoming[2],
			'three_off': upcoming[3],
			'four_off': upcoming[4],
			'five_off': upcoming[5],
			'six_off': upcoming[6],
		}

		header_template = jinja_environment.get_template('header.html')
		content_template = jinja_environment.get_template('main.html')
		footer_template = jinja_environment.get_template('footer.html')
		self.response.out.write(header_template.render())
		self.response.out.write(content_template.render(template_values))
		self.response.out.write(footer_template.render())

	# Helper function that tests if a datetime falls within a period of time, [start, end)
	def between(start, end, test):
		if start <= test:
			if end > test:
				return true
		return false

	# Helper function that tests if an event is going on between a given period of time, [start, end),
	# useful for multi-day events
	def occurs(start, end, event):
		if between(start, end, event.start_time):
			return true
		elif between(start, end, event.end_time):
			return true
		else:
			return false
# -- end of MainHandler --


def About(webapp2.RequestHandler):
	header_template = jinja_environment.get_template('header.html')
	content_template = jinja_environment.get_template('about.html')
	footer_template = jinja_environment.get_template('footer.html')
	self.response.out.write(header_template.render())
	self.response.out.write(content_template.render())
	self.response.out.write(footer_template.render())
# -- end of About --


# The following code makes App Engine Work
# Remove debug=True when in production
app = webapp2.WSGIApplication([('/', MainHandler), ('/submit', Calendar)], debug=True)

def main():
	run_wsgi_app(application)

if __name__ == '__main__':
	main()