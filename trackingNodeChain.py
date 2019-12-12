
# projectTags: TRACKING TREE, infoTree, DATA SCIENCE, MACHINE LEARNING, SIMI RECUSIVE PROCESS

# Object that Travese any tree structure using a stack for back tracking the traversal process
# Purpose: Purpose to traverse json objects using a stack (LIFO) to backtrack the travesal process, hence simulating recursive process				  # nodeChain to build a sort of node travesal history buffer
# requirement: MUST HAVE convertToDict function so that the infoTree can be converted and stored in a dictonary and thereby be converted to json and used in noSQL Database and/or SIEM System
#			   for faster data analysis.
# TODO: Implement support for all object types, dict, list, str, number, so it can handle any jsonObject structure of nested og linked objects
# STATUS: (DONE)

# METHOD (Tree Travesal using a nodeChain):
# Simulate stack by building a nodeChain "linked list" where a pop() method returns self.prevNode "prev trackingNode", this way i can backtrack nodeChain instead of a tree
# Basically the same as trackingStack just using simi-recursive method to build and backtrack the nodeChain
# self.push => self.nextNode = "pushed node"

import json
import xmltodict
from collections import OrderedDict
# import xmltodict

# Object that can be used to maintain chain of trackingNodes
# STATUS: TESTED, WORKS, DONE
class trackingStack:
	def __init__(self):
		self.node_ = "" # Current nextNode
		self.treeTraversed_ = False # Flag signaling when the node tree has been Traversed
	
	# Method to add a new item to the stack
	# Note nodeIx = -1 => no prevNode hence this is first childNode
	def pushNode(self, node_):
		# Is trackingStack empty?
		if self.node_ == "":
			#Y => Add new rootNode
			self.node_ = trackingNode(node_.key_, node_.value_, node_.nodeIx_, node_.childNodeIx_, node_.prevNode_, node_.nextNode_)
			#return self
			return self

		# Assume trackingStack is not empty		
		# Add new trackingNode to the trackingStack
		# push new trackingNode on stack
		self.node_ = self.node_.pushNode(node_.key_, node_.value_, node_.nodeIx_, node_.childNodeIx_, node_.prevNode_, node_.nextNode_)

		return self

	# Method To look at the the first node on the stack
	def peekFirstNode(self):
		# Is trackingStack empty?
		if self.node_ == "":
			#Y => return empty
			return ""

		# Assume trackingStack is not empty		
		#"N" => return rootNode
		return self.node_.getRootNode()

	# Method to look a last node on the stack
	def peekNode(self):
		# Is trackingStack empty?
		if self.node_ == "":
			#Y => return empty
			return ""

		# Assume trackingStack is not empty		
		#"N" => Return leafNode
		return self.node_.getLeafNode()

	# Method to copy last trackingNode in stack
	def copyNode(self):
		# Is trackingStack empty?
		if self.node_ == "":
			#Y => return empty
			return ""

		# Assume trackingStack is not empty		
		#"N" => Get leafNode
		thisNode = self.node_.getLeafNode()
		# Return copy of leafNode
		myTrackingNode = thisNode.copyNode()

		return myTrackingNode

	# Method to remove last node from the stack "Back tracking process"
	def popNode(self):
		# Is trackingStack empty?
		if self.node_ == "":
			#Y => return empty
			return ""

		# Assume trackingStack is not empty		
		#"N" => backtrack nodeChain
		self.node_ = self.node_.popNode()

		# return nextNode
		return self.node_

	#Methods that auto detects the itemClass "Object type"
	def isDict(self, value_=""):
		# Is trackingStack empty?
		if self.node_ == "":
			#Y => return empty
			return ""

		# Assume trackingStack is not empty
		return self.node_.isDict(value_)

	def isOrderedDict(self, value_=""):
		# Is trackingStack empty?
		if self.node_ == "":
			#Y => return empty
			return ""

		# Assume trackingStack is not empty
		return self.node_.isOrderedDict(value_)
			
	def isList(self, value_=""):
		# Is trackingStack empty?
		if self.node_ == "":
			#Y => return empty
			return ""

		# Assume trackingStack is not empty
		return self.node_.isList(value_)

	def isString(self, value_=""):
		# Is trackingStack empty?
		if self.node_ == "":
			#Y => return empty
			return ""

		# Assume trackingStack is not empty		
		return self.node_.isString(value_)

	def isNumber(self, value_=""):
		# Is trackingStack empty?
		if self.node_ == "":
			#Y => return empty
			return ""

		# Assume trackingStack is not empty	
		return self.node_.isNumber(value_)	

	# method that returns wether a given node is a leafNode, hence contains a simple object fx, str, int, dbl or dict/list with one item etc
	def isLeafNode(self):
		# Is trackingStack empty?
		if self.node_ == "":
			#Y => return empty
			return ""

		# Assume trackingStack is not empty
		#"N" => auto discover node type
		return self.node_.isLeafNode()
		
	# method that returns wether a given node is a simple leafNode, hence contains a simple object fx, str, int, dbl etc
	def isSimpleLeafNode(self):
		# Is trackingStack empty?
		if self.node_ == "":
			#Y => return empty
			return ""

		# Assume trackingStack is not empty		
		#"N" => auto discover node type
		return self.node_.isSimpleLeafNode()

	# Method used to print leafNodes
	def printLeafNode(self):
		# Is trackingStack empty?
		if self.node_ == "":
			#Y => return empty
			return

		# Assume trackingStack is not empty		
		#"N" => print the node
		print(self.node_.getString())		
		return

	# Method used to signal Tree travesal restart, hence reset Tree Traversal Complete flag
	def restart(self):
		# Reset Tree Traversed flag
		self.treeTraversed_ = False
		return

    # -------- NODE TREE TRAVERSAL METHODS -------
	# Method used to traverse the json infoTree object or or sub-infoTree relative to startNode in forward direction
	# STATUS: DONE->TESTED->WORKS!!
	def getNextNode(self, startNode_=""):
		# Is trackingStack empty?
		if self.node_ == "":
			#Y => return empty
			return ""

		# Assume trackingStack is not empty		
		#"N" => get nextNode
		self.node_ = self.node_.getNextNode(startNode_)

		# Has Tree been traversed?
		if self.node_ == "":
			#Y => Signal tree traversed
			self.treeTraversed_ = True

		# Return trackingStack
		return self
			
	# Method used to traverse the json infoTree object or or sub-infoTree relative to startNode in backward direction
	# STATUS: DONE->TESTED->NOT WORKING AS EXPECTED!!
	def getPrevNode(self, startNode_=""):
		# Is trackingStack empty?
		if self.node_ == "":
			#Y => return empty
			return ""

		# Assume trackingStack is not empty		
		#"N" => get nextNode
		self.node_ = self.node_.getPrevNode(startNode_)

		# Has trr been traversed?
		if self.node_ == "":
			#Y => Signal tree traversed
			self.treeTraversed_ = True
				
		# Return trackingStack
		return self

    # ----------------- NODE SEARCH METHODS ---------
    # Method used to find a item with the given Dict Key, handy when trying the getPrevNode method
	# OBS: This node is meant for traversal only to edit json Object use the jsonObject class
	def getNodeByKey(self, key_, startNode_ = ""):
		# Is trackingStack empty?
		if self.node_ == "":
			#Y => return empty
			return ""

		# Assume trackingStack is not empty		
		#"N" => find the node
		return self.node_.getNodeByKey(key_, startNode_)
	
	# ----- NODE ITEM TYPE AUTO DISCOVER ---------
	def getName(self):
		# Is trackingStack empty?
		if self.node_ == "":
			#Y => return empty
			return ""

		# Assume trackingStack is not empty		
		#"N" => get name
		return self.node_.getName()
		
	#------- END ITEM TYPE AUTO DISCOVER -----
			
