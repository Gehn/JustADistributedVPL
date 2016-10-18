
class LinkTypes:
	required = "required"
	optional = "optional"

	@staticmethod
	def GetAvailableLinkTypes():
		return [getattr(LinkTypes, attr) for attr in dir(LinkTypes) \
						if not hasattr(getattr(LinkTypes, attr), "__call__") and not attr.startswith("_")]


class Link:
	def __init__(self, parent, child, argument=None, setting=None, linkType=LinkTypes.required):
		self._linkType = linkType
		self._parent = parent
		self._child = child
		self._argument = argument
		self._setting = setting


	def GetParent(self):
		return self._parent


	def GetChild(self):
		return self._child


	def GetArgument(self):
		return self._argument


	def GetSetting(self):
		return self._setting


	def GetType(self):
		return self._linkType


	#TODO: something feels slightly off about having this here instead of in StateMachine.
	def Remove(self):
		if self._argument:
			self._parent.RemoveOutgoingLink(self._child, self._argument, self._setting)
		
