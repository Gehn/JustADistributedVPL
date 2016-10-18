import http.client
import inspect
import time
import json
import urllib
import logging
import sys

from bottle import request

formatter = logging.Formatter('%(levelname)s : %(asctime)s : %(message)s')
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(0)
handler.setFormatter(formatter)
logger = logging.getLogger()
logger.setLevel(0)
logger.addHandler(handler)

logger.info('Logging enabled.')


#TODO; this whole module is an unmitigated disaster.  Replace it with something real.
class Api:
	api_endpoints = {}
	_URI = None

	def __init__(self, targetHost):
		self.targetHost = targetHost

	def call(self, target, *args, **kwargs):
		return Api.api_endpoints[target](self.targetHost, *args, **kwargs)

	#custom_index for use when you're wrapping original function.
	@staticmethod
	def NewEndpoint(function, route, method="GET", custom_index=None):
		if custom_index == None:
			custom_index = function

		if custom_index not in Api.api_endpoints:
			Api.api_endpoints[custom_index] = ApiCall(function, route, method)
		else:
			Api.api_endpoints[custom_index].addNewRoute(route)

	@staticmethod
	def SetMyUri(uri):
		Api._URI = uri

	@staticmethod
	def GetMyUri():
		return Api._URI


	def GetTargetUri(self):
		return self.targetHost
		


class ApiCall:
	def __init__(self, target, route, method):
		self.target = target
		self.routes = []
		self.method = method

		self.addNewRoute(route)


	def parseRouteTemplate(self, route):
		route_path = route.split('?')[0]
		param_string = ""
		if '?' in route:
			param_string = route.split('?')[1]

		route_vars = {index:item[1:-1] for index, item in enumerate(route_path.split('/')) \
					if len(item) > 1 and item[0] == '<' and item[len(item)-1] == '>'}
		param_vars = [item[1:-1] for item in param_string.split('&') \
					if len(item) > 1 and item[0] == '<' and item[len(item)-1] == '>']

		return (route_vars, param_vars)


	def __call__(self, host, *args, **kwargs):
		route = self.buildRoute(*args, **kwargs)
		logger.info("calling: " + route)
		return makeApiCall(host, route, self.method)
	

	def addNewRoute(self, newRoute):
		self.routes.append(newRoute)


	def buildRoute(self, *args, **kwargs):
		argspec = inspect.getargspec(self.target)
		#Extract the default args and match them with their values for later use.
		defaults = {}
		if argspec.defaults:
			defaults = {key:val for key, val in zip(argspec.args[-len(argspec.defaults):], argspec.defaults)}

		#Match varargs with actual arg ordering for the Api call
		target_args = argspec.args

		populated_arg_index = {}

		for index,target in enumerate(target_args):
			if index < len(args):
				populated_arg_index[target] = args[index]
			else:
				try:
					populated_arg_index[target] = kwargs[target]
				except:
					#arg not found, could be fine if derived from default.  TODO: validate here?
					pass

		#Determine which route we should be using.
		#And try to apply the args into the URI variables.
		target_route = None
		route_vars = {}
		param_vars = []
		for potential_route in self.routes:
			route_vars, param_vars = self.parseRouteTemplate(potential_route)
			if set(route_vars.values()).union(set(param_vars)) == set(populated_arg_index.keys()):
				target_route = potential_route
				break

		if target_route == None:
			raise Exception("No valid route")

		#Populate the route with provided arguments.
		populated_route_tokens = []
		for index, token in enumerate(target_route.split('?')[0].split('/')):
			if index in route_vars:
				populated_route_tokens.append(urllib.parse.quote(str( \
					populated_arg_index[route_vars[index]] \
				)))
			else:
				populated_route_tokens.append(token)

		#Build the "real" URL
		complete_base_route = "/".join(populated_route_tokens)


		#TODO: do the list-value multi-parameter expansion here, if I really want to support it.
		#I did it on the other side of the equation, so I really should.
		query_parameters = [str(param) + "=" + urllib.parse.quote(str(populated_arg_index[param])) \
					for param in param_vars]
		complete_route = complete_base_route
		if query_parameters:
			complete_route += "?" + "&".join(query_parameters)
		
		return complete_route
		

def registerApi(route, routeFunction = None, method="GET"):
	def Route(callback):
		logger.info("Registering API: " + str(route) + " with callback: " + str(callback))
		unpack_wrapped_callback = wrapFunctionWithUnpacker(callback)
		unquote_wrapped_callback = wrapFunctionWithUnquoter(unpack_wrapped_callback)

		Api.NewEndpoint(callback, route, method)

		if routeFunction:
			routeFunction(route.split('?')[0])(unquote_wrapped_callback)
		return callback
	return Route


def makeApiCall(host, resource,method="GET", protocol="http"):
	'''
		Makes an http request and returns the un-jsonified response.

			:param resource: the path (e.g. /v2/items) to query for.
	'''
	found_resource = False #To deal with redirects
	retries = 0 # How many retries have we gone through thus far.
	retry_threshold = 2 # For transient errors
	retry_delay = 1 # Seconds

	url = host
	data = None

	while not found_resource:
		#logger.debug("Getting: " + str(protocol) + str(url) + str(resource))

		if protocol == "https":
			connection = http.client.HTTPSConnection(url)
		else:
			connection = http.client.HTTPConnection(url)

		connection.request(method, resource)

		response = connection.getresponse()

		if response.status >= 500 and retries < retry_threshold:
			#logger.error("Retrying due to potentially transient Api failure: " + response.reason + " ; " + str(response.status))
			retries += 1
			time.sleep(retry_delay)
			continue
		elif response.status >= 400:
			connection.close()
			#logger.error("Api call failed: " + response.reason + " ; " + str(response.status))
			raise Exception("Api call failed: " + response.reason + " ; " + str(response.status))
		elif response.status == 302:
			parsed_url = urlparse(response.getheader('location'))
			url = parsed_url.netloc
			#resource = parsed_url.path FIXME: Determine if I should have this to some extent.
			protocol = parsed_url.scheme
			#logger.debug("Redirecting to: " + str(protocol) + str(url) + str(resource))
			continue
		elif 200 <= response.status < 300 :
			#logger.debug("Got response.")
			found_resource = True
		else:
			#logger.error("Unspecified response: " + str(response.status))
			pass

		response_body = response.read()

		try:
			#print(data)
			data = json.loads(response_body.decode())
		except Exception as e: #Known to be value error; but that came out of nowhere, so being a bit generous here.
			logger.info("Json parsing failure for " + str(resource) + " : " + str(e))


	connection.close()

	return data


def wrapFunctionWithUnpacker(callback):
	'''
		return a callback that unpacks the query parameters into args.
	'''
	def unpacked_callback(*args, **kwargs):
		for key in request.query.keys():
			vals = request.query.getall(key)
			kwargs[key] = vals if len(vals) > 1 else vals[0]

		return callback(*args, **kwargs)

	return unpacked_callback


def wrapFunctionWithUnquoter(callback):
	'''
		return a callback that unquotes all string args automagically.

		:param callback: The function to cook.
	'''
	def unquoted_callback(*args, **kwargs):
		unquoted_args = []
		unquoted_kwargs = {}

		for arg in args:
			if arg.__class__.__name__ == "str":
				unquoted_args.append(urllib.parse.unquote(arg))

		for (key, value) in kwargs.items():
			if value.__class__.__name__ == "str":
				unquoted_kwargs[key] = urllib.parse.unquote(value)

		return callback(*args, **kwargs)

	return unquoted_callback