# Object that contains info about one item
# Note nodeIx = -1 => no prevNode hence this is first childNode
# STATUS: TESTED, WORKS, DONE
class trackingNode:
	def __init__(self, key_, value_, nodeIx_ = 0, childNodeIx_=-1, prevNode_ = "", nextNode_="", nodeLevelSeparator_="."):
		self.prevNode_ = prevNode_ # prevNode of this trackingNode
		self.nextNode_ = nextNode_ # nextNode of this trackingNode
		self.nodeId_ = "" # Auto calgulated nodeId, ensures this exact node can be located using this id
		self.nodeLevelSeparator_ = nodeLevelSeparator_ # Node level seperator used in this nodeTree, def. = "."
		self.key_ = key_
		self.value_ = value_
		self.nodeIx_ = nodeIx_
		self.childNodeIx_ = childNodeIx_ # nodeIx of current childNode of thisNode, beeing processed, -1 = no nodes processed yet
		self.lastChildNodeIx_ = -1	# last childNode ix, used to detect leafNodes
		self.type_ = 0 # Specifies the type of object thisNode contains
		# requires all affected nodes rootOffset_ is recalgulated when nodes are added, removed and moved!!
		# 0 = OrderedDict, 1 = List "Array", 2 = String, 3 = number		

		# Auto Discover Object Type
		# Does thisNode contain a OrderedDict Object?
		if self.isOrderedDict():
			#Y => Signal thisNode contains orderedDict object
			self.type_ = 0

		# Does thisNode contain a list obejct?
		if self.isList():
			#Y => Signal thisNode contains list object
			self.type_ = 1

		# Does thisNode contain a string object
		if self.isString():
			#Y => Signal thisNode contains a string object
			self.type_ = 2

		if self.isNumber():
			#Y => Signal thisNode contains a number object?
			self.type_ = 3		

		# Calc nodeId and nodeLevel based on parrentNode
		# Is thsNode the rootNode?
		if self.prevNode_ == "":
			#Y => THis is root, hence nodeLevel 0
			self.nodeLevel_ = 0 # Specifies what level this node is at in a Tree structure
			self.nodeId_ = "root"
		else:
			# Is prevNode thisNodes parrentNode?
			# Is prevNode a OrderedDict Object?
			if prevNode_.isOrderedDict():
				#Y => Is thisItem a childItem of prevNode?
				if self.value_ in prevNode_.value_.values():
					#Y
					thisParrentNode = prevNode_
				else:
					#N => Find correct parrentNode for thisNode
					# Find thisNodes parrent "Ensure jsonTree is in sync with json object structure"
					thisParrentNode = self.getParrentNode()					

			# Is prevNode a List Object?
			if prevNode_.isList():
				#Y => Is thisItem a childItem of prevNode?
				if self.value_ in prevNode_.value_:
					#Y
					thisParrentNode = prevNode_
				else:
					#N => Find correct parrentNode for thisNode					
					# Find thisNodes parrent "Ensure jsonTree is in sync with json object structure"
					thisParrentNode = self.getParrentNode()

			# Update nodeLevel (Keeps track of what level in the infoTree thisNode is at)
			self.nodeLevel_ = thisParrentNode.nodeLevel_ + 1
			# Generate new key "NodeId" using the nodes location in the tree
			self.nodeId_ = thisParrentNode.nodeId_ + self.nodeLevelSeparator_ + str(self.nodeIx_)

		# Is this trackingNode containing a simple leafNode
		if not self.isSimpleLeafNode():
			#N => assume it contains a dict or list object
			#**if self.isOrderedDict():
			# Calc last childNodeIx
			self.lastChildNodeIx_ = len(self.value_) - 1

	# Method to fin dthe parrentNode of thisNode
