import threading
from collections import defaultdict

from state import *
from link import LinkTypes

class StateMachine:
	def __init__(self):
		self._currentStates = set([])
		self._states = {}
		self._remoteStates = defaultdict(dict) #{IP:ID:state}


	def Run(self, stateId=None, passthrough=None):
		if stateId == None:
			targets = [state.Run for state in self._states.values() if state.IsRunnable()]
		else:
			targets = [self.GetState(stateId).Run]

		for target in targets:			
			thread = threading.Thread(target=target)
			thread.start()

		return


	def AddState(self, stateType):
		if isinstance(stateType, str):
			stateType = self.GetAvailableStateTypes()[stateType]

		newState = MetaState(stateType)
		newId = newState.GetId()
		self._states[newId] = newState
		return newState


	def AddRemoteState(self, remoteIp, remoteStateId, remoteStateType, remoteSettings=[], remoteArguments=[]):
		try:
			return self.GetRemoteState(remoteIp, remoteStateId)
		except:
			pass

		newState = RemoteState(remoteIp, remoteStateId, remoteStateType, remoteSettings, remoteArguments)
		newId = newState.GetId()
		self._states[newId] = newState
		self._remoteStates[remoteIp][remoteStateId] = newState
		return newState


	def RemoveState(self, state):
		#TODO: the behavior of this with remote states needs to get tuned.
		#TODO this try except is a cop out.  Formalize your behavior for all mutable stuff, especially for threads. (use locks you idiot, don't overthink it.)
		if state.__class__ == int:
			state = self._states[state]

		del(self._states[state.GetId()])
		if isinstance(state, RemoteState):
			del(self._remoteStates[state.GetRemoteUri()][state.GetRemoteId()])

		linksToRemove = set([])
		for link in state.GetAllIncomingLinks():
			linksToRemove.add(link)

		for child in state.GetNextStates():
			for link in child.GetIncomingLinks(state):
				linksToRemove.add(link)

		for link in linksToRemove:
			try:
				link.Remove()
			except:
				pass


	def LinkStates(self, source, destination, argument=None, setting=None, linkType=LinkTypes.required, shouldProliferate=True):
		if source.__class__ == int:
			source = self._states[source]
		if destination.__class__ == int:
			destination = self._states[destination]

		source.AddOutgoingLink(destination, argument, setting, linkType, shouldProliferate)


	def UnlinkStates(self, source, destination, argument=None, setting=None, shouldProliferate=True):
		if source.__class__ == int:
			source = self._states[source]
		if destination.__class__ == int:
			destination = self._states[destination]

		source.RemoveOutgoingLink(destination, argument, setting, shouldProliferate)


	def GetAllStates(self):
		return self.GetStateGraph()["states"]


	def GetAllVectors(self):
		return self.GetStateGraph()["vectors"]

	
	def GetStateGraph(self):
		return {state.GetId():state.GetSummaryDict() for state in self._states.values()}


	def FromStateGraph(self, graph):
		for stateId, stateDict in graph.items():
			if "remoteId" in stateDict:
				state = RemoteState(stateDict["remoteUri"], stateDict["remoteId"])
				state.FromSummaryDict(stateDict)
				state.LoadFromRemote() #TODO: this is gonna be problematic.
				self._remoteStates[state.GetRemoteUri()][state.GetRemoteId()] = state
			else:
				state = MetaState(stateDict["typeId"])
				state.FromSummaryDict(stateDict)
				self._states[state.GetId()] = state

		for stateId, stateDict in graph.items():
			for link in stateDict["incomingLinks"]:
				parent = self.GetState(link["parent"])
				child = self.GetState(int(stateId))
				parent.AddOutgoingLink(child, link["argument"], link["setting"], link["linkType"])


	def GetAvailableStateTypes(self):
		return MetaState.GetAvailableStateTypes()


	def GetState(self, stateId):
		return self._states[stateId]


	def GetRemoteState(self, stateIp, stateId):
		if stateIp == Api.GetMyUri():
			return GetState(stateId)
		return self._remoteStates[stateIp][stateId]


	def GetRemoteStateMap(self):
		return self._remoteStates
