from collections import defaultdict
import json
import inspect

from util import Api, logger
import api
from link import Link, LinkTypes

def State(stateType):
	MetaState._availableStateTypes[stateType.__module__ + '.' + stateType.__name__] = stateType
	MetaState._availableStateTypesReverseIndex[stateType] = stateType.__module__ + '.' + stateType.__name__
	logger.info("Registering state:" + str(stateType))
	return stateType



class MetaState:
	_availableStateTypes = {}
	_availableStateTypesReverseIndex = {}
	@classmethod
	def GetAvailableStateTypes(obj):
		return MetaState._availableStateTypes

	_maxId = 0
	def __init__(self, runnableStateType):
		self._id = MetaState._maxId
		MetaState._maxId += 1

		self._nextStates = []

		#Args are dicts as well to more easily maintain index:value prior to running.
		self._settingsArgs = {}
		self._settingsKWArgs = {}

		self._runtimeArgs = {}
		self._runtimeKWArgs = {}
	
		self._incomingLinks = []
		self._parentsReady = []

		#This seems...  hacky? But it lets the UX abuse the engine for consistent layout.
		#Easy enough to rip out later if I end up getting smart about things.
		self._arbitraryData = {}

		if (runnableStateType and runnableStateType.__class__ == int):
			self._runnableStateType = _availableStateTypes[runnableStateType]
		else:
			self._runnableStateType = runnableStateType


	def AcceptIncomingResult(self, parent, result):
		logger.info("Accepting argument: " + str(result) + "; From: " + str(parent.GetId()))

		ret = False
		for link in self._incomingLinks:
			if link.GetParent() == parent:
				if link.GetArgument() != None:
					self.PrepareArgument(link.GetArgument(), result)
				else:
					self.PrepareSetting(link.GetSetting(), result)
				ret = True
		return ret


	def AddIncomingLink(self, parent, argument=None, setting=None, linkType=LinkTypes.required, shouldProliferate=True):
		self._incomingLinks.append(Link(parent, self, argument, setting, linkType))
		return True


	def RemoveIncomingLink(self, parent, argument=None, setting=None, shouldProliferate=True):
		for link in self._incomingLinks:
			if link.GetParent() == parent and link.GetSetting() == setting:
				self._incomingLinks.remove(link)
				return True
		return False

	
	def GetAllIncomingLinks(self):
		return self._incomingLinks


	def GetIncomingLinks(self, parent):
		return [link for link in self._incomingLinks if link.GetParent() == parent]


	def PrepareArgument(self, position, value):
		logger.info("Preparing argument: " + str(position) + " = " + str(value))

		if position == None:
			return

		if position.__class__ == int:
			self._runtimeArgs[position] = value
		else:
			self._runtimeKWArgs[position] = value


	def PrepareSetting(self, position, value):
		logger.info("Preparing setting: " + str(position) + " = " + str(value))
		if position == None:
			return

		if position.__class__ == int:
			self._settingsArgs[position] = value
		else:
			self._settingsKWArgs[position] = value


	def IsRunnable(self):
		requiredParents = [parent.GetParent() for parent in self._incomingLinks \
							if parent.GetType == LinkTypes.required]
		isRunnable = set(requiredParents).issubset(set(self._parentsReady))

		logger.info("is " + str(self._id) + "." + str(self._runnableStateType.__name__) + " runnable? " + str(isRunnable) + "; Ready parents: " + str(self._parentsReady))

		return isRunnable


	def Run(self):
		if not self.IsRunnable():
			return

		logger.info("Running state: " + self._runnableStateType.__name__)
		logger.info("        Args: " + str(self._runtimeArgs) + str(self._runtimeKWArgs))

		self._parentsReady = [] #TODO: decide what I want my on failure behavior to be, this may need to move.
		#Terribly sloppy, but _call_ won't work because we want to allow callable functions
		if self._runnableStateType.__class__.__name__ != "function":
			runnableState = self._runnableStateType(*(self._settingsArgs), **(self._settingsKWArgs))
		else:
			runnableState = self._runnableStateType
		result = runnableState(*(self._runtimeArgs), **(self._runtimeKWArgs))

		nextStates = self.GetNextStates()
		for nextState in nextStates:
			nextState.AcceptIncomingResult(self, result)
			#TODO: if I wanted this to be efficient, I could return a value from Accept, and not double call unless ready.
			nextState.Run()


	def __call__(self):
		return self.Run()


	def GetNextStates(self):
		return set(self._nextStates)


	#TODO: it's a bit bad that you just have to "know" to only use the outgoing operations, not incoming.  fix that.
	def AddOutgoingLink(self, nextState, argument=None, setting=None, linkType=LinkTypes.required, shouldProliferate=True):
		nextState.AddIncomingLink(self, argument, setting, linkType, shouldProliferate)
		self._nextStates.append(nextState)


	def RemoveOutgoingLink(self, nextState, argument=None, setting=None, shouldProliferate=True):
		nextState.RemoveIncomingLink(self, argument, setting, shouldProliferate)
		self._nextStates.remove(nextState)


	def GetAvailableSettings(self):
		try:
			return self._runnableStateType.__init__.__code__.co_varnames[1:] # Init arguments after self
		except:
			pass
		return []


	def GetAvailableArgs(self):
		try:
			return self._runnableStateType.__call__.__code__.co_varnames[1:]
		except:
			pass
		return self._runnableStateType.__code__.co_varnames


	def GetPopulatedSettings(self):
		defaults = {}
		if self._runnableStateType.__class__.__name__ != "function":
			argspec = inspect.getargspec(self._runnableStateType.__init__)
			defaults = {}
			if argspec.defaults:
				defaults = {key:val for key, val in zip(argspec.args[-len(argspec.defaults):], argspec.defaults)}

		args = defaults
		args.update({index:arg for index, arg in enumerate(self._settingsArgs)})
		args.update(self._settingsKWArgs)
		return args


	def GetPopulatedArgs(self):
		defaults = {}
		target = self._runnableStateType
		if target.__class__.__name__ != "function":
			target = target.__call__

		argspec = inspect.getargspec(target)
		defaults = {}
		if argspec.defaults:
			defaults = {key:val for key, val in zip(argspec.args[-len(argspec.defaults):], argspec.defaults)}

		settings = defaults
		settings.update({index:arg for index, arg in enumerate(self._runtimeArgs)})
		settings.update(self._runtimeKWArgs)
		return settings


	def GetTypeId(self):
		return self._availableStateTypesReverseIndex[self._runnableStateType]


	def GetId(self):
		return self._id


	def GetRemoteId(self):
		return self._id


	def GetRemoteUri(self):
		return Api.GetMyUri()


	def SetArbitraryData(self, key, value):
		self._arbitraryData[key] = value


	def GetArbitraryData(self, key):
		return self._arbitraryData[key]


	def GetAllArbitraryData(self):
		return self._arbitraryData


	def FromSummaryDict(self, summary):
		self._id = summary["stateId"]
		self._runnableStateType = self._availableStateTypes[summary["typeId"]]
		# TODO: store current settings, has a LOT of caveats especially re: defaults, though.
		self._arbitraryData = summary["arbitraryData"]


	def GetSummaryDict(self):
		incomingLinks = \
			[{"parent":link.GetParent().GetId(), "argument":link.GetArgument(), "linkType":link.GetType(), "setting":link.GetSetting()} \
				for link in self._incomingLinks]

		# TODO: FIXME: Make sure this does the right thing for a remote state.
		return {"stateId":self.GetId(), \
			"typeId":self.GetTypeId(), \
			"args":self.GetAvailableArgs(), \
			"settings":self.GetAvailableSettings(), \
			"populatedSettings":self.GetPopulatedSettings(), \
			"populatedArgs":self.GetPopulatedArgs(), \
			"incomingLinks":incomingLinks, \
			"arbitraryData":self.GetAllArbitraryData()}