#**	def getParrentNode(self):
		# set startNode
#**		thisNode = self

		# Loop until the parrent has been located
#**		while(thisNode != ""):
			# Backtrack nodeStack
#**			thisNode = thisNode.prevNode_

			# Is this the parrentNode?
			

	# Method to push a new node on the stack "add node to chain"
	def pushNode(self, key_, value_, nodeIx_ = 0, childNodeIx_ = -1, prevNode_ ="", nextNode_ = ""):
		# Get rootNode
		thisNode = self.getRootNode()

		# Does newNode allready Exist trackingNodeChain?
		while(thisNode != ""):
			# Is the key we are looking for?
			if thisNode.key_ == key_:
				# Is the ix we are looking for?
				if thisNode.nodeIx_ == nodeIx_:
					#Y => Is this the Item we are looking for?
					if thisNode.value_ == value_:
						#Y => Reject attempt to push existing node and just update the existing node
						thisNode.nodeIx_ = nodeIx_
						thisNode.childNodeIx_ = childNodeIx_
						#Return existing node
						return thisNode

			# Try next node
			thisNode = thisNode.nextNode_

		# Get rootNode
		thisNode = self.getRootNode()		

		# Create new tracking node with thisNode as its prevNode
		newNode = trackingNode(key_, value_, nodeIx_, childNodeIx_, self, "")

		# Loop until all nodes checked
		# Calc newNode nodeLevel [UNREQUIRED the constructor allready performs this task]
		#newNode.getNodeLevel()

	# ---- [UNREQUIRED NODE EXISTENSE ALLREADY CHEKED EARLIER]
#		while(thisNode != ""):
		# Has thisNode allready been added?
			# Is thisNode similar to newNode?
#			if thisNode.key_ == newNode.key_:
#				if thisNode.nodeIx_ == newNode.nodeIx_:
#					if thisNode.nodeLevel_ == newNode.nodeLevel_:
#						if thisNode.value_ == value_:
							# Assume thisNode allready exists, hence update existing node
#							thisNode.childNodeIx_ = newNode.childNodeIx_
#							thisNode.nextNode_ = newNode.nextNode_

							# Unlink newNode from the nodeChain
#							newNode.nextNode_ = ""
#							newNode.prevNode_ = ""
							
							# Retun existing node
#							return thisNode

			# Try next node
