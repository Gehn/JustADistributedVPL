#!/usr/bin/env python3

import sys
import json

from routes import webapp
from util import Api
import api
import states
from stateMachine import StateMachine


def Run(host="0.0.0.0", port="99", config_path=None):
	'''
		Run the web server for the site specified by the routes in this module.

		:param config_path: Optional additional or alternate configuration file.
	'''
	Api.SetMyUri(":".join([host,port]))

	#Initialize the instance that the API supports.
	api.stateMachineInstance = StateMachine()
	try:
		with open("./state_graph.temp", "r") as f:
			api.stateMachineInstance.FromStateGraph(json.loads(f.read()))
	except (IOError, ValueError):
		pass

	webapp.run(host=host, port=port)

	with open("./state_graph.temp", "w") as f:
		f.write(json.dumps(api.stateMachineInstance.GetStateGraph()))


if __name__=="__main__":
	ip = "0.0.0.0" #TODO: get from args?
	port = "82"
	if len(sys.argv) > 1:
		ip = sys.argv[1]
	if len(sys.argv) > 2:
		port = sys.argv[2]
	Run(ip, port)