class RemoteState(MetaState):
	def __init__(self, targetUri, remoteStateId, remoteTypeId=None, remoteSettings=[], remoteArguments=[]):
		self._targetApi = Api(targetUri)
		self._remoteId = remoteStateId

		self._remoteSettings = remoteSettings
		self._remoteArguments = remoteArguments

		self._remoteTypeId = remoteTypeId

		super(RemoteState, self).__init__(None)


	def LoadFromRemote(self):
		remoteStateData = self._targetApi.call(GetState, remoteStateId)
		self._remoteSettings = remoteStateData["settings"]
		self._remoteArguments = remoteStateData["args"]
		self._remoteTypeId = remoteStateData["typeId"]
		if ("remoteUri" in remoteStateData):
			self._targetApi = Api(remoteStateData["remoteUri"])
			self._remoteId = remoteStateData["remoteId"]

		#TODO: do I want this?
		super(RemoteState, self).__init__(None)



	def AcceptIncomingResult(self, parent, result):
		if isinstance(parent, RemoteState):
			self._targetApi.call(api.AcceptResult, json.dumps(result), self._remoteId, parent.GetRemoteId(), parent.GetRemoteIp())
		else:
			self._targetApi.call(api.AcceptResult, json.dumps(result), self._remoteId, parent.GetId(), Api.GetMyUri())


	def AddIncomingLink(self, parent, argument=None, setting=None, linkType=LinkTypes.required, shouldProliferate=True):
		#TODO: if two remote nodes are linked and talk to the same target, it
		#will call link to that target twice.  make sure this is idempotent, and it'll be fine for now.
		#It'll also think one of its own nodes is a remote node, should probably fix that too.

		if shouldProliferate:
			self._targetApi.call(api.AddRemoteState, \
				parent.GetRemoteUri(), \
				parent.GetRemoteId(), \
				parent.GetTypeId(), \
				json.dumps(parent.GetAvailableSettings()), \
				json.dumps(parent.GetAvailableArgs()))
			self._targetApi.call(api.LinkStates, \
				parent.GetRemoteId(), \
				self.GetRemoteId(), \
				parent.GetRemoteUri(), \
				argument=argument, \
				setting=setting, \
				linkType=linkType)

		super(RemoteState, self).AddIncomingLink(parent, argument, setting, linkType, shouldProliferate)


	def RemoveIncomingLink(self, parent, argument=None, setting=None, shouldProliferate=True):
		if shouldProliferate:
			self._targetApi.call(api.UnlinkStates, \
				parent.GetRemoteId(), \
				self.GetRemoteId(), \
				parent.GetRemoteUri(), \
				argument=argument, \
				setting=setting)

		super(RemoteState, self).RemoveIncomingLink(parent, argument, setting, shouldProliferate)
	

	def PrepareArgument(self, position, value):
		self._targetApi.call(api.PrepareArgument, self._remoteId, position, value)


	def PrepareSetting(self, position, value):
		self._targetApi.call(api.PrepareSetting, self._remoteId, position, value)


	def IsRunnable(self):
		return self._targetApi.call(api.IsRunnable, self._remoteId)


	def Run(self):
		logger.info("Running remote state: " + str(self._remoteId))
		self._targetApi.call(api.Run, self._remoteId)


	def AddOutgoingLink(self, nextState, argument=None, setting=None, linkType=LinkTypes.required, shouldProliferate=True):
		if shouldProliferate:
			self._targetApi.call(api.AddRemoteState, \
				nextState.GetRemoteUri(), \
				nextState.GetRemoteId(), \
				nextState.GetTypeId(), \
				json.dumps(nextState.GetAvailableSettings()), \
				json.dumps(nextState.GetAvailableArgs()))
			self._targetApi.call(api.LinkStates, \
				self.GetRemoteId(), \
				nextState.GetRemoteId(), \
				childStateIp=nextState.GetRemoteUri(), \
				argument=argument, \
				setting=setting, \
				linkType=linkType)

		super(RemoteState, self).AddOutgoingLink(nextState, argument, setting, linkType, shouldProliferate)


	def RemoveOutgoingLink(self, nextState, argument=None, setting=None, shouldProliferate=True):
		if shouldProliferate:
			self._targetApi.call(api.UnlinkStates, \
				self.GetRemoteId(), \
				nextState.GetRemoteId(), \
				childStateIp=nextState.GetRemoteUri(), \
				argument=argument, \
				setting=setting)

		super(RemoteState, self).RemoveOutgoingLink(nextState, argument, setting, shouldProliferate)


	def GetAvailableSettings(self):
		return self._remoteSettings


	def GetAvailableArgs(self):
		return self._remoteArguments


	def GetPopulatedSettings(self):
		return self._targetApi.call(api.GetPopulatedSettings, self.GetRemoteId())


	def GetPopulatedArgs(self):
		return self._targetApi.call(api.GetPopulatedArgs, self.GetRemoteId())


	def GetTypeId(self):
		return self._remoteTypeId


	def GetRemoteId(self):
		return self._remoteId


	def GetRemoteUri(self):
		return self._targetApi.GetTargetUri()


	def SetArbitraryData(self, key, value):
		self._targetApi.call(api.SetArbitraryData, self.GetRemoteId(), key, value)


	def GetArbitraryData(self, key):
		return self._targetApi.call(api.GetArbitraryData, self.GetRemoteId(), key)


	def GetSummaryDict(self):
		summary = super(RemoteState, self).GetSummaryDict()
		summary["remoteId"] = self.GetRemoteId()
		summary["remoteUri"] = self.GetRemoteUri()
		return summary


	def FromSummaryDict(self, summary):
		self._remoteId = summary["remoteId"]
		self._remoteUri = summary["remoteUri"]

		super(RemoteState, self).FromSummaryDict(summary)