#			thisNode = thisNode.nextNode_

		# Assume thisNode does not exists			

		# Link thisNode to newNode
		self.nextNode_ = newNode

		# Return the new leafNode of the stack
		return newNode

	# Method to pop last/leafNode from the stack
	def popNode(self):
		# Is stack empty
		if self.prevNode_ == "" and self.nextNode_ == "":
			#Y => Signal stack empty, hence return empty
			return ""

		# Assume stack is not empty
		# Find leafNode
		thisNode = self
		while(thisNode != ""):
			# Is this the leafNode?
			if thisNode.nextNode_ == "":
				# Remove node from the stack
				# Is thisNode a rootNode?
				if thisNode.prevNode_ != "":
					# Move to prevNode
					thisNode = thisNode.prevNode_
					#N => Remove prevNodes link to "thisNode"
					thisNode.nextNode_ = ""
					 

				#Y => signal leafNode found
				return thisNode

			# Try nextNode
			thisNode = thisNode.nextNode_

		# Assume the leafNode was not found
		return thisNode

	# Method to look at this thisNodes value in stack
	def peekValue(self):
		return self.value_

	# Method to look a this trackingNode in stack
	def peekNode(self):
		return self

	# Method to copy this trackingNode in stack
	def copyNode(self):
		myTrackingNode = trackingNode(self.key_, self.value_, self.nodeIx_,
											self.childNodeIx_, self.prevNode_, self.nextNode_)
		return myTrackingNode

	# Method to manually update childNodeIx it the nodeTree traversal process
	def setChildNodeIx(self, nodeIx_):
		# Update info of this trackingNode
		self.childNodeIx_ = nodeIx_

	#Methods that auto detects the itemClass "Object type"
	def isDict(self, value_=""):
		# Has value been specified?
		if value_ == "":
			#N => Assume thisNodes items should be classified
			value_ = self.value_

		if isinstance(value_, dict):
			return True
		else:
			return False

	def isOrderedDict(self, value_=""):
		# Has item been specified?
		if value_ == "":
			#N => Assume thisNodes items should be classified
			value_ = self.value_

		if isinstance(value_, OrderedDict):
			return True
		else:
			return False			

	def isList(self, value_=""):
		# Has item been specified?
		if value_ == "":
			#N => Assume thisNodes items should be classified
			value_ = self.value_

		if isinstance(value_, list):
			return True
		else:
			return False

	def isString(self, value_=""):
		# Has item been specified?
		if value_ == "":
			#N => Assume thisNodes items should be classified
			value_ = self.value_

		if isinstance(value_, str):
			return True
		else:
			return False

	def isNumber(self, value_=""):
		# Has item been specified?
		if value_ == "":
			#N => Assume thisNodes items should be classified
			value_ = self.value_

		# Is thisItem a simple leafNode?
		if self.isSimpleLeafNode(value_):
			#Y => Is thisItem a number?
			if not isinstance(value_, str):
				#Y
				return True

		# Assume thisItem is not a number
		return False

	# method that returns wether a given node is a leafNode, hence contains a simple object fx, str, int, dbl or dict/list with one item etc
	def isLeafNode(self, node_ = ""):
		# Has node been specified?
		if node_ == "":
			#N => Assume thisNodes item should be checked
			value_ = self.value_
			node_ = self			
		else:
			#N => assume specified nodes value should be checked
			# Is node_ a trackingNode?
			if isinstance(node_, trackingNode):
				# Y => Get thisNodes value
				value_ = node_.value_
			else:
				#N => Assume node is a item value
				value_ = node_
				# Ensure node is allways trackingNode
				node_ = self

		# Is this a dictObject?
		if isinstance(value_, OrderedDict):
			#YES
			# Calc last childNode ix
			lastChildNodeIx	 = len(value_) - 1		
			# Is this a orderedDict Object containg a leafNode "one simple key:value pair"
			if lastChildNodeIx == 0:
				# this childNode a simple leafNode?
				for k, v in value_.items():
					if node_.isSimpleLeafNode(v):
						#Y
						return True
				
				# Assume this dictObject does not contain a simple leafNode
				return False

			# Assume this what not a orderedDict Object containg a simple leafNode
			return False
		
		# Is this a listObject?
		if isinstance(value_, list):
			#YES
			# Calc last childNode ix
			lastChildNodeIx	 = len(value_) - 1			
			# Is this a listObject containg a leafNode "one simple value"
			if lastChildNodeIx == 0:
				#Y 
				# Is this childNode a simple leafNode
				for v in value_:
					if node_.isSimpleLeafNode(v):
						#Y
						return True
			
			# Assume this was not a listObject containing a simple leafNode
			return False

		# Assume this is a leafNode "simple object without childNodes", fx string or number
		return True

	# method that returns wether a given node is a simple leafNode, hence contains a simple object fx, str, int, dbl etc
	def isSimpleLeafNode(self, node_ = ""):
		# Has node been specified?
		if node_ == "":
			#N => Assume thisNodes item should be checked
			value_ = self.value_
			node_ = self
		else:
			#N => assume specified nodes value should be checked
			# is ThisNode a trackingNode
			if isinstance(node_, trackingNode):
				#Y => Assume thisnode value should be checeld
				value_ = node_.value_
			else:
				#N => Assume node is a simple leafNode value
				value_ = node_

		# Is this a dictObject?
		if isinstance(value_, OrderedDict):
			#YES
			return False
		
		# Is this a listObject?
		if isinstance(value_, list):
			#YES
			return False

		# Assume this is a leafNode "simple object without childNodes", fx string or number
		return True

	# Method that detects wether a node is a parrentNode, hence has childNodes "is non leafNode"
	def isParrentNode(self, node_ = ""):
		# Has node been specified?
		if node_ == "":
			#N => Assume thisNodes item should be checked
			value_ = self.value_
			node_ = self
		else:
			#N => assume specified nodes value should be checked
			# is ThisNode a trackingNode
			if isinstance(node_, trackingNode):
				#Y => Assume thisnode value should be checeld
				value_ = node_.value_
			else:
				#N => Assume node is a simple leafNode value
				value_ = node_

		# Is this a dictObject?
		if isinstance(value_, OrderedDict):
			#Y => Does this dict Object have childNodes?
			lastChildNodeIx = len(value_) - 1
			if lastChildNodeIx > -1:
				# Y => Signal this is a parrentNode
				return True
		
		# Is this a listObject?
		if isinstance(value_, list):
			#Y => Does this list Object have childNodes?
			lastChildNodeIx = len(value_) - 1
			if lastChildNodeIx > -1:
				# Y => Signal this is a parrentNode
				return True			

		# Assume this is a leafNode "simple object without childNodes", fx string or number
		return False 
		
	# Method used to print leafNodes
	def printLeafNode(self, node_ = ""):
		# Has node been specified?
		if node_ == "":
			#N => Assume thisNodes item should be checked
			node_ = self

		print(node_.getString())
		return

	# Method that retuns a node as a string
	def getString(self, value_ = ""):
		# Has a item been specified?
		if value_ != "":
			#Y => Assume specified item should be converted to a string
			#Is item a leafNode?
			if not self.isLeafNode(value_):
				#N => Return empty
				return ""

			# Assume this item is a leafNode
			#Is this leafNode a orderedDict Object?
			if isinstance(value_, OrderedDict):
				# Is this a orderedDict Object containg a simple leafNode "one key:value pair"
				if self.isLeafNode(value_):
					#Y => return leafNode
					for k, v in value_.items():
						# does it have key?
						if k != "":
							#Y
							return k + ": " + self.getString(v)
						else:
							return self.getString(v)
				else:
					return k + ": "

			#Is thisleafNode a list Object?
			if isinstance(value_, list):
				# Is this a orderedDict Object containg a simple leafNode "one key:value pair"
				if self.isLeafNode(value_):
					#Y => return leafNode
					for v in value_:
						return self.getString(v)
				else:
					return ""

			#Is this leafNode a string Object?
			if isinstance(value_, str):
				#Y
				return value_
			
			# Assume this leafNode is a number
			return str(value_)

		# "N" => Assume thisNode item should be converted to string
		#Is item a leafNode?
		if not self.isLeafNode():
			#N => Return empty
			return ""

		#Is this leafNode a orderedDict Object?
		if isinstance(self.value_, OrderedDict):
			# Is this a orderedDict Object containg a simple leafNode "one key:value pair"
			if self.isLeafNode():
				#Y => return leafNode
				for k, v in self.value_.items():
					# Does it have key?
					if k != "":
						#Y
						return k + ": " + self.getString(v)
					else:
						#N
						return self.getString(v)
			else:
				return k + ": "

		#Is thisleafNode a list Object?
		if isinstance(self.value_, list):
			# Is this a orderedDict Object containg a simple leafNode "one key:value pair"
			if self.isLeafNode():
				#Y => return leafNode
				for v in self.value_:
					return self.getString(v)
			else:
				return ""

		#Is this leafNode a string Object?
		if isinstance(self.value_, str):
			#Y
			# Does thisNode have key?
			if self.key_ != "":
				#Y
				return self.key_ + ": " + self.value_
			else:
				#N
				return self.value_
		
		# Assume this leafNode is a number
		# Does thisNode have key?
		if self.key_ != "":
			#Y
			return self.key_ + ": " + str(self.value_)
		else:
			#N
			return str(self.value_)

	# Method that retuns a node item as a string
	def getValueString(self, value_ = ""):
		# Has a item been specified?
		if value_ != "":
			#Y => Assume specified item should be converted to a string
			#Is item a leafNode?
			if not self.isLeafNode(value_):
				#N => Return empty
				return ""

			# Assume this item is a leafNode
			#Is this leafNode a orderedDict Object?
			if isinstance(value_, OrderedDict):
				# Is this a orderedDict Object containg a simple leafNode "one key:value pair"
				if self.isLeafNode(value_):
					#Y => return leafNode
					for v in value_.values():
						return self.getString(v)
				else:
					return ""

			#Is thisleafNode a list Object?
			if isinstance(value_, list):
				# Is this a orderedDict Object containg a simple leafNode "one key:value pair"
				if self.isLeafNode(value_):
					#Y => return leafNode
					for v in value_:
						return self.getString(v)
				else:
					return ""

			#Is this leafNode a string Object?
			if isinstance(value_, str):
				#Y
				return value_
			
			# Assume this leafNode is a number
			return str(value_)

		# "N" => Assume thisNode item should be converted to string
		#Is item a leafNode?
		if not self.isLeafNode():
			#N => Return empty
			return ""

		#Is this leafNode a orderedDict Object?
		if isinstance(self.value_, OrderedDict):
			# Is this a orderedDict Object containg a simple leafNode "one key:value pair"
			if self.isLeafNode():
				#Y => return leafNode
				for v in self.value_.values():
					return self.getString(v)
			else:
				return ""

		#Is thisleafNode a list Object?
		if isinstance(self.value_, list):
			# Is this a orderedDict Object containg a simple leafNode "one key:value pair"
			if self.isLeafNode():
				#Y => return leafNode
				for v in self.value_:
					return self.getString(v)
			else:
				return ""

		#Is this leafNode a string Object?
		if isinstance(self.value_, str):
			#Y
			return self.value_
		
		# Assume this leafNode is a number
		return str(self.value_)

	# Method used to signal Tree travesal restart, hence reset Tree Traversal Complete flag
	def restart(self):
		# Reset Tree Traversed flag
		self.treeTraversed_ = False
		return

