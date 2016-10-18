import functools
import os
import string
import urllib
import json
import sys

from bottle import route, run, template, jinja2_view, url, Jinja2Template, response, static_file, put, get
import bottle

# ----- INITIALIZE THE SERVER ----- #

webapp = bottle.Bottle()


from api import *
from util import Api



# ----- SET UP THE TEMPLATE ENGINE ----- #

Jinja2Template.defaults = {
}

# ----- SET UP HELPER FUNCTIONS ----- #

# Convenience function to set up views from the right directory
view = functools.partial(jinja2_view, template_lookup=['views'])

def make_link(destination, text=None):
	'''
		Convenience function, generate the HTML for a link.

		:param destination: the location of the link.
		:param text: the alt text of the link. (default = destination)
	'''
	if not text:
		text = destination

	return "<a href=\"%s\">%s</a>" % (destination, text)

# Thanks to richard-flosi for this gist.
@webapp.hook('after_request')
def enable_cors():
    """
    You need to add some headers to each request.
    Don't use the wildcard '*' for Access-Control-Allow-Origin in production.
    """
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'PUT, GET, POST, DELETE, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Origin, Accept, Content-Type, X-Requested-With, X-CSRF-Token'


# ----- ROUTES ----- #

@webapp.route("/")
@view("basePage.tpl")
def Root():
	return {}


@webapp.route("/joint.css")
def GetCSS():
	return static_file("joint.min.css", root="./")


@webapp.route("/joint.js")
def GetJS():
	return static_file("joint.min.js", root="./")


@webapp.route("/jquery.js")
def GetJS():
	return static_file("jquery.min.js", root="./")


@webapp.route("/lodash.js")
def GetCSS():
	return static_file("lodash.js", root="./")


@webapp.route("/backbone.js")
def GetJS():
	return static_file("backbone.js", root="./")




