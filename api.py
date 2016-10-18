import json
import threading

from util import registerApi
from routes import webapp
from link import LinkTypes

stateMachineInstance = None

@registerApi("/AddRemoteState?<remoteIp>&<remoteStateId>&<remoteStateType>&<remoteSettings>&<remoteArguments>", webapp.put, "PUT")
@registerApi("/AddRemoteState?<remoteIp>&<remoteStateId>", webapp.put, "PUT")
#TODO: if args not provided, do the get from here.
def AddRemoteState(remoteIp, remoteStateId, remoteStateType=None, remoteSettings=None, remoteArguments=None):
	if remoteSettings:
		remoteSettings = json.loads(remoteSettings)
	if remoteArguments:
		remoteArguments = json.loads(remoteArguments)

	remoteStateId = int(remoteStateId)
	state = stateMachineInstance.AddRemoteState(remoteIp, remoteStateId, remoteStateType, remoteSettings, remoteArguments)
	if remoteStateType == None:
		state.LoadFromRemote()

	return state.GetSummaryDict()


@registerApi("/AddState?<stateTypeId>", webapp.put, "PUT")
def AddState(stateTypeId):
	stateType = stateMachineInstance.GetAvailableStateTypes()[stateTypeId]
	state = stateMachineInstance.AddState(stateType)
	settings = state.GetAvailableSettings()
	args = state.GetAvailableArgs()
	return state.GetSummaryDict()


@registerApi("/RemoveState?<stateId>", webapp.put, "PUT")
def RemoveState(stateId):
	stateId = int(stateId)
	stateMachineInstance.RemoveState(stateId)
	return {}


@registerApi("/LinkStates?<parentStateIp>&<parentStateId>&<childStateIp>&<childStateId>&<argument>&<linkType>", webapp.put, "PUT")
@registerApi("/LinkStates?<parentStateIp>&<parentStateId>&<childStateIp>&<childStateId>&<setting>&<linkType>", webapp.put, "PUT")
@registerApi("/LinkStates?<parentStateIp>&<parentStateId>&<childStateIp>&<childStateId>&<linkType>", webapp.put, "PUT")
@registerApi("/LinkStates?<parentStateIp>&<parentStateId>&<childStateIp>&<childStateId>&<argument>", webapp.put, "PUT")
@registerApi("/LinkStates?<parentStateIp>&<parentStateId>&<childStateIp>&<childStateId>&<setting>", webapp.put, "PUT")
@registerApi("/LinkStates?<parentStateIp>&<parentStateId>&<childStateIp>&<childStateId>", webapp.put, "PUT")
@registerApi("/LinkStates?<parentStateId>&<childStateIp>&<childStateId>&<argument>&<linkType>", webapp.put, "PUT")
@registerApi("/LinkStates?<parentStateId>&<childStateIp>&<childStateId>&<setting>&<linkType>", webapp.put, "PUT")
@registerApi("/LinkStates?<parentStateId>&<childStateIp>&<childStateId>&<linkType>", webapp.put, "PUT")
@registerApi("/LinkStates?<parentStateId>&<childStateIp>&<childStateId>&<argument>", webapp.put, "PUT")
@registerApi("/LinkStates?<parentStateId>&<childStateIp>&<childStateId>&<setting>", webapp.put, "PUT")
@registerApi("/LinkStates?<parentStateId>&<childStateIp>&<childStateId>", webapp.put, "PUT")
@registerApi("/LinkStates?<parentStateIp>&<parentStateId>&<childStateId>&<argument>&<linkType>", webapp.put, "PUT")
@registerApi("/LinkStates?<parentStateIp>&<parentStateId>&<childStateId>&<setting>&<linkType>", webapp.put, "PUT")
@registerApi("/LinkStates?<parentStateIp>&<parentStateId>&<childStateId>&<linkType>", webapp.put, "PUT")
@registerApi("/LinkStates?<parentStateIp>&<parentStateId>&<childStateId>&<argument>", webapp.put, "PUT")
@registerApi("/LinkStates?<parentStateIp>&<parentStateId>&<childStateId>&<setting>", webapp.put, "PUT")
@registerApi("/LinkStates?<parentStateIp>&<parentStateId>&<childStateId>", webapp.put, "PUT")
@registerApi("/LinkStates?<parentStateId>&<childStateId>&<argument>&<linkType>", webapp.put, "PUT")
@registerApi("/LinkStates?<parentStateId>&<childStateId>&<setting>&<linkType>", webapp.put, "PUT")
@registerApi("/LinkStates?<parentStateId>&<childStateId>&<linkType>", webapp.put, "PUT")
@registerApi("/LinkStates?<parentStateId>&<childStateId>&<argument>", webapp.put, "PUT")
@registerApi("/LinkStates?<parentStateId>&<childStateId>&<setting>", webapp.put, "PUT")
@registerApi("/LinkStates?<parentStateId>&<childStateId>", webapp.put, "PUT")
def LinkStates(parentStateId, childStateId, parentStateIp=None, childStateIp=None, linkType=LinkTypes.required, argument=None, setting=None):
	parentStateId = int(parentStateId)
	childStateId = int(childStateId)

	shouldProliferate=True

	if parentStateIp:
		try:
			parentState = stateMachineInstance.GetRemoteState(parentStateIp, parentStateId)
		except:
			parentState = stateMachineInstance.AddRemoteState(parentStateIp, parentStateId)
		parentStateId = parentState.GetId()
		shouldProliferate=False

	if childStateIp:
		try:
			childState = stateMachineInstance.GetRemoteState(childStateIp, childStateId)
		except:
			childState = stateMachineInstance.AddRemoteState(childStateIp, childStateId)
		childStateId = childState.GetId()
		shouldProliferate=False

	stateMachineInstance.LinkStates(parentStateId, childStateId, argument, setting, linkType, shouldProliferate)
	return {}