# --------------- NODE SEARCH METHDOS -----------
	def getNodeById(self, nodeId_, startNode_ = ""):
		thisNode = self
		
		# find specfied Node
		while(thisNode != ""):
			thisNode = thisNode.getNextNode(startNode_)

			# Was valid nextNode found
			if thisNode == "":
				#N => Signal failed to find nextNode
				return ""			

			# Is this the node we are looking for?
			if thisNode.nodeId_ == nodeId_:
				#Y
				return thisNode

		# Assume the node was not found
		return ""

# ----------------------------------------------
    # -------- NODE TREE TRAVERSAL METHODS -------
	# Method used to traverse the json infoTree object or or sub-infoTree relative to startNode
	# STATUS: DONE->TESTED->WORKS!!
	def getNextNode(self, startNode_=""):
		# Has a startNode been specified?
		if startNode_ == "":
			#NO => Assume thisNode is startNode
			startNode_ = trackingNode(self.key_, self.value_, self.nodeIx_, self.childNodeIx_, self.prevNode_, self.nextNode_)
		
		# Set startNode
		thisNode = self

		# json Dict Object traversal using trackingNode
		# ----------- Look through using a trackingStack, Foward traversal ---------------
		# Loop until all nodes has been read
		while(thisNode != ""):
			# Has nodeTree been traversed?
			# Has all thisNodes subNodes been read?
			#Y => Has the sub-infoTree been traversed?
			if thisNode.childNodeIx_ >= thisNode.lastChildNodeIx_:
				#Y
				# Is this startNode level?
				if thisNode.nodeLevel_ == startNode_.nodeLevel_:
					# Has sub-infoTree been traversed?
					if (thisNode.childNodeIx_ > startNode_.childNodeIx_):
						#Y => Tree travesal complte
						# Signal tree has been traversed => return empty
						return ""

			# Loop until a valid nextNode has been found
			while(thisNode != ""):
				# Has nodeTree been traversed "Alle nodes has been read"?
				# Has nodeTree been traversed?
				# Has all thisNodes subNodes been read?
				#Y => Has the sub-infoTree been traversed?
				if thisNode.childNodeIx_ >= thisNode.lastChildNodeIx_:
					#Y
					# Is this startNode level?
					if thisNode.nodeLevel_ == startNode_.nodeLevel_:
						# Has sub-infoTree been traversed?
						if (thisNode.childNodeIx_ > startNode_.childNodeIx_):
							#Y => Tree travesal complte
							# Signal tree has been traversed
							return ""
				# Loop until non simple leafNode found
				#**while(1):
					# Is thisNode a simple leafNode?
					#**if thisNode.isSimpleLeafNode():
						#Y
						#Y => Just show the node and find nextNode
						#**thisNode.printLeafNode()
						# Backtrack to nextNode
						#**thisNode = thisNode.popNode()
					#**else:
						#N=> Assume non simple leafNode found
						#**break

				# Is thisNode a simple leafNode? "dict/list leafNode or string or number object"
				if thisNode.isSimpleLeafNode():
					#Y => Just show the node and find nextNode
					#**thisNode.printLeafNode()

					# Keep track of thisTrackingNode
					thisTrackingNode = thisNode

					# Backtrack to nextNode
					# Assume this list or dict object leafNode
					# Move/Point to next childNode
					# Restore childNode
					thisNode = thisNode.popNode()
					# Restore this parrentNode
					#**thisNode = thisNode.popNode()
					# Point/Move to this parrentNode
					#**thisNode = thisNode.value_
					#**return thisNode
					# Return this trackingNode, hence the detected leafNode
					# update leafNode link
					#**thisNode.leafNode_ = thisTrackingNode

					#**return thisNode
					break

				else:
					#N => Assume thisNode is a parrentNode "has subNodes"
					# Find nextNode
					# Has all thisNodes subNodes been read?
					#Y => Has the sub-infoTree been traversed?
					if thisNode.childNodeIx_ >= thisNode.lastChildNodeIx_:
						#Y
						# Is this startNode level?
						if thisNode.nodeLevel_ == startNode_.nodeLevel_:
							# Has sub-infoTree been traversed?
							if (thisNode.childNodeIx_ > startNode_.childNodeIx_):
								#Y => Tree travesal complte
								# Signal tree has been traversed, hence return empty
								return ""

						# Assume this i not rootNode
						# Backtrack nodeTree "find next valid parrentNode"
						# Restore prevNode
						thisNode = thisNode.popNode()
						# Point/Move to prevNode
						#**thisNode = self.value_
						# Forced exit loop => try nextNode
						break
					else:
						#N => find next valid subNode

						# What kind of object does thisNodes contain?
						# Is thisNode a orderedDict object?
						if thisNode.isOrderedDict():
							# Is this orderedDict a simple leafNode "orderedDict that contains a single simple key:value pair"
							#**if thisNode.isLeafNode(): 
								#Y =>								   
								# Forced exit, new LeafNode found							 
								#**break						 
							
							# Assume this childNode is not a leafNode																   
							#Y => find this orderedDict next childNode
							# Reset this childNode ix
							ix = 0
							for k, v in thisNode.value_.items():
								# Has next childNode been found?
								if ix > thisNode.childNodeIx_:
									#Y
									# Keep track of thisNode
									thisNode = thisNode.pushNode(thisNode.key_, thisNode.value_, thisNode.nodeIx_, ix, thisNode)
									# Keep track of this childNode
									thisNode = thisNode.pushNode(k, v, ix, -1, thisNode) # -1 = signal childNodes has not been processed yet									

									# Keep track of thisTrackingNode
									thisTrackingNode = thisNode

									# What kind of Object does this childNode contain?
									# Is this a leafNode?
									if thisNode.isSimpleLeafNode():
										#Y => Show the leafNode
										thisNode.printLeafNode()
										# Forced exit loop leafNode found
										#**break
										# Forced return new leafNode foun
										return thisNode
										
									# Assume this childNode does not contain a leafNode, hence it is a parrentNode
									# Show parrentNode
									print("New parrentNode containing orderedDict Object discovered: " + k)							   
									# Point/Move to next childNode
									#**thisNode = v
									
									
									# Forced exit next childNode found
									return thisTrackingNode #thisNode
									#**break

								# Update childNode ix
								ix = ix + 1 

						# Is thisNode a listObject?
						if thisNode.isList():
							# Is this orderedDict a simple leafNode "orderedDict that contains a single simple key:value pair"
							#**if thisNode.isLeafNode(): 
								#Y =>								   
								# Forced exit, new LeafNode found							 
								#**break
							   
							# Assume this childNode is not a leafNode																   
							#Y => find this listObject next childNode
							# Reset this childNode ix
							ix = 0
							for v in thisNode.value_:
								# Has next childNode been found?
								if ix > thisNode.childNodeIx_:
									#Y
									# Keep track of thisNode
									thisNode = thisNode.pushNode(thisNode.key_, thisNode.value_, thisNode.nodeIx_, ix, thisNode)
									# Keep track of this childNode
									thisNode = thisNode.pushNode(str(ix), v, ix, -1, thisNode) # -1 = signal childNodes has not been processed yet

									# Keep track of thisTrackingNode
									thisTrackingNode = thisNode

									# What kind of Object does this childNode contain?
									# Is this a leafNode?
									if thisNode.isLeafNode():
										#Y
										# Show leafNode
										thisNode.printLeafNode()
										# Point/Move to next childNode
										#**thisNode = v
										
										# Forced exit loop leafNode found
										#**break
										# Forced return new leafNode found
										return thisNode

									# Assume this childNode does not contain a leafNode, hence it is a parrentNode
									# Show parrentNode
									print("New parrentNode containg list Object discovered: Item " + str(ix))							 
									# Point/Move to next childNode
									#**thisNode = v

									# Forced exit next childNode found
									return thisTrackingNode #thisNode
									#**break
								
								# Update childNode ix
								ix = ix + 1

		# Assume nodeTree Traversal complete
		return ""								
		#-------------- END OF FORWARD TRAVESAL ---------

# ----------- peerNode traversal Methods ------------------
	# Method to get next peerNode, Search from thisNode to satrtNode
	def getNextPeerNode(self, startNode_ = ""):
		# Set thisNode
		thisNode = self

		# Is thisNode rootNode?
		if thisNode.prevNode_ == "":
			#Y => Signal cant get peerNode of RootNodes
			return ""

		# Set parrentNode
		thisParrentNode = thisNode.prevNode_

		# Has startNode been specifified?
		if startNode_ == "":
			#NO => Assume thisNode is startNode
			startNode_ = trackingNode(thisParrentNode.key_, thisParrentNode.value_, thisParrentNode.nodeIx_, thisParrentNode.childNodeIx_, thisParrentNode.prevNode_, thisParrentNode.nextNode_)

		# Loop until nextParrentNode found
		while(thisNode != ""):
			# Try nextNode
			thisNode = thisNode.getNextNode(startNode_)

			# Has nextNode been found?
			if thisNode == "":
				#N => Forced exit, no nextNode found
				return "" 

			# Is thisNode nextPeerNode, hence have same parrentNode as startNode_?
			if thisNode.prevNode_ == thisParrentNode:
				#Y => Retun the nextPeerNode
				return thisNode

		# Assume nextPeerNode was not found
		return ""

	# Method to get prev peerNode, Search from thisNode to satrtNode
	def getPrevPeerNode(self, startNode_ = ""):
		# Set thisNode
		thisNode = self

		# Is thisNode rootNode?
		if thisNode.prevNode_ == "":
			#Y => Signal cant get peerNode of RootNodes
			return ""
		
		# Set parrentNode
		thisParrentNode = thisNode.prevNode_

		# Has startNode been specifified?
		if startNode_ == "":
			#NO => Assume thisNode is startNode
			startNode_ = trackingNode(thisParrentNode.key_, thisParrentNode.value_, thisParrentNode.nodeIx_, thisParrentNode.childNodeIx_, thisParrentNode.prevNode_, thisParrentNode.nextNode_)

		# Loop until nextParrentNode found
		while(thisNode != ""):
			# Try nextNode
			thisNode = thisNode.getNextNode(startNode_)

			# Has nextNode been found?
			if thisNode == "":
				#N => Forced exit, no nextNode found
				return ""			

			# Is thisNode prevPeerNode, hence have same parrentNode as startNode_ but smaller nodeIx?
			if thisNode.prevNode_ == thisParrentNode and thisNode.nodeIx_ < startNode_.nodeIx_:
				#Y => Retun the prevPeerNode
				return thisNode

		# Assume prevPeerNode was not found
		return ""		