@registerApi("/UnlinkStates?<parentStateIp>&<parentStateId>&<childStateIp>&<childStateId>&<argument>", webapp.put, "PUT")
@registerApi("/UnlinkStates?<parentStateIp>&<parentStateId>&<childStateIp>&<childStateId>&<setting>", webapp.put, "PUT")
@registerApi("/UnlinkStates?<parentStateIp>&<parentStateId>&<childStateIp>&<childStateId>", webapp.put, "PUT")
@registerApi("/UnlinkStates?<parentStateId>&<childStateIp>&<childStateId>&<argument>", webapp.put, "PUT")
@registerApi("/UnlinkStates?<parentStateId>&<childStateIp>&<childStateId>&<setting>", webapp.put, "PUT")
@registerApi("/UnlinkStates?<parentStateId>&<childStateIp>&<childStateId>", webapp.put, "PUT")
@registerApi("/UnlinkStates?<parentStateIp>&<parentStateId>&<childStateId>&<argument>", webapp.put, "PUT")
@registerApi("/UnlinkStates?<parentStateIp>&<parentStateId>&<childStateId>&<setting>", webapp.put, "PUT")
@registerApi("/UnlinkStates?<parentStateIp>&<parentStateId>&<childStateId>", webapp.put, "PUT")
@registerApi("/UnlinkStates?<parentStateId>&<childStateId>&<argument>", webapp.put, "PUT")
@registerApi("/UnlinkStates?<parentStateId>&<childStateId>&<setting>", webapp.put, "PUT")
@registerApi("/UnlinkStates?<parentStateId>&<childStateId>", webapp.put, "PUT")
def UnlinkStates(parentStateId, childStateId, parentStateIp=None, childStateIp=None, argument=None, setting=None):
	parentStateId = int(parentStateId)
	childStateId = int(childStateId)

	shouldProliferate=True

	if parentStateIp:
		parentState = stateMachineInstance.GetRemoteState(parentStateIp, parentStateId)
		parentStateId = parentState.GetId()
		shouldProliferate=False

	if childStateIp:
		childState = stateMachineInstance.GetRemoteState(childStateIp, childStateId)
		childStateId = childState.GetId()
		shouldProliferate=False

	stateMachineInstance.UnlinkStates(parentStateId, childStateId, argument, setting, shouldProliferate)
	return {}