# --------------------- End of peerNode Traversal -----------------------

	# Method used to find trackingNodes parrentNode
	def getParrentNode(self, startNode_=""):		
		# Has a startNode been specified?
		if startNode_ == "":
			#NO => Assume rootNode is startNode
			startNode_ = self.getRootNode()
		
		# Set startNode to ThisNode
		thisNode = self

		# Create new trackingNode to avoid current becomes corrupt
		thisNode = trackingNode(thisNode.key_, thisNode.value_)		

		# Loop until parrentNode found
		while(thisNode != ""):
			#Try prev node
			thisNode = thisNode.getPrevNode(startNode_)

			# Was valid prevNode found
			if thisNode == "":
				#N => Signal failed to find parrentNode
				return ""

			# Has parrentNode been found?
			if thisNode.nodeLevel_ == self.nodeLevel_ - 1:
				#Y => Return parrentNode
				return thisNode

		# Assume prevNode was not found
		# Signal no node found
		return ""		

	# Method used to traverse the json infoTree object or or sub-infoTree relative to startNode
	# STATUS: DONE->TESTED->NOT WORKING AS EXPECTED!! (Alt. design implemented using forward traversal since it was too complex to perform backward traversal)
	def getPrevNode(self, startNode_=""):
		# Has a startNode been specified?
		if startNode_ == "":
			#NO => Assume rootNode is startNode
			startNode_ = self.getRootNode()
		
		# Set startNode
		thisNode = startNode_

		# Create new trackingNode to avoid current becomes corrupt
		thisNode = trackingNode(thisNode.key_, thisNode.value_)

		# Loop until prevNode found
		while(thisNode != ""):
			# Keep track of prevNode
			prevNode = thisNode

			#Try next node
			thisNode = thisNode.getNextNode(startNode_)

			# Was a valid node found?
			if thisNode == "":
				#N => Assume prevNode not found, Signal invalid node
				return ""

			# Has prevNode been found?
			# does keys match?
			if thisNode.key_ == self.key_:
				#Y => Does Values match?
				thisItem = self.getString()
				someItem = thisNode.getString()
				if thisItem == someItem:
					#Y => This must be the node we are looking for
					return prevNode

		# Assume prevNode was not found
		# Signal no node found
		return ""

		#-------------- END OF BACKWARD TRAVESAL ---------

    # ----------------- NODE SEARCH METHODS ---------
    # Method to find rootNode of the nodeChain
	def getRootNode(self):
		thisNode = self

		# Loop until rootNode found
		while(thisNode != ""):
			#Is thisNode the rootNode?
			if thisNode.prevNode_ == "":
				#Y => Return the root node
				return thisNode

			# Try prev node
			thisNode = thisNode.prevNode_

		# Assume rootNode not found
		return thisNode
				

	# Method to find leafNode of the nodeChain
	def getLeafNode(self):
		thisNode = self

		# Loop until leafNode found
		while(thisNode != ""):
			# Is thisNode the leafNode?
			if thisNode.nextNode_ == "":
				#Y => Return leafNode
				return thisNode
			
			# Try next Node
			thisNode = thisNode.nextNode_

		# Assume leafNode not found
		return thisNode

	# Method To used calc a nodes level "position i a tree structre"
	def getNodeLevel(self):
		thisNode = self
		prevNode = thisNode.prevNode_

		# Calc nodeLevel based on parrentNode
		# Is thisNode the rootNode?
		if self.prevNode_ == "":
			#Y => THis is root, hence nodeLevel 0
			self.nodeLevel_ = 0 # Specifies what level this node is at in a Tree structure
			return self.nodeLevel_
		else:
			# Is prevNode thisNodes parrentNode?
			# Is prevNode a OrderedDict Object?
			if prevNode.isOrderedDict():
				#Y => Is thisItem a childItem of prevNode?
				if self.value_ in prevNode.value_.values():
					#Y
					thisParrentNode = prevNode
				else:
					#N => Find correct parrentNode for thisNode
					# Find thisNodes parrent "Ensure jsonTree is in sync with json object structure"
					thisParrentNode = self.getParrentNode()					

			# Is prevNode a List Object?
			if prevNode.isList():
				#Y => Is thisItem a childItem of prevNode?
				if self.value_ in prevNode.value_:
					#Y
					thisParrentNode = prevNode
				else:
					#N => Find correct parrentNode for thisNode					
					# Find thisNodes parrent "Ensure jsonTree is in sync with json object structure"
					thisParrentNode = self.getParrentNode()

			# Update nodeLevel (Keeps track of what level in the infoTree thisNode is at)
			self.nodeLevel_ = thisParrentNode.nodeLevel_ + 1

		# return calc nodeLevel
		return self.nodeLevel_

	# Method used to find a item with the given Dict Key, handy when trying the getPrevNode method
	# OBS: This node is meant for traversal only to edit json Object use the jsonObject class
	def getNodeByKey(self, key_, startNode_ = ""):
		# Has a startNode been specified?
		if startNode_ == "":
			#N => Assume thisNode is startNode
			startNode_ = self

		# Set startNode
		thisNode = startNode_

        # Reset Tree Traversaed flag
		while(thisNode != ""):
			# Try next node
			thisNode = thisNode.getNextNode(startNode_)

			# Was valid prevNode found
			if thisNode == "":
				#N => Signal failed to find nextNode
				return ""			

			# Does this node contain the dict item we are looking for?
			if thisNode.key_ == key_:
				#Y
				return thisNode

		# Assume node was not found
		return ""
	
	# ----- NODE ITEM TYPE AUTO DISCOVER ---------
	def getName(self):
		# Auto discover name of thisNode
		#Does this thisNode have a prevNode "not rootNode"?
		if self.prevNode_ != "":
			#Y
			# Is this prevNode a dict object
			if self.prevNode_.isOrderedDict():
				#Y => Set name to key
				# Find key
				ix = 0
				for k in self.prevNode_.value_.keys():
					# Is this the item we are looking for?
					if ix == self.nodeIx_:
						#Y => Signal name is thisKey
						# Update key of thisNode
						self.key_ = k
						return k
					
					# Update item ix
					ix += 1
		else:
			#N 
			#Is thisNode a dict leafNode?
			if self.isLeafNode() and not self.isSimpleLeafNode():
				#Y => Get first key
				for k in self.value_.keys():
					self.key_ = k
					return k
		
		#"N" => No parrent assume this is a rootNode, hence unnamed
		return ""

	# Method to get last last childNode ix
	def getLastChildNodeIx(self, node_ = ""):
		# Has value been specified
		if node_ != "":
			if not self.isSimpleLeafNode(node_):
				#N => Assume it contains a dict or list object
				return len(node_) - 1
			else: #Y => assume this a leafNode
				return -1

		# Assume thisNode value should be checked
		# Is this trackingNode containing a simple leafNode
		if not self.isSimpleLeafNode():
			#N => assume it contains a dict or list object
			#**if self.isOrderedDict():
			# Calc last childNodeIx
			self.lastChildNodeIx_ = len(self.value_) - 1
			return self.lastChildNodeIx_		

		# If no conditions are met assume its a leafNode
		return -1

	#------- END ITEM TYPE AUTO DISCOVER -----		
	