@registerApi("/PrepareArgument?<stateId>&<position>&<value>", webapp.put, "PUT")
def PrepareArgument(stateId, position, value):
	stateId = int(stateId)
	stateMachineInstance.GetState(stateId).PrepareArgument(position, value)
	return {}


@registerApi("/PrepareSetting?<stateId>&<position>&<value>", webapp.put, "PUT")
def PrepareSetting(stateId, position, value):
	stateId = int(stateId)
	stateMachineInstance.GetState(stateId).PrepareSetting(position, value)
	return {}


@registerApi("/AcceptResult?<targetStateId>&<parentStateIp>&<parentStateId>&<result>", webapp.put, "PUT")
@registerApi("/AcceptResult?<targetStateId>&<parentStateId>&<result>", webapp.put, "PUT")
def AcceptResult(result, targetStateId, parentStateId, parentStateIp=None):
	targetStateId = int(targetStateId)
	parentStateId = int(parentStateId)
	if parentStateId:
		parentState = stateMachineInstance.GetRemoteState(parentStateIp, parentStateId)
	else:
		parentState = stateMachineInstance.GetState(parentStateId)

	targetState = stateMachineInstance.GetState(targetStateId)
	targetState.AcceptIncomingResult(parentState, json.loads(result))
	return {}


@registerApi("/Run?<stateId>", webapp.put, "PUT")
@registerApi("/Run", webapp.put, "PUT")
def Run(stateId=None):
	if stateId:
		stateId = int(stateId)

	stateMachineInstance.Run(stateId)
	return {}


@registerApi("/IsRunnable?<stateId>", webapp.get)
def IsRunnable(stateId):
	stateId = int(stateId)
	return {"isRunnable":stateMachineInstance.GetState(stateId).IsRunnable()}


@registerApi("/GetStateGraph", webapp.get)
def GetStateGraph():
	graph = stateMachineInstance.GetStateGraph()
	print(graph)
	return graph


@registerApi("/GetAvailableStateTypes", webapp.get)
def GetAvailableStateTypes():
	return {index:stateType.__name__ for index, stateType in stateMachineInstance.GetAvailableStateTypes().items()}


@registerApi("/GetAvailableLinkTypes", webapp.get)
def GetAvailableLinkTypes():
	#FIXME: really terrible way of faking a list for JS, but {"linkTypes":[]} only seems marginally better.
	return {link:link for link in LinkTypes.GetAvailableLinkTypes()}


@registerApi("/GetStateSettings?<stateId>", webapp.get)
def GetStateSettings(stateId):
	stateId = int(stateId)
	return stateMachineInstance.GetState(stateId).GetAvailableSettings()


@registerApi("/GetStateArgs?<stateId>", webapp.get)
def GetStateArgs(stateId):
	stateId = int(stateId)
	return stateMachineInstance.GetState(stateId).GetAvailableArgs()


@registerApi("/GetPopulatedStateSettings?<stateId>", webapp.get)
def GetPopulatedSettings(stateId):
	stateId = int(stateId)
	return stateMachineInstance.GetState(stateId).GetPopulatedSettings()


@registerApi("/GetPopulatedStateArgs?<stateId>", webapp.get)
def GetPopulatedArgs(stateId):
	stateId = int(stateId)
	return stateMachineInstance.GetState(stateId).GetPopulatedArgs()


@registerApi("/GetState?<stateId>", webapp.get)
def GetState(stateId):
	stateId = int(stateId)
	return stateMachineInstance.GetState(stateId).GetSummaryDict()


@registerApi("/SetArbitraryData?<stateId>&<key>&<value>", webapp.put, "PUT")
def SetArbitraryData(stateId, key, value):
	stateId = int(stateId)
	stateMachineInstance.GetState(stateId).SetArbitraryData(key, value)


@registerApi("/GetArbitraryData?<stateId>&<key>", webapp.get, "GET")
def GetArbitraryData(stateId, key):
	stateId = int(stateId)
	return stateMachineInstance.GetState(stateId).GetArbitraryData(key)

