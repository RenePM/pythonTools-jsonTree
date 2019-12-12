
# projectTags: orderedDictNode, DATA SCIENCE, MACHINE LEARNING, SIMI RECUSIVE

# Object that can manage json objects by nesting them in a orderedDictNode, Travese any tree structure using a stack for back tracking the traversal process
# Purpose: Purpose to manage json objects using a orderedDictNode consisting of the all the object types linked or nested in a jsonObject, hence simulating recursive process                # nodeChain to build a sort of node travesal history buffer
# requirement: MUST HAVE convertToDict function so that the orderedDictNode can be converted and stored in a dictonary and thereby be converted to json and used in noSQL Database and/or SIEM System
#              for faster data analysis.
# FUNKTIONALITY
# - ADD, REMOVE, INSERT, REPLACE, MODIFY
# - searchById, searchByName, searchByValue, searchByTag
# EXPORT
#   - exportToFile, createJson file based on this jsonObject structure "orderedDictNode structure"
#   - importFromFile create orderedDictNode consisting of json object stored in a file
# STAUS: (PENDING)

# Classes required to create a info tree consisting of any json object structure
# orderedDictNode, the standard jsonObject node containg orderedDictObject, , with subNodes of any type, OBS MOST BE orderedDict to preserve item order!!
# TODO: Implement anoter version that is dynamic hence subNodes_ becomes same object time as json object "item_" so that jsonNode is in sync with object contained in it, such as list, dict objects
# ---->TODO: Implement support for all jsonObject item types!! ENSURE ALL methods can handle its own item and some other item

import json
import xmltodict
from collections import OrderedDict
from trackingNodeChain import trackingStack, trackingNode
# import xmltodict

# JSON OBJECTS: OrderedDict, List "Array", String, Number
# Default jsonObject node is an orderedDict object
# STATUS: (WORKING)
class jsonNode(object):
	def __init__(self, name_ = "", item_ = "",	parrentNode_="", nodeLevelSeparator_="."):
		self.subNodes_ = [] # subNodes of this jsonNode is allways stored in array this ensures that all items can be located using node name, id or ix
		self.parrentNode_ = parrentNode_ # thisNodes parrentNode
		self.nodeLevelSeparator_ = nodeLevelSeparator_
		self.error_ = "" # Hold "thisError text, can be read to see what went wrong when a infoTree method returns nothing"
		self.uniqueLevel_ = 0 # Assume this node should not exist uniquely in the infoTree "let other Metods decide this question!!"
		self.tags_ = [] # tagChain that can help descripe thisNode
		self.freq_ = 1 # Def. freq. for root node, there can only be one :D
		self.type_ = 0 # Specifies the type of object thisNode contains
		# self.rootOffset_ # Specified nextNode count relative to rootNode, required to edit/access thisNodes item, hence data in json object
			# requires all affected nodes rootOffset_ is recalgulated when nodes are added, removed and moved!!
		# 0 = OrderedDict, 1 = List "Array", 2 = String, 3 = number
		
		self.item_ = item_ # the item (json object and its sub-infoTree) contained in thisNode fx. OrderedDict, list "array", string, number
		self.name_ = name_ # field name, Also known as key in dict, hence no dublicate keys allowed in childNodes
		# For non dict items "key:value pairs" this attribute is set to Empty
		self.lastSubNodeIx_ = -1 # thisNodes last subNodes ix, -1 = has no subNodes "subNodeCount - 1"

		# Auto Discover Object Type
		# Does thisNode contain a OrderedDict Object?
		if self.isOrderedDict(item_):
			#Y => Signal thisNode contains orderedDict object
			self.type_ = 0

		# Does thisNode contain a list obejct?
		if self.isList(item_):
			#Y => Signal thisNode contains list object
			self.type_ = 1

		# Does thisNode contain a string object
		if self.isString(item_):
			#Y => Signal thisNode contains a string object
			self.type_ = 2

		if self.isNumber(item_):
			#Y => Signal thisNode contains a number object?
			self.type_ = 3

		# Is this root node?
		if(self.parrentNode_ == ""):
			#Y=> This is Root so just set node ix 0
			self.nodeIx_ = 0
		else:
			#N=> Calc node ix used when auto generating nodeId's
			self.nodeIx_ = self.parrentNode_.lastSubNodeIx_ + 1

		# is this a root node?
		if(self.parrentNode_ != ""):
			#N=> Generate new key "NodeId" using the nodes location in the tree
			self.nodeId_ = self.parrentNode_.nodeId_ + self.nodeLevelSeparator_ + str(self.nodeIx_)
			# Update nodeLevel (Keeps track of what level in the infoTree thisNode is at)
			self.nodeLevel_ = self.getNodeLevel()

		# -----------------[UNREQUIRED Since Item is set earlier in the constructor, and the core methods performs this task]-------------
			# Auto discover item type and update thisNode item "jsonObject structure"
			# Is this parrentNode a dict object?
			#if self.parrentNode_.isOrderedDict():
				# Y=> add new dict item
				# Does this item allready exist?
				#if not self.name_ in self.parrentNode_.item_.keys():
					#N => Add the childItem
					#self.parrentNode_.item_[self.name_] = self.item_

			# Is this parrentNode a list object?
			#if self.parrentNode_.isList():
				#Y
				# Does this item allready exist?
				#if self.parrentNode_.getNodeByItem(self.name_, self.item_) == "":
					#N => Add childItem
					#self.parrentNode_.item_.append(self.item_)
		# -------------- END OF UNREQUIRED TASK --------------					

			# Is this parrentNode "CURRENTLY" a simple leafNode?
			if self.parrentNode_.isSimpleLeafNode():
				#Y => Signal attempt to add subNode to a leafNode
				self.error_ = "jsonNode: leafNodes do not have subNodes"

		else: #Y=> Assume this is root
			self.nodeId_ = "root"
			# Update nodeLevel
			self.nodeLevel_ = 0

		# Has name "used as key when the node is related to a dict item" been specified?
		if(self.name_ == ""):
			# No node name so just assign def.
			self.name_ = "Node " + self.nodeId_			

	# ------ OBJECT IMPORT/EXPOT FEATURES ------
	# Method used to import json object structure from a json file in to thisNode
	def importFromFile(self, fileName_):
		# Does this file exists?
		try:
			#Y
			# Open the json file for read
			with open(fileName_) as file:
				# Extract the json object structure
				jsonDict = json.load(file, object_pairs_hook=OrderedDict)
		except: # If open file fails
			#N => Signal failed to import file
			self.error_ = "importFromFile: Failed to import from " + fileName_
			return ""

		# Assume json object structure was imported from file
		# Create jsonObject containing the json object structure

		# Point to thisNode
		thisNode = self

		# Update thisNodes item "json object structure" and sub-infoTree, hence point to new json dict and update sub-infoTree
		thisNode.setValue(jsonDict)

		# Signal File import successful
		return thisNode

	# Method used to import json object structure stored in dict object structure and reconstruct thisNodes sub-infoTree to reflect this json Object
	def importFromOrderedDict(self, item_):
		# Point to thisNode
		thisNode = self

		# Update thisNodes item "json object structure" and sub-infoTree, hence point to new json dict and update sub-infoTree
		thisNode = thisNode.setValue(item_)

		# return result
		return thisNode
		
	# Method used to export thisNode and its sub-infoTree to json file
	def exportToFile(self, fileName_):
		# Does this file exists?
		try:
			#Y
			# Open the json file for read
			with open(fileName_, "x") as file:
				# Export the json object structure to file and specify tabs = 4 spaces
				# Convert jsonObject to a json string
				jsonString = json.dumps(self.item_, indent=4)
				# Write json string to file
				file.write(jsonString)

		except: # If open file fails
			#N => Signal failed to import file
			self.error_ = "exportToFile: Failed to export node with id " + self.nodeId_ + " and its sub-infoTree to file " + fileName_
			return ""

		# Assume json object structure was exported to file

		# Signal File export successful
		return self

	# ------ END IMPORT/EXPORT FEATURES ------			   

	# ------ OBJECT AUTO DISCOVERY FEATURES -----------
	# method that returns wether a given node is a leafNode, hence contains a simple object fx, str, int, dbl or dict/list with one item etc
	def isLeafNode(self, item_ = ""):
		# Has a item been specified?
		if item_ != "":
			#Y => Assume specified item should be classified
			# Is this a dictObject?
			if isinstance(item_, OrderedDict):
				#YES
				# Is this a orderedDict Object containg a leafNode "one simple key:value pair"
				# Calc last subNode ix
				lastSubNodeIx = len(item_) - 1
				if lastSubNodeIx == 0:
					# Is this childNode a simple leafNode?
					for k, v in item_.items():
						if self.isSimpleLeafNode(v):
							#Y
							return True
					
					# Assume this dictObject does not contain a simple leafNode
					return False

				# Assume this what not a orderedDict Object containg a simple leafNode
				return False
			
			# Is this a listObject?
			if isinstance(item_, list):
				#YES
				# Is this a listObject containg a leafNode "one simple value"
				# Calc last subNode Ix
				lastSubNodeIx = len(item_) - 1
				if lastSubNodeIx == 0:
					#Y 
					# Is this childNode a simple leafNode
					for v in item_:
						if self.isSimpleLeafNode(v):
							#Y
							return True
				
				# Assume this was not a listObject containing a simple leafNode
				return False

			# Assume this is a leafNode "simple object without childNodes", fx string or number
			return True

		#N => Assume thisNode item should be classified
		# Is this a dictObject?
		if isinstance(self.item_, OrderedDict):
			#YES
			# Is this a orderedDict Object containg a leafNode "one simple key:value pair"
			if self.lastSubNodeIx_ == 0:
				# Is this childNode a simple leafNode?
				for k, v in self.item_.items():
					if self.isSimpleLeafNode(v):
						#Y
						return True
				
				# Assume this dictObject does not contain a simple leafNode
				return False

			# Assume this what not a orderedDict Object containg a simple leafNode
			return False
		
		# Is this a listObject?
		if isinstance(item_, list):
			#YES
			# Is this a listObject containg a leafNode "one simple value"
			if self.lastSubNodeIx_ == 0:
				#Y 
				# Is this childNode a simple leafNode
				for v in item_:
					if self.isSimpleLeafNode(v):
						#Y
						return True
			
			# Assume this was not a listObject containing a simple leafNode
			return False

		# Assume this is a leafNode "simple object without childNodes", fx string or number
		return True

	# method that returns wether a given node is a simple leafNode, hence contains a simple object fx, str, int, dbl etc
	def isSimpleLeafNode(self, item_ = ""):
		# Has a item been specified?
		if item_ != "":
			#Y
			# Is this a dictObject?
			if isinstance(item_, OrderedDict):
				#YES
				return False
			
			# Is this a listObject?
			if isinstance(item_, list):
				#YES
				return False

			# Assume this is a leafNode "simple object without childNodes", fx string or number
			return True

		# "N" => Assume thisNode item should be classified
		# Is this a dictObject?
		if isinstance(self.item_, OrderedDict):
			#YES
			return False
		
		# Is this a listObject?
		if isinstance(self.item_, list):
			#YES
			return False

		# Assume this is a leafNode "simple object without childNodes", fx string or number
		return True		
		
	# Methods that auto detects and classifies the object type/class
	def isDict(self, item_ = ""):
		# Has a item_ been specified?
		if item_ != "":
			#Y => Assume specified item should be classified
			#Does node contain a dict object?
			if isinstance(item_, dict):
				#Y
				return True
			else: #N
				return False

		# Assume thisNode should be classified
		#Does thisNode contain a dict object?
		if isinstance(self.item_, dict):
			#Y
			return True
		
		# Assume thisNode does not contain a dict object
		return False

	def isOrderedDict(self, item_ = ""):
		# Has a item been specified?
		if item_ != "":
			#N => Assume specified item should be classified
			#Does node contain a dict object?
			if isinstance(item_, OrderedDict):
				#Y
				return True
			else: #N
				return False

		# Assume thisNode should be classified
		#Does thisNode contain a dict object?
		if isinstance(self.item_, OrderedDict):
			#Y
			return True
		
		# Assume thisNode does not contain a dict object
		return False

	def isList(self, item_ = ""):
		# Has a node been specified?
		if item_ != "":
			#N => Assume specified item should be classified
			#Does node contain a dict object?
			if isinstance(item_, list):
				#Y
				return True
			else: #N
				return False

		# Assume thisNode should be classified
		#Does thisNode contain a dict object?
		if isinstance(self.item_, list):
			#Y
			return True
		
		# Assume thisNode does not contain a dict object
		return False

	def isString(self, item_ = ""):
		# Has a node been specified?
		if item_ != "":
			#N => Assume specified item should be classified
			#Does node contain a dict object?
			if isinstance(item_, str):
				#Y
				return True
			else: #N
				return False

		# Assume thisNode should be specified
		#Does thisNode contain a dict object?
		if isinstance(self.item_, str):
			#Y
			return True
		
		# Assume thisNode does not contain a dict object
		return False

	def isNumber(self, item_ = ""):
		# Has a item been specified?
		if item_ != "":
			#N => Assume specified item should be classified
			# Does specified node contain a leafNode?
			if self.isSimpleLeafNode(item_):
				#Y
				#Does node contain a string object?
				if isinstance(item_, str):
					#Y
					return False
				else: #N => Assume node contains a number
					return True

		# Assume thisNode should be specified
		#Does thisNode contain a leafNode?
		if self.isSimpleLeafNode():
			#Y
			#Does thisNode contain a string object?
			if isinstance(self.item_, str):
				#Y
				return False
			else:
				#N => Assume thisNode contains a number
				return True
		
		# Assume thisNode does not contain a Number object
		return False

	def isJsonNode(self, item_ = ""):
		# Has a node been specified?
		if item_ != "":
			#N => Assume specified item should be classified
			#Does node contain a dict object?
			if isinstance(item_, jsonNode):
				#Y
				return True
			else: #N
				return False

		# Assume thisNode should be classified
		#Does thisNode contain a dict object?
		if isinstance(self.item_, jsonNode):
			#Y
			return True
		
		# Assume thisNode does not contain a jsonNode object
		return False		

	#------- END AUTO DISOVERY FEATURES ---------------

	#------- NODE PRINT FEATURES -------------------
	# Method used to print a item contained in a node
	def print(self, item_ = ""):
		# Has an item been specified?
		if item_ != "":
			#Y => Assume specifed item should be printed
			print(self.getString(item_))
			return

		# Assume thisNode item should e printed
		print(self.getString())
		return

	# Method that retuns a node as a string
	def getString(self, item_ = ""):
		# Has a item been specified?
		if item_ != "":
			#Y => Assume specified item should be converted to a string
			#Is item a leafNode?
			if not self.isLeafNode(item_):
				#N => Return empty
				return ""

			# Assume this item is a leafNode
			#Is this leafNode a orderedDict Object?
			if isinstance(item_, OrderedDict):
				# Is this a orderedDict Object containg a simple leafNode "one key:value pair"
				if self.isLeafNode(item_):
					#Y => return leafNode
					for k, v in item_.items():
						# does it have key?
						if k != "":
							#Y
							return k + ": " + self.getString(v)
						else:
							return self.getString(v)
				else:
					return k + ": "

			#Is thisleafNode a list Object?
			if isinstance(item_, list):
				# Is this a orderedDict Object containg a simple leafNode "one key:value pair"
				if self.isLeafNode(item_):
					#Y => return leafNode
					for v in item_:
						return self.getString(v)
				else:
					return ""

			#Is this leafNode a string Object?
			if isinstance(item_, str):
				#Y
				return item_
			
			# Assume this leafNode is a number
			return str(item_)

		# "N" => Assume thisNode item should be converted to string
		#Is item a leafNode?
		if not self.isLeafNode():
			#N => Return empty
			return ""

		#Is this leafNode a orderedDict Object?
		if isinstance(self.item_, OrderedDict):
			# Is this a orderedDict Object containg a simple leafNode "one key:value pair"
			if self.isLeafNode():
				#Y => return leafNode
				for k, v in self.item_.items():
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
		if isinstance(self.item_, list):
			# Is this a orderedDict Object containg a simple leafNode "one key:value pair"
			if self.isLeafNode():
				#Y => return leafNode
				for v in self.item_:
					return self.getString(v)
			else:
				return ""

		#Is this leafNode a string Object?
		if isinstance(self.item_, str):
			#Y
			# Does thisNode have key?
			if self.name_ != "":
				#Y
				return self.name_ + ": " + self.item_
			else:
				#N
				return self.item_
		
		# Assume this leafNode is a number
		# Does thisNode have key?
		if self.name_ != "":
			#Y
			return self.name_ + ": " + str(self.item_)
		else:
			#N
			return str(self.item_)

	# Method that retuns a node item as a string
	def getValueString(self, item_ = ""):
		# Has a item been specified?
		if item_ != "":
			#Y => Assume specified item should be converted to a string
			#Is item a leafNode?
			if not self.isLeafNode(item_):
				#N => Return empty
				return ""

			# Assume this item is a leafNode
			#Is this leafNode a orderedDict Object?
			if isinstance(item_, OrderedDict):
				# Is this a orderedDict Object containg a simple leafNode "one key:value pair"
				if self.isLeafNode(item_):
					#Y => return leafNode
					for v in item_.values():
						return self.getString(v)
				else:
					return ""

			#Is thisleafNode a list Object?
			if isinstance(item_, list):
				# Is this a orderedDict Object containg a simple leafNode "one key:value pair"
				if self.isLeafNode(item_):
					#Y => return leafNode
					for v in item_:
						return self.getString(v)
				else:
					return ""

			#Is this leafNode a string Object?
			if isinstance(item_, str):
				#Y
				return item_
			
			# Assume this leafNode is a number
			return str(item_)

		# "N" => Assume thisNode item should be converted to string
		#Is item a leafNode?
		if not self.isLeafNode():
			#N => Return empty
			return ""

		#Is this leafNode a orderedDict Object?
		if isinstance(self.item_, OrderedDict):
			# Is this a orderedDict Object containg a simple leafNode "one key:value pair"
			if self.isLeafNode():
				#Y => return leafNode
				for v in self.item_.values():
					return self.getString(v)
			else:
				return ""

		#Is thisleafNode a list Object?
		if isinstance(self.item_, list):
			# Is this a orderedDict Object containg a simple leafNode "one key:value pair"
			if self.isLeafNode():
				#Y => return leafNode
				for v in self.item_:
					return self.getString(v)
			else:
				return ""

		#Is this leafNode a string Object?
		if isinstance(self.item_, str):
			#Y
			return self.item_
		
		# Assume this leafNode is a number
		return str(self.item_)

	# Gets the level of thisNode based on its nodeId
	def getNodeLevel(self):
		thisNode = self
		
		ix=0
		nodeLevel=0
		while(ix != -1):
			ix = thisNode.nodeId_.find(thisNode.nodeLevelSeparator_, ix)
			# was a nodeLevel seperator found?
			if(ix > -1):
				nodeLevel += 1
				# Prepare search for next nodeLevel separator
				ix = ix + 1 
		
		# Return the nodeLevel
		return nodeLevel

	# Gets last/thisError that occured while handling thisNode
	def getError(self):
		return self.error_

#-------------------- All Nodes Handling (Search from thisNode to end of its sub-infoTree) --------------
#------------------ ADD Node Handling (Search from thisNode to end of its sub-nodeTree) --------------
	# Add new nodeObj on same parrentNode/nodeChain as thisNode as new last-subNode
	def addNodeObj(self, newNode_, uniqueLevel_=-1):
		thisNode = self
		thisParrentNode = thisNode.parrentNode_
			 
		# Auto discover item type and update thisNode uniquenessLevel
		# Is this parrentNode a dict object?
		if thisParrentNode.isOrderedDict():
			#Y => Set uniqunessLevel to peerNode uniqueness since a dict cannot contain duplicate keys
			uniqueLevel_ = 2

		# Has uniqueness level been specified?
		if uniqueLevel_ < 0:
			#N => Use/Enherit thisNodes
			uniqueLevel_ = thisNode.uniqueLevel_

		# Is this rootNode?
		if(thisParrentNode == ""):
			# YES => rootNode does not have peerNodes
			self.error_ = "addPeerNodeObj: rootNode does have peerNodes!!"
			return ""

		# Is node->value unique?
		# Is it infoTree Uniqueness?
		if(uniqueLevel_ == 1):
			# Does this node allready exist?
			thisRootNode = thisNode.getRootNode()
			existingNode = thisRootNode.findNodeByItem(newNode_.name_, newNode_.item_)
			if(existingNode != ""):
				# Node exist just update frequency "match count"
				existingNode.freq_ += 1				   
				return self
		# Is it peerNode Uniqueness?
		if(uniqueLevel_ == 2):
			# Does this node allready exist as a peerNode?
			existingNode = thisNode.findPeerNodeByItem(newNode_.name_, newNode_.item_)
			if(existingNode != ""):
				# Node exist just update frequency "match count"
				existingNode.freq_ += 1
				return self
		# Is it subNode Uniqueness?
		if(uniqueLevel_ == 3):
			# Does this node allready exist as a subNode?
			existingNode = thisNode.findSubNodeByItem(newNode_.name_, newNode_.item_)
			if(existingNode != ""):
				# Node exist just update freq "match count"
				existingNode.freq_ += 1
				return self
		# Is it sub-infoTree Uniqueness
		if(uniqueLevel_ == 4):
			# Does this node allready exist as a subNode?
			existingNode = thisNode.findNodeByItem(newNode_.name_, newNode_.item_)
			if(existingNode != ""):
				# Node exist just update freq "match count"
				existingNode.freq_ += 1
				return self

		# Assume the node does not exist
		# update this parrentNodes subNode structure "sub-infoTree"
		# Does this subNode allready Exist?
		for node in thisParrentNode.subNodes_:
			# Is newNode == to someNode?
			if newNode_.name_ == node.name_:
				#Y => Signal tryed to add existing node
				thisNode.error_ = "addPeerNodeObj: node " + newNode_.name_ + " allready exist in sub-nodeTree of parrentNode " + thisParrentNode.name_
				# Forced exit node allready exists
				return thisNode

		# Ensure the newPeerNode has been associated/linked to thisNodes parrentNode
		newNode_.parrentNode_ = thisNode.parrentNode_
		# Ensure the newPeerNode has the specified uniqueness level
		newNode_.uniqueLevel_ = uniqueLevel_

		# Add the new peerNode
		thisParrentNode.subNodes_.append(newNode_)
		
		# Update sub node count
		thisParrentNode.lastSubNodeIx_ += 1
		# Ensure nodeIx has lastNode ix so it can be fixed 
		newNode_.nodeIx_ = thisParrentNode.lastSubNodeIx_

		# Fix newPeerNode & its sub-infoTree nodeId's
		newNode_.updateSubinfoTreeNodeIds()

		# Auto discover item type and update this parrentNodes json object structure "sub-infoTree"
		# Is this parrentNode a dict object?
		if thisParrentNode.isOrderedDict():
			#Y => Has this key allready been added?
			if not newNode_.name_ in thisParrentNode.item_.keys():
				#N => Add the new dict item, insert not supported for dicts so we must recreate the sub-infoTree of all nodes after the ref node
				thisParrentNode.item_[newNode_.name_] = newNode_.item_				
				
		# Is this parrentNode a list Object?
		if thisParrentNode.isList():
			#Y
			# Has this item allready been added?
			if thisParrentNode.getNodeByItem(newNode_.name_, newNode_.item_) == "":
				#N => Add new list item, hence nodeix + 1 => after node at ix
				thisParrentNode.item_.append(newNode_.item_)

		# Update new nodes sub-infoTree to reflect its json object structure
		#newNode_.setValue()	

		return newNode_

	# Add new nodeObj (by value) relative to Node Specified by Id as new last-subNode, Search from thisNode and to end of its sub-infoTree unless startNode has been specified
	# use rootNode if you are unsure where the node is located
	def addNodeObjById(self, nodeId_, newNode_, uniqueLevel_=-1, startNode_ = ""):
		thisNode = self
		startNode = startNode_

		# Has node search been restricted to a specific endNode?
		if startNode_ == "":
			#N => Assume thisNode sub-infoTree 
			startNode = thisNode

		# Find the reference node
		thisParrentNode=""
		while(thisNode != ""):
			# Is this the node we are looking for?
			if(thisNode.nodeId_.lower() == nodeId_.lower()):
				thisParrentNode = thisNode.parrentNode_
				break

			# Get next node
			thisNode = thisNode.getNextNode(startNode)

		# Was the ref. node found?
		if(thisParrentNode == ""):
			# NO
			self.error_ = "addPeerNodeObjById: Unable to find node with Id" + nodeId_			 
			return ""

		# Auto discover item type and update thisNode uniquenessLevel
		# Is this parrentNode a dict object?
		if thisParrentNode.isOrderedDict():
			#Y => Set uniqunessLevel to peerNode uniqueness since a dict cannot contain duplicate keys
			uniqueLevel_ = 2			

		#Has uniquenessLevel been specified?
		if uniqueLevel_ < 0:
			#N => Use/Enherit from thisNode
			uniqueLevel_ = thisNode.uniqueLevel_
		
		# Is node->value unique?
		# Is it infoTree Uniqueness?
		if(uniqueLevel_ == 1):
			# Does this node allready exist?
			thisRootNode = thisNode.getRootNode()
			existingNode = thisRootNode.findNodeByItem(newNode_.name_, newNode_.item_)
			if(existingNode != ""):
				# Node exist just update frequency "match count"
				existingNode.freq_ += 1				   
				return self
		# Is it peerNode Uniqueness?
		if(uniqueLevel_ == 2):
			# Does this node allready exist as a peerNode?
			existingNode = thisNode.findPeerNodeByItem(newNode_.name_, newNode_.item_)
			if(existingNode != ""):
				# Node exist just update frequency "match count"
				existingNode.freq_ += 1
				return self
		# Is it subNode Uniqueness?
		if(uniqueLevel_ == 3):
			# Does this node allready exist as a subNode?
			existingNode = thisNode.findSubNodeByItem(newNode_.name_, newNode_.item_)
			if(existingNode != ""):
				# Node exist just update freq "match count"
				existingNode.freq_ += 1
				return self
		# Is it sub-infoTree Uniqueness
		if(uniqueLevel_ == 4):
			# Does this node allready exist as a subNode?
			existingNode = thisNode.findNodeByItem(newNode_.name_, newNode_.item_)
			if(existingNode != ""):
				# Node exist just update freq "match count"
				existingNode.freq_ += 1
				return self
		
		# Assume the ref. node was found
		# update this parrentNodes subNode structure "sub-infoTree"
		# Does this subNode allready Exist?
		for node in thisParrentNode.subNodes_:
			# Is newNode == to someNode?
			if newNode_.name_ == node.name_:
				#Y => Signal tryed to add existing node
				thisNode.error_ = "addPeerNodeObjById: node " + newNode_.name_ + " allready exist in sub-nodeTree of parrentNode " + thisParrentNode.name_
				# Forced exit node allready exists
				return thisNode

		# Assume the node does not exist
		# Ensure the newPeerNode has been associated/linked to thisNodes parrentNode
		newNode_.parrentNode_ = thisNode.parrentNode_ 
		# Ensure the newPeerNode has the specified uniqueness level
		newNode_.uniqueLevel_ = uniqueLevel_		

		# Add the new peerNode
		thisParrentNode.subNodes_.append(newNode_)

		# Update sub node count
		thisParrentNode.lastSubNodeIx_ += 1
		# Ensure nodeIx is has lastNode ix so it can be fixed 
		newNode_.nodeIx_ = thisParrentNode.lastSubNodeIx_		  

		# Fix newPeerNode & its sub-infoTree nodeId's
		newNode_.updateSubinfoTreeNodeIds()

		# Auto discover item type and update this parrentNodes json object structure "sub-infoTree"
		# Is this parrentNode a dict object?
		if thisParrentNode.isOrderedDict():
			#Y => Has this key allready been added?
			if not newNode_.name_ in thisParrentNode.item_.keys():
				#N => Add the new dict item, insert not supported for dicts so we must recreate the sub-infoTree of all nodes after the ref node
				thisParrentNode.item_[newNode_.name_] = newNode_.item_				
				
		# Is this parrentNode a list Object?
		if thisParrentNode.isList():
			#Y
			# Has this item allready been added?
			if thisParrentNode.getNodeByItem(newNode_.name_, newNode_.item_) == "":			
				#N => Add new list item, hence nodeix + 1 => after node at ix
				thisParrentNode.item_.append(newNode_.item_)

		# Update new nodes sub-infoTree to reflect its json object structure
		#newNode_.setValue()		
		
		return newNode_

	# Add new nodeObj (by value) relative to Node Specified by Name as new last-subNode, Search from thisNode and to end of its sub-infoTree unless startNode has been specified
	# use rootNode if you are unsure where the node is located
	def addNodeObjByName(self, name_, newNode_, uniqueLevel_=-1, startNode_ = ""):
		thisNode = self
		startNode = startNode_

		# Has node search been restricted to a specific endNode?
		if startNode_ == "":
			#N => Assume thisNode sub-infoTree 
			startNode = thisNode

		# Find the reference node
		thisParrentNode=""
		while(thisNode != ""):
			# Is this the node we are looking for?
			if(thisNode.name_.lower() == name_.lower()):
				thisParrentNode = thisNode.parrentNode_
				break

			# Get next node
			thisNode = thisNode.getNextNode(startNode)

		# Was the ref. node found?
		if(thisParrentNode == ""):
			# NO
			self.error_ = "addPeerNodeObjByName: Unable to find node with Name" + name_			 
			return ""

		# Auto discover item type and update thisNode uniquenessLevel
		# Is this parrentNode a dict object?
		if thisParrentNode.isOrderedDict():
			#Y => Set uniqunessLevel to peerNode uniqueness since a dict cannot contain duplicate keys
			uniqueLevel_ = 2			

		#Has uniquenessLevel been specified?
		if uniqueLevel_ < 0:
			#N => Use/Enherit from thisNode
			uniqueLevel_ = thisNode.uniqueLevel_
		
		# Is node->value unique?
		# Is it infoTree Uniqueness?
		if(uniqueLevel_ == 1):
			# Does this node allready exist?
			thisRootNode = thisNode.getRootNode()
			existingNode = thisRootNode.findNodeByItem(newNode_.name_, newNode_.item_)
			if(existingNode != ""):
				# Node exist just update frequency "match count"
				existingNode.freq_ += 1				   
				return self
		# Is it peerNode Uniqueness?
		if(uniqueLevel_ == 2):
			# Does this node allready exist as a peerNode?
			existingNode = thisNode.findPeerNodeByItem(newNode_.name_, newNode_.item_)
			if(existingNode != ""):
				# Node exist just update frequency "match count"
				existingNode.freq_ += 1
				return self
		# Is it subNode Uniqueness?
		if(uniqueLevel_ == 3):
			# Does this node allready exist as a subNode?
			existingNode = thisNode.findSubNodeByItem(newNode_.name_, newNode_.item_)
			if(existingNode != ""):
				# Node exist just update freq "match count"
				existingNode.freq_ += 1
				return self
		# Is it sub-infoTree Uniqueness
		if(uniqueLevel_ == 4):
			# Does this node allready exist as a subNode?
			existingNode = thisNode.findNodeByItem(newNode_.name_, newNode_.item_)
			if(existingNode != ""):
				# Node exist just update freq "match count"
				existingNode.freq_ += 1
				return self
		
		# Assume the ref. node was found
		# update this parrentNodes subNode structure "sub-infoTree"
		# Does this subNode allready Exist?
		for node in thisParrentNode.subNodes_:
			# Is newNode == to someNode?
			if newNode_.name_ == node.name_:
				#Y => Signal tryed to add existing node
				thisNode.error_ = "addPeerNodeObjByName: node " + newNode_.name_ + " allready exist in sub-nodeTree of parrentNode " + thisParrentNode.name_
				# Forced exit node allready exists
				return thisNode

		# Assume the node does not exist
		# Ensure the newPeerNode has been associated/linked to thisNodes parrentNode
		newNode_.parrentNode_ = thisNode.parrentNode_ 
		# Ensure the newPeerNode has the specified uniqueness level
		newNode_.uniqueLevel_ = uniqueLevel_		

		# Add the new peerNode
		thisParrentNode.subNodes_.append(newNode_)

		# Update sub node count
		thisParrentNode.lastSubNodeIx_ += 1
		# Ensure nodeIx is has lastNode ix so it can be fixed 
		newNode_.nodeIx_ = thisParrentNode.lastSubNodeIx_		  

		# Fix newPeerNode & its sub-infoTree nodeId's
		newNode_.updateSubinfoTreeNodeIds()

		# Auto discover item type and update this parrentNodes json object structure "sub-infoTree"
		# Is this parrentNode a dict object?
		if thisParrentNode.isOrderedDict():
			#Y => Has this key allready been added?
			if not newNode_.name_ in thisParrentNode.item_.keys():
				#N => Add the new dict item, insert not supported for dicts so we must recreate the sub-infoTree of all nodes after the ref node
				thisParrentNode.item_[newNode_.name_] = newNode_.item_				
				
		# Is this parrentNode a list Object?
		if thisParrentNode.isList():
			#Y
			# Has this item allready been added?
			if thisParrentNode.getNodeByItem(newNode_.name_, newNode_.item_) == "":			
				#N => Add new list item, hence nodeix + 1 => after node at ix
				thisParrentNode.item_.append(newNode_.item_)

		# Update new nodes sub-infoTree to reflect its json object structure
		#newNode_.setValue()		
		
		return newNode_

	# Add new nodeObj (by value) relative to Node Specified by Value as new last-subNode, Search from thisNode and to end of its sub-infoTree
	# use rootNode if you are unsure where the node is located
	# uniquenessLevel refferes to name
	def addNodeObjByValue(self, value_, newNode_, uniqueLevel_=-1):
		thisNode = self
		startNode = thisNode

		# Find the reference node
		thisParrentNode=""
		while(thisNode != ""):
			# Is this the node we are looking for?
			# Is thisNode and value a ordered dict object
			if thisNode.isOrderedDict() and thisNode.isOrderedDict(value_):
				#Y => Is this the value we are looking for
				if thisNode.item_ == value_:
					#Y
					thisParrentNode = thisNode.parrentNode_
					break

			# Is thisNode and value a list object
			if thisNode.isList() and thisNode.isList(value_):
				#Y => Is this the value we are looking for
				if thisNode.item_ == value_:
					#Y
					thisParrentNode = thisNode.parrentNode_
					break					

			# Is thisNode and value a string
			if thisNode.isString() and thisNode.isString(value_):
				#Y => Is this the value we are looking for
				if(thisNode.item_.lower() == value_.lower()):
					#Y
					thisParrentNode = thisNode.parrentNode_
					break

			# Is thisNode and value a number
			if thisNode.isNumber() and thisNode.isNumber(value_):
				#Y => Is this the value we are looking for
				if thisNode.item_ == value_:
					#Y
					thisParrentNode = thisNode.parrentNode_
					break

			# Get next node
			thisNode = thisNode.getNextNode(startNode)

		# Was the ref. node found?
		if(thisParrentNode == ""):
			# NO
			self.error_ = "addPeerNodeObjByName: Unable to find node with name " + name_			
			return ""

		# Auto discover item type and update thisNode uniquenessLevel
		# Is this parrentNode a dict object?
		if thisParrentNode.isOrderedDict():
			#Y => Set uniqunessLevel to peerNode uniqueness since a dict cannot contain duplicate keys
			uniqueLevel_ = 2			

		# Has a uniquenessLevel been specified?
		if uniqueLevel_ < 0:
			#N => Use/Enheri thisNodes
			uniqueLevel_ = thisNode.uniqueLevel_
		
		# Is node->value unique?
		# Is it infoTree Uniqueness?
		if(uniqueLevel_ == 1):
			# Does this node allready exist?
			thisRootNode = thisNode.getRootNode()			 
			existingNode = thisRootNode.findNodeByName(newNode_.name_)
			if(existingNode != ""):
				# Node exit just update frequency "match count"
				existingNode.freq_ += 1
				return self
		# Is it peerNode Uniqueness?
		if(uniqueLevel_ == 2):
			# Does this node allready exist as a peerNode?
			existingNode = thisNode.findPeerNodeByName(newNode_.name_)
			if(existingNode != ""):
				# Node exist just update frequency "match count"
				existingNode.freq_ += 1
				return self
		# Is it subNode Uniqueness?
		if(uniqueLevel_ == 3):
			# Does this node allready exist as a subNode?
			existingNode = thisNode.findSubNodeByName(newNode_.name_)
			if(existingNode != ""):
				# Node exist just update freq "match count"
				existingNode.freq_ += 1
				return self
		# Is it sub-infoTree Uniqueness
		if(uniqueLevel_ == 4):
			# Does this node allready exist as a subNode?
			existingNode = thisNode.findNodeByName(newNode_.name_)
			if(existingNode != ""):
				# Node exist just update freq "match count"
				existingNode.freq_ += 1
				return self
		
		# Assume the ref. node was found
		# update this parrentNodes subNode structure "sub-infoTree"
		# Does this subNode allready Exist?
		for node in thisParrentNode.subNodes_:
			# Is newNode == to someNode?
			if newNode_.name_ == node.name_:
				#Y => Signal tryed to add existing node
				thisNode.error_ = "addPeerNodeObjName: node " + newNode_.name_ + " allready exist in sub-nodeTree of parrentNode " + thisParrentNode.name_
				# Forced exit node allready exists
				return thisNode

		# Assume the node does not exist
		# Ensure the newPeerNode has been associated/linked to thisNodes parrentNode
		newNode_.parrentNode_ = thisNode.parrentNode_ 
		# Ensure the newPeerNode has the specified uniqueness level
		newNode_.uniqueLevel_ = uniqueLevel_

		# Add the new peerNode
		thisParrentNode.subNodes_.append(newNode_)

		# Update sub node count
		thisNode.parrentNode_.lastSubNodeIx_ += 1
		# Ensure nodeIx is has lastNode ix so it can be fixed 
		newNode_.nodeIx_ = thisNode.parrentNode_.lastSubNodeIx_	  

		# Fix newPeerNode & its sub-infoTree nodeId's
		newNode_.updateSubinfoTreeNodeIds()

		# Auto discover item type and update this parrentNodes json object structure "sub-infoTree"
		# Is this parrentNode a dict object?
		if thisParrentNode.isOrderedDict():
			#Y => Has this key allready been added?
			if not newNode_.name_ in thisParrentNode.item_.keys():
				#N => Add the new dict item, insert not supported for dicts so we must recreate the sub-infoTree of all nodes after the ref node
				thisParrentNode.item_[newNode_.name_] = newNode_.item_				
				
		# Is this parrentNode a list Object?
		if thisParrentNode.isList():
			#Y
			# Has this item allready been added?
			if thisParrentNode.getNodeByItem(newNode_.name_, newNode_.item_) == "":			
				#N => Add new list item, hence nodeix + 1 => after node at ix
				thisParrentNode.item_.append(newNode_.item_)

		# Update new nodes sub-infoTree to reflect its json object structure
		#newNode_.setValue()		
				
		return newNode_

	# Add new nodeObj on thisNodes peerNode specified by Ix as new last-subNode
	def addNodeObjByIx(self, nodeIx_, newNode_, uniqueLevel_=-1):
		thisNode = self
		thisParrentNode = thisNode.parrentNode_

		# Is ix valid?
		if nodeIx_ < 0 or nodeIx_ > thisParrentNode.lastSubNodeIx_:
			#N => Signal failed to add Node
			self.error_ = "addNodeObjByIx: Cannot find a peerNode at ix " + str(nodeIx_)
			return ""

		# Find the Ref. Node
		thisNode = thisParrentNode.subNodes_[nodeIx_]
		thisParrentNode = thisNode

		# Auto discover item type and update thisNode uniquenessLevel
		# Is this parrentNode a dict object?
		if thisParrentNode.isOrderedDict():
			#Y => Set uniqunessLevel to peerNode uniqueness since a dict cannot contain duplicate keys
			uniqueLevel_ = 2

		# Has uniqueness level been specified?
		if uniqueLevel_ < 0:
			#N => Use/Enherit thisNodes
			uniqueLevel_ = thisNode.uniqueLevel_

		# Is this rootNode?
		if(thisParrentNode == ""):
			# YES => rootNode does not have peerNodes
			self.error_ = "addNodeObjByIx: rootNode does have peerNodes!!"
			return ""

		# Is node->value unique?
		# Is it infoTree Uniqueness?
		if(uniqueLevel_ == 1):
			# Does this node allready exist?
			thisRootNode = thisNode.getRootNode()
			existingNode = thisRootNode.findNodeByItem(newNode_.name_, newNode_.item_)
			if(existingNode != ""):
				# Node exist just update frequency "match count"
				existingNode.freq_ += 1				   
				return self
		# Is it peerNode Uniqueness?
		if(uniqueLevel_ == 2):
			# Does this node allready exist as a peerNode?
			existingNode = thisNode.findPeerNodeByItem(newNode_.name_, newNode_.item_)
			if(existingNode != ""):
				# Node exist just update frequency "match count"
				existingNode.freq_ += 1
				return self
		# Is it subNode Uniqueness?
		if(uniqueLevel_ == 3):
			# Does this node allready exist as a subNode?
			existingNode = thisNode.findSubNodeByItem(newNode_.name_, newNode_.item_)
			if(existingNode != ""):
				# Node exist just update freq "match count"
				existingNode.freq_ += 1
				return self
		# Is it sub-infoTree Uniqueness
		if(uniqueLevel_ == 4):
			# Does this node allready exist as a subNode?
			existingNode = thisNode.findNodeByItem(newNode_.name_, newNode_.item_)
			if(existingNode != ""):
				# Node exist just update freq "match count"
				existingNode.freq_ += 1
				return self

		# Assume the node does not exist
		# update this parrentNodes subNode structure "sub-infoTree"
		# Does this subNode allready Exist?
		for node in thisParrentNode.subNodes_:
			# Is newNode == to someNode?
			if newNode_.name_ == node.name_:
				#Y => Signal tryed to add existing node
				thisNode.error_ = "addNodeObjIx: node " + newNode_.name_ + " allready exist in sub-nodeTree of parrentNode " + thisParrentNode.name_
				# Forced exit node allready exists
				return thisNode

		# Ensure the newPeerNode has been associated/linked to thisNodes parrentNode
		newNode_.parrentNode_ = thisNode.parrentNode_
		# Ensure the newPeerNode has the specified uniqueness level
		newNode_.uniqueLevel_ = uniqueLevel_

		# Add the new peerNode
		thisParrentNode.subNodes_.append(newNode_)
		
		# Update sub node count
		thisParrentNode.lastSubNodeIx_ += 1
		# Ensure nodeIx has lastNode ix so it can be fixed 
		newNode_.nodeIx_ = thisParrentNode.lastSubNodeIx_

		# Fix newPeerNode & its sub-infoTree nodeId's
		newNode_.updateSubinfoTreeNodeIds()

		# Auto discover item type and update this parrentNodes json object structure "sub-infoTree"
		# Is this parrentNode a dict object?
		if thisParrentNode.isOrderedDict():
			#Y => Has this key allready been added?
			if not newNode_.name_ in thisParrentNode.item_.keys():
				#N => Add the new dict item, insert not supported for dicts so we must recreate the sub-infoTree of all nodes after the ref node
				thisParrentNode.item_[newNode_.name_] = newNode_.item_				
				
		# Is this parrentNode a list Object?
		if thisParrentNode.isList():
			#Y
			# Has this item allready been added?
			if thisParrentNode.getNodeByItem(newNode_.name_, newNode_.item_) == "":
				#N => Add new list item, hence nodeix + 1 => after node at ix
				thisParrentNode.item_.append(newNode_.item_)

		# Update new nodes sub-infoTree to reflect its json object structure
		#newNode_.setValue()	

		return newNode_

#-------------------- ADD peerNode Handling (Search From thisNodes to end of its sub-infoTree) -----------	   
	# Add new peerNodeObj on same parrentNode/nodeChain as thisNode as new last-subNode
	# STATUS: TESTED->OK
	def addPeerNodeObj(self, newNode_, uniqueLevel_=-1):
		thisNode = self
		thisParrentNode = thisNode.parrentNode_
			 
		# Auto discover item type and update thisNode uniquenessLevel
		# Is this parrentNode a dict object?
		if thisParrentNode.isOrderedDict():
			#Y => Set uniqunessLevel to peerNode uniqueness since a dict cannot contain duplicate keys
			uniqueLevel_ = 2

		# Has uniqueness level been specified?
		if uniqueLevel_ < 0:
			#N => Use/Enherit thisNodes
			uniqueLevel_ = thisNode.uniqueLevel_

		# Is this rootNode?
		if(thisParrentNode == ""):
			# YES => rootNode does not have peerNodes
			self.error_ = "addPeerNodeObj: rootNode does have peerNodes!!"
			return ""

		# Is node->value unique?
		# Is it infoTree Uniqueness?
		if(uniqueLevel_ == 1):
			# Does this node allready exist?
			thisRootNode = thisNode.getRootNode()
			existingNode = thisRootNode.findNodeByItem(newNode_.name_, newNode_.item_)
			if(existingNode != ""):
				# Node exist just update frequency "match count"
				existingNode.freq_ += 1				   
				return self
		# Is it peerNode Uniqueness?
		if(uniqueLevel_ == 2):
			# Does this node allready exist as a peerNode?
			existingNode = thisNode.findPeerNodeByItem(newNode_.name_, newNode_.item_)
			if(existingNode != ""):
				# Node exist just update frequency "match count"
				existingNode.freq_ += 1
				return self
		# Is it subNode Uniqueness?
		if(uniqueLevel_ == 3):
			# Does this node allready exist as a subNode?
			existingNode = thisNode.findSubNodeByItem(newNode_.name_, newNode_.item_)
			if(existingNode != ""):
				# Node exist just update freq "match count"
				existingNode.freq_ += 1
				return self
		# Is it sub-infoTree Uniqueness
		if(uniqueLevel_ == 4):
			# Does this node allready exist as a subNode?
			existingNode = thisNode.findNodeByItem(newNode_.name_, newNode_.item_)
			if(existingNode != ""):
				# Node exist just update freq "match count"
				existingNode.freq_ += 1
				return self

		# Assume the node does not exist
		# update this parrentNodes subNode structure "sub-infoTree"
		# Does this subNode allready Exist?
		for node in thisParrentNode.subNodes_:
			# Is newNode == to someNode?
			if newNode_.name_ == node.name_:
				#Y => Signal tryed to add existing node
				thisNode.error_ = "addPeerNodeObj: node " + newNode_.name_ + " allready exist in sub-nodeTree of parrentNode " + thisParrentNode.name_
				# Forced exit node allready exists
				return thisNode

		# Ensure the newPeerNode has been associated/linked to thisNodes parrentNode
		newNode_.parrentNode_ = thisNode.parrentNode_
		# Ensure the newPeerNode has the specified uniqueness level
		newNode_.uniqueLevel_ = uniqueLevel_

		# Add the new peerNode
		thisParrentNode.subNodes_.append(newNode_)
		
		# Update sub node count
		thisParrentNode.lastSubNodeIx_ += 1
		# Ensure nodeIx has lastNode ix so it can be fixed 
		newNode_.nodeIx_ = thisParrentNode.lastSubNodeIx_

		# Fix newPeerNode & its sub-infoTree nodeId's
		newNode_.updateSubinfoTreeNodeIds()

		# Auto discover item type and update this parrentNodes json object structure "sub-infoTree"
		# Is this parrentNode a dict object?
		if thisParrentNode.isOrderedDict():
			#Y => Has this key allready been added?
			if not newNode_.name_ in thisParrentNode.item_.keys():
				#N => Add the new dict item, insert not supported for dicts so we must recreate the sub-infoTree of all nodes after the ref node
				thisParrentNode.item_[newNode_.name_] = newNode_.item_				
				
		# Is this parrentNode a list Object?
		if thisParrentNode.isList():
			#Y
			# Has this item allready been added?
			if thisParrentNode.getNodeByItem(newNode_.name_, newNode_.item_) == "":			
				#N => Add new list item, hence nodeix + 1 => after node at ix
				thisParrentNode.item_.append(newNode_.item_)

		# Update new nodes sub-infoTree to reflect its json object structure
		#newNode_.setValue()		

		return newNode_

	# Add new peerNodeObj (by value) relative to Node Specified by Id as new last-peerNode, Search from thisNodes to end of its sub-infoTree
	# use rootNode if you are unsure where the node is located
	def addPeerNodeObjById(self, nodeId_, newNode_, uniqueLevel_=-1):
		thisNode = self
		startNode = thisNode

		# Find the reference node
		thisParrentNode=""
		while(thisNode != ""):
			# Is this the node we are looking for?
			if(thisNode.nodeId_.lower() == nodeId_.lower()):
				thisParrentNode = thisNode.parrentNode_
				break

			# Get next node
			thisNode = thisNode.getNextNode(startNode)

		# Was the ref. node found?
		if(thisParrentNode == ""):
			# NO
			self.error_ = "addPeerNodeObjById: Unable to find node with Id" + nodeId_			 
			return ""

		# Auto discover item type and update thisNode uniquenessLevel
		# Is this parrentNode a dict object?
		if thisParrentNode.isOrderedDict():
			#Y => Set uniqunessLevel to peerNode uniqueness since a dict cannot contain duplicate keys
			uniqueLevel_ = 2			

		#Has uniquenessLevel been specified?
		if uniqueLevel_ < 0:
			#N => Use/Enherit from thisNode
			uniqueLevel_ = thisNode.uniqueLevel_
		
		# Is node->value unique?
		# Is it infoTree Uniqueness?
		if(uniqueLevel_ == 1):
			# Does this node allready exist?
			thisRootNode = thisNode.getRootNode()
			existingNode = thisRootNode.findNodeByItem(newNode_.name_, newNode_.item_)
			if(existingNode != ""):
				# Node exist just update frequency "match count"
				existingNode.freq_ += 1				   
				return self
		# Is it peerNode Uniqueness?
		if(uniqueLevel_ == 2):
			# Does this node allready exist as a peerNode?
			existingNode = thisNode.findPeerNodeByItem(newNode_.name_, newNode_.item_)
			if(existingNode != ""):
				# Node exist just update frequency "match count"
				existingNode.freq_ += 1
				return self
		# Is it subNode Uniqueness?
		if(uniqueLevel_ == 3):
			# Does this node allready exist as a subNode?
			existingNode = thisNode.findSubNodeByItem(newNode_.name_, newNode_.item_)
			if(existingNode != ""):
				# Node exist just update freq "match count"
				existingNode.freq_ += 1
				return self
		# Is it sub-infoTree Uniqueness
		if(uniqueLevel_ == 4):
			# Does this node allready exist as a subNode?
			existingNode = thisNode.findNodeByItem(newNode_.name_, newNode_.item_)
			if(existingNode != ""):
				# Node exist just update freq "match count"
				existingNode.freq_ += 1
				return self
		
		# Assume the ref. node was found
		# update this parrentNodes subNode structure "sub-infoTree"
		# Does this subNode allready Exist?
		for node in thisParrentNode.subNodes_:
			# Is newNode == to someNode?
			if newNode_.name_ == node.name_:
				#Y => Signal tryed to add existing node
				thisNode.error_ = "addPeerNodeObjById: node " + newNode_.name_ + " allready exist in sub-nodeTree of parrentNode " + thisParrentNode.name_
				# Forced exit node allready exists
				return thisNode

		# Assume the node does not exist
		# Ensure the newPeerNode has been associated/linked to thisNodes parrentNode
		newNode_.parrentNode_ = thisNode.parrentNode_ 
		# Ensure the newPeerNode has the specified uniqueness level
		newNode_.uniqueLevel_ = uniqueLevel_		

		# Add the new peerNode
		thisParrentNode.subNodes_.append(newNode_)

		# Update sub node count
		thisParrentNode.lastSubNodeIx_ += 1
		# Ensure nodeIx is has lastNode ix so it can be fixed 
		newNode_.nodeIx_ = thisParrentNode.lastSubNodeIx_		  

		# Fix newPeerNode & its sub-infoTree nodeId's
		newNode_.updateSubinfoTreeNodeIds()

		# Auto discover item type and update this parrentNodes json object structure "sub-infoTree"
		# Is this parrentNode a dict object?
		if thisParrentNode.isOrderedDict():
			#Y => Has this key allready been added?
			if not newNode_.name_ in thisParrentNode.item_.keys():
				#N => Add the new dict item, insert not supported for dicts so we must recreate the sub-infoTree of all nodes after the ref node
				thisParrentNode.item_[newNode_.name_] = newNode_.item_				
				
		# Is this parrentNode a list Object?
		if thisParrentNode.isList():
			#Y
			# Has this item allready been added?
			if thisParrentNode.getNodeByItem(newNode_.name_, newNode_.item_) == "":			
				#N => Add new list item, hence nodeix + 1 => after node at ix
				thisParrentNode.item_.append(newNode_.item_)

		# Update new nodes sub-infoTree to reflect its json object structure
		#newNode_.setValue()		

		return newNode_

	# Add new peerNodeObj (by value) relative to Node Specified by Name as new last-peerNode, Search from thisNode and to end of its sub-infoTree
	# use rootNode if you are unsure where the node is located
	# uniquenessLevel refferes to name
	def addPeerNodeObjByName(self, name_, newNode_, uniqueLevel_=-1):
		thisNode = self
		startNode = thisNode

		# Find the reference node
		thisParrentNode=""
		while(thisNode != ""):
			# Is this the node we are looking for?
			if(thisNode.name_.lower() == name_.lower()):
				thisParrentNode = thisNode.parrentNode_
				break

			# Get next node
			thisNode = thisNode.getNextNode(startNode)

		# Was the ref. node found?
		if(thisParrentNode == ""):
			# NO
			self.error_ = "addPeerNodeObjByName: Unable to find node with name " + name_			
			return ""

		# Auto discover item type and update thisNode uniquenessLevel
		# Is this parrentNode a dict object?
		if thisParrentNode.isOrderedDict():
			#Y => Set uniqunessLevel to peerNode uniqueness since a dict cannot contain duplicate keys
			uniqueLevel_ = 2			

		# Has a uniquenessLevel been specified?
		if uniqueLevel_ < 0:
			#N => Use/Enheri thisNodes
			uniqueLevel_ = thisNode.uniqueLevel_
		
		# Is node->value unique?
		# Is it infoTree Uniqueness?
		if(uniqueLevel_ == 1):
			# Does this node allready exist?
			thisRootNode = thisNode.getRootNode()			 
			existingNode = thisRootNode.findNodeByName(newNode_.name_)
			if(existingNode != ""):
				# Node exit just update frequency "match count"
				existingNode.freq_ += 1
				return self
		# Is it peerNode Uniqueness?
		if(uniqueLevel_ == 2):
			# Does this node allready exist as a peerNode?
			existingNode = thisNode.findPeerNodeByName(newNode_.name_)
			if(existingNode != ""):
				# Node exist just update frequency "match count"
				existingNode.freq_ += 1
				return self
		# Is it subNode Uniqueness?
		if(uniqueLevel_ == 3):
			# Does this node allready exist as a subNode?
			existingNode = thisNode.findSubNodeByName(newNode_.name_)
			if(existingNode != ""):
				# Node exist just update freq "match count"
				existingNode.freq_ += 1
				return self
		# Is it sub-infoTree Uniqueness
		if(uniqueLevel_ == 4):
			# Does this node allready exist as a subNode?
			existingNode = thisNode.findNodeByName(newNode_.name_)
			if(existingNode != ""):
				# Node exist just update freq "match count"
				existingNode.freq_ += 1
				return self
		
		# Assume the ref. node was found
		# update this parrentNodes subNode structure "sub-infoTree"
		# Does this subNode allready Exist?
		for node in thisParrentNode.subNodes_:
			# Is newNode == to someNode?
			if newNode_.name_ == node.name_:
				#Y => Signal tryed to add existing node
				thisNode.error_ = "addPeerNodeObjName: node " + newNode_.name_ + " allready exist in sub-nodeTree of parrentNode " + thisParrentNode.name_
				# Forced exit node allready exists
				return thisNode

		# Assume the node does not exist
		# Ensure the newPeerNode has been associated/linked to thisNodes parrentNode
		newNode_.parrentNode_ = thisNode.parrentNode_ 
		# Ensure the newPeerNode has the specified uniqueness level
		newNode_.uniqueLevel_ = uniqueLevel_

		# Add the new peerNode
		thisParrentNode.subNodes_.append(newNode_)

		# Update sub node count
		thisNode.parrentNode_.lastSubNodeIx_ += 1
		# Ensure nodeIx is has lastNode ix so it can be fixed 
		newNode_.nodeIx_ = thisNode.parrentNode_.lastSubNodeIx_	  

		# Fix newPeerNode & its sub-infoTree nodeId's
		newNode_.updateSubinfoTreeNodeIds()

		# Auto discover item type and update this parrentNodes json object structure "sub-infoTree"
		# Is this parrentNode a dict object?
		if thisParrentNode.isOrderedDict():
			#Y => Has this key allready been added?
			if not newNode_.name_ in thisParrentNode.item_.keys():
				#N => Add the new dict item, insert not supported for dicts so we must recreate the sub-infoTree of all nodes after the ref node
				thisParrentNode.item_[newNode_.name_] = newNode_.item_				
				
		# Is this parrentNode a list Object?
		if thisParrentNode.isList():
			#Y
			# Has this item allready been added?
			if thisParrentNode.getNodeByItem(newNode_.name_, newNode_.item_) == "":			
				#N => Add new list item, hence nodeix + 1 => after node at ix
				thisParrentNode.item_.append(newNode_.item_)

		# Update new nodes sub-infoTree to reflect its json object structure
		#newNode_.setValue()		
				
		return newNode_

	# Add new peerNodeObj (by value) relative to Node Specified by Value as new last-peerNode, Search from thisNode and to end of its sub-infoTree
	# use rootNode if you are unsure where the node is located
	# uniquenessLevel refferes to name
	def addPeerNodeObjByValue(self, value_, newNode_, uniqueLevel_=-1):
		thisNode = self
		startNode = thisNode

		# Find the reference node
		thisParrentNode=""
		while(thisNode != ""):
			# Is this the node we are looking for?
			# Is thisNode and value a ordered dict object
			if thisNode.isOrderedDict() and thisNode.isOrderedDict(value_):
				#Y => Is this the value we are looking for
				if thisNode.item_ == value_:
					#Y
					thisParrentNode = thisNode.parrentNode_
					break

			# Is thisNode and value a list object
			if thisNode.isList() and thisNode.isList(value_):
				#Y => Is this the value we are looking for
				if thisNode.item_ == value_:
					#Y
					thisParrentNode = thisNode.parrentNode_
					break					

			# Is thisNode and value a string
			if thisNode.isString() and thisNode.isString(value_):
				#Y => Is this the value we are looking for
				if(thisNode.item_.lower() == value_.lower()):
					#Y
					thisParrentNode = thisNode.parrentNode_
					break

			# Is thisNode and value a number
			if thisNode.isNumber() and thisNode.isNumber(value_):
				#Y => Is this the value we are looking for
				if thisNode.item_ == value_:
					#Y
					thisParrentNode = thisNode.parrentNode_
					break

			# Get next node
			thisNode = thisNode.getNextNode(startNode)

		# Was the ref. node found?
		if(thisParrentNode == ""):
			# NO
			self.error_ = "addPeerNodeObjByName: Unable to find node with name " + name_			
			return ""

		# Auto discover item type and update thisNode uniquenessLevel
		# Is this parrentNode a dict object?
		if thisParrentNode.isOrderedDict():
			#Y => Set uniqunessLevel to peerNode uniqueness since a dict cannot contain duplicate keys
			uniqueLevel_ = 2			

		# Has a uniquenessLevel been specified?
		if uniqueLevel_ < 0:
			#N => Use/Enheri thisNodes
			uniqueLevel_ = thisNode.uniqueLevel_
		
		# Is node->value unique?
		# Is it infoTree Uniqueness?
		if(uniqueLevel_ == 1):
			# Does this node allready exist?
			thisRootNode = thisNode.getRootNode()			 
			existingNode = thisRootNode.findNodeByName(newNode_.name_)
			if(existingNode != ""):
				# Node exit just update frequency "match count"
				existingNode.freq_ += 1
				return self
		# Is it peerNode Uniqueness?
		if(uniqueLevel_ == 2):
			# Does this node allready exist as a peerNode?
			existingNode = thisNode.findPeerNodeByName(newNode_.name_)
			if(existingNode != ""):
				# Node exist just update frequency "match count"
				existingNode.freq_ += 1
				return self
		# Is it subNode Uniqueness?
		if(uniqueLevel_ == 3):
			# Does this node allready exist as a subNode?
			existingNode = thisNode.findSubNodeByName(newNode_.name_)
			if(existingNode != ""):
				# Node exist just update freq "match count"
				existingNode.freq_ += 1
				return self
		# Is it sub-infoTree Uniqueness
		if(uniqueLevel_ == 4):
			# Does this node allready exist as a subNode?
			existingNode = thisNode.findNodeByName(newNode_.name_)
			if(existingNode != ""):
				# Node exist just update freq "match count"
				existingNode.freq_ += 1
				return self
		
		# Assume the ref. node was found
		# update this parrentNodes subNode structure "sub-infoTree"
		# Does this subNode allready Exist?
		for node in thisParrentNode.subNodes_:
			# Is newNode == to someNode?
			if newNode_.name_ == node.name_:
				#Y => Signal tryed to add existing node
				thisNode.error_ = "addPeerNodeObjName: node " + newNode_.name_ + " allready exist in sub-nodeTree of parrentNode " + thisParrentNode.name_
				# Forced exit node allready exists
				return thisNode

		# Assume the node does not exist
		# Ensure the newPeerNode has been associated/linked to thisNodes parrentNode
		newNode_.parrentNode_ = thisNode.parrentNode_ 
		# Ensure the newPeerNode has the specified uniqueness level
		newNode_.uniqueLevel_ = uniqueLevel_

		# Add the new peerNode
		thisParrentNode.subNodes_.append(newNode_)

		# Update sub node count
		thisNode.parrentNode_.lastSubNodeIx_ += 1
		# Ensure nodeIx is has lastNode ix so it can be fixed 
		newNode_.nodeIx_ = thisNode.parrentNode_.lastSubNodeIx_	  

		# Fix newPeerNode & its sub-infoTree nodeId's
		newNode_.updateSubinfoTreeNodeIds()

		# Auto discover item type and update this parrentNodes json object structure "sub-infoTree"
		# Is this parrentNode a dict object?
		if thisParrentNode.isOrderedDict():
			#Y => Has this key allready been added?
			if not newNode_.name_ in thisParrentNode.item_.keys():
				#N => Add the new dict item, insert not supported for dicts so we must recreate the sub-infoTree of all nodes after the ref node
				thisParrentNode.item_[newNode_.name_] = newNode_.item_				
				
		# Is this parrentNode a list Object?
		if thisParrentNode.isList():
			#Y
			# Has this item allready been added?
			if thisParrentNode.getNodeByItem(newNode_.name_, newNode_.item_) == "":			
				#N => Add new list item, hence nodeix + 1 => after node at ix
				thisParrentNode.item_.append(newNode_.item_)

		# Update new nodes sub-infoTree to reflect its json object structure
		#newNode_.setValue()		
				
		return newNode_

# -------- SPECIAL DICT INSERT/REPLACE ITEM METHOD TO PRESERVE DICT OBJECT -------
	# Method thats inserts a new item relative to "before" item specified by key, in dict object while preserving existing items
	def insertDictItemByKey(self, key_, newKey_, newValue_ = "", node_ = ""):
		# Has node object been specified?
		if node_ == "":
			#N => Assume thisNode item is the dict
			node_ = self

		# Does the specified key exist?
		if not key_ in node_.item_.keys():
			#N => Signal failed to insert item
			self.error_ = "insertDictItemByKey: Cannont find item with key " + key_
			return ""

		# Does newKey allready Exist?
		if newKey_ in node_.item_.keys():
			#Y => Signal failed to insert item
			self.error_ = "insertDictItemByKey: new key " + newKey_ + " allready exists in the dict"
			return ""			

		#Insert the new dict item, insert not supported for dicts so we must recreate the sub-infoTree of all nodes after the ref node
		# Create temp Dict that keeps track of all affected items
		tempDict = OrderedDict()
		# Add the item "key:value pair" that should be inserted
		tempDict[newKey_] = newValue_
		# Copy thisDict and remove items one by one, hence preserve original dict so all nodes related/linked to thisDict, does not loose there relation to thisDict "ensure item is not replaced"
		ix = 0
		refIx = -1
		for k, v in node_.item_.items():
			# Is this the item we are looking for?
			if k == key_:
				#Y
				# Keep track of ref item
				refIx = ix
			
			# Is thisItem located after or at ref item?
			if ix >= refIx and refIx != -1:
				# Y => keep track of this item
				tempDict[k] = v
				# Remove item form thisDict
				node_.item_.pop(k)

			# Update item ix
			ix += 1

		# Readded removed items incl. the inserted item in correct order
		for k, v in tempDict.items():
			node_.item_[k] = v
		
		return node_

	# Method that inserts a new item relative to "before" item specified by ix, in dict while preserving exisiting items
	def insertDictItemByIx(self, ix_, newKey_, newValue_ = "", node_ = ""):
		# Has dict object been specified?
		if node_ == "":
			#N => Assume thisNode item is the dict
			node_ = self

		# Does the specified key exist?
		# Calc last ix "NOTE DICTS USE BINARY MATH SO LEN REFFERES TO LAST ITEM IX AND NOT SIZE OF DICT"
		lastItemIx = len(node_.item_)
		if ix_ > lastItemIx:
			#N => Signal failed to insert dict
			self.error_ = "insertDictItemByIx: Cannont find item at ix " + str(ix_) + ", last item ix was " + str(lastItemIx)
			return ""

		# Does newKey allready Exist?
		if newKey_ in node_.item_.keys():
			#Y => Signal failed to insert item
			self.error_ = "insertDictItemByIx: new key " + newKey_ + " allready exists in the dict"
			return ""						

		#Insert the new dict item, insert not supported for dicts so we must recreate the sub-infoTree of all nodes after the ref node
		# Create temp Dict that keeps track of all affected items
		tempDict = OrderedDict()
		# Add the item "key:value pair" that should be inserted
		tempDict[newKey_] = newValue_

		while(1):
			# Copy thisDict and remove items one by one, hence preserve original dict so all nodes related/linked to thisDict, does not loose there relation to thisDict "ensure item is not replaced"
			ix = 0
			# Set specified ref ix
			refIx = ix_
			for k, v in node_.item_.items():			
				# Is thisItem located after or at ref item?
				if ix >= refIx and refIx != -1:
					# Y => keep track of this item
					tempDict[k] = v
					# Remove item form thisDict
					node_.item_.pop(k)
					# Forced exit dict has been modified and iteration needs to restart
					break

				# Update item ix
				ix += 1

			# Has all childItems been checked?
			if ix >= len(node_.item_):
				#Y => Forced exit insert complete
				break

		# Readded removed items incl. the inserted item in correct order
		for k, v in tempDict.items():
			node_.item_[k] = v		

		return node_
# ------------ REPLACE -----------
	# Method thats replaces dict item specified by key with a new item, in dict object while preserving existing items
	def replaceDictItemByKey(self, key_, newKey_, newValue_ = "", node_ = ""):
		# Has dict object been specified?
		if node_ == "":
			#N => Assume thisNode item is the dict
			node_ = self

		# Does the specified key exist?
		if not key_ in node_.item_.keys():
			#N => Signal failed to insert dict
			self.error_ = "replaceDictItemByKey: Cannont find item with key " + key_
			return ""

		# Does newKey allready Exist?
		if newKey_ in node_.item_.keys():
			#Y => Signal failed to insert item
			self.error_ = "replaceDictItemByKey: new key " + newKey_ + " allready exists in the dict"
			return ""						

		#Insert the new dict item, insert not supported for dicts so we must recreate the sub-infoTree of all nodes after the ref node
		# Create temp Dict that keeps track of all affected items
		tempDict = OrderedDict()
		# Add the new item "key:value pair" that should replace ref item
		tempDict[newKey_] = newValue_
		# Copy thisDict and remove items one by one, hence preserve original dict so all nodes related/linked to thisDict, does not loose there relation to thisDict "ensure item is not replaced"
		ix = 0
		refIx = -1
		for k, v in node_.item_.items():
			# Is this the item we are looking for?
			if k == key_:
				#Y
				# remove the item to replace
				node_.item_.pop(k)
				# Keep track of ref item
				refIx = ix
			
			# Is thisItem located after ref item?
			if ix > refIx and refIx != -1:
				# Y => keep track of this item
				tempDict[k] = v
				# Remove item form thisDict
				node_.item_.pop(k)

			# Update item ix
			ix += 1

		# Readded removed items incl. the replaced item in correct order
		for k, v in tempDict.items():
			node_.item_[k] = v
		
		return node_

	# Method that replaces dict item specified by ix with a new item, in dict while preserving exisiting items
	def replaceDictItemByIx(self, ix_, newKey_, newValue_ = "", node_ = ""):
		# Has dict object been specified?
		if node_ == "":
			#N => Assume thisNode item is the dict
			node_ = self

		# Does the specified key exist?
		# Calc last ix
		lastItemIx = len(node_.item_)
		if ix_ > lastItemIx:
			#N => Signal failed to insert dict
			self.error_ = "replaceDictItemByIx: Cannont find item at ix " + str(ix_) + ", last item ix was " + str(lastItemIx)
			return ""

		# Does newKey allready Exist?
		if newKey_ in node_.item_.keys():
			#Y => Signal failed to insert item
			self.error_ = "replaceDictItemByIx: new key " + newKey_ + " allready exists in the dict"
			return ""						

		#Insert the new dict item, insert not supported for dicts so we must recreate the sub-infoTree of all nodes after the ref node
		# Create temp Dict that keeps track of all affected items
		tempDict = OrderedDict()
		# Add the item "key:value pair" that should replace the ref item
		tempDict[newKey_] = newValue_
		# Copy thisDict and remove items one by one, hence preserve original dict so all nodes related/linked to thisDict, does not loose there relation to thisDict "ensure item is not replaced"
		ix = 0
		# Set specified ref ix
		refIx = ix_
		for k, v in node_.item_.items():
			# Is thisItem the ref item?
			if ix == refIx:
				# Y => Remove the item to replace
				node_.item_.pop(k)

			# Is thisItem located after ref item?
			if ix > refIx and refIx != -1:
				# Y => keep track of this item
				tempDict[k] = v
				# Remove item form thisDict
				node_.item_.pop(k)

			# Update item ix
			ix += 1

		# Readded removed items incl. the replaced item in correct order
		for k, v in tempDict.items():
			node_.item_[k] = v		

		return node_

# -------- END OF SPECIAL DICT METHOD ---------
# -----------  ADD subNode Handling (Search From thisNodes to end of its sub-infoTree) -------
	# Add new subNodeObj to thisNode as new last-subNode
	# STATUS: TESTED->OK
	def addSubNodeObj(self, newNode_, uniqueLevel_=-1):
		thisNode = self

		# Auto discover item type and update thisNode uniquenessLevel
		# Is this parrentNode a dict object?
		if thisNode.isOrderedDict():
			#Y => Set uniqunessLevel to peerNode uniqueness since a dict cannot contain duplicate keys
			uniqueLevel_ = 2		

		# Has uniquenessLevel been specified
		if uniqueLevel_ < 0:
			#N => Use/Enherit thisNodes
			uniqueLevel_ = self.uniqueLevel_
		
		# Is node->value unique?
		# Is it infoTree Uniqueness?
		if(uniqueLevel_ == 1):
			# Does this node allready exist?
			thisRootNode = thisNode.getRootNode()
			existingNode = thisRootNode.findNodeByItem(newNode_.name_, newNode_.item_)
			if(existingNode != ""):
				# Node exist just update frequency "match count"
				existingNode.freq_ += 1				   
				return self
		# Is it peerNode Uniqueness?
		if(uniqueLevel_ == 2):
			# Does this node allready exist as a peerNode?
			existingNode = thisNode.findPeerNodeByItem(newNode_.name_, newNode_.item_)
			if(existingNode != ""):
				# Node exist just update frequency "match count"
				existingNode.freq_ += 1
				return self
		# Is it subNode Uniqueness?
		if(uniqueLevel_ == 3):
			# Does this node allready exist as a subNode?
			existingNode = thisNode.findSubNodeByItem(newNode_.name_, newNode_.item_)
			if(existingNode != ""):
				# Node exist just update freq "match count"
				existingNode.freq_ += 1
				return self
		# Is it sub-infoTree Uniqueness
		if(uniqueLevel_ == 4):
			# Does this node allready exist as a subNode?
			existingNode = thisNode.findNodeByItem(newNode_.name_, newNode_.item_)
			if(existingNode != ""):
				# Node exist just update freq "match count"
				existingNode.freq_ += 1
				return self

		# update this parrentNodes subNode structure "sub-infoTree"
		# Does this subNode allready Exist?
		for node in thisNode.subNodes_:
			# Is newNode == to someNode?
			if newNode_.name_ == node.name_:
				#Y => Signal tryed to add existing node
				self.error_ = "addSubNodeObj: node " + newNode_.name_ + " allready exist in sub-nodeTree of parrentNode " + thisNode.name_
				# Forced exit node allready exists
				return self

		# Ensure the newSubNode has been associated/linked to thisNodes, has thisNode as parrentNode
		newNode_.parrentNode_ = thisNode
		# Ensure the newSubNode has the specified uniqueness level
		newNode_.uniqueLevel_ = uniqueLevel_
		
		# Add the new subNode
		thisNode.subNodes_.append(newNode_)

		# Update sub node count
		thisNode.lastSubNodeIx_ += 1
		# Ensure nodeIx is has lastNode ix so it can be fixed 
		newNode_.nodeIx_ = thisNode.lastSubNodeIx_		

		# Fix newSubNode & its sub-infoTree nodeId's
		newNode_.updateSubinfoTreeNodeIds()

		# Auto discover item type and update this parrentNodes json object structure "sub-infoTree"
		# Is this parrentNode a dict object?
		if thisNode.isOrderedDict():
			#Y => Has this key allready been added?
			if not newNode_.name_ in thisNode.item_.keys():
				#N => Add the new dict item, insert not supported for dicts so we must recreate the sub-infoTree of all nodes after the ref node
				thisNode.item_[newNode_.name_] = newNode_.item_				
				
		# Is this parrentNode a list Object?
		if thisNode.isList():
			#Y
			# Has this item allready been added?
			if thisNode.getNodeByItem(newNode_.name_, newNode_.item_) == "":
				#N => Add new list item, hence nodeix + 1 => after node at ix
				thisNode.item_.append(newNode_.item_)

		# Update new nodes sub-infoTree to reflect its json object structure
		#newNode_.setValue()		
		
		return newNode_

	# Add new subNodeObj (by value) to Node Specified by Id as new last-subNode, Search from thisNode and to end of its sub-infoTree unless startNode has been specified
	# use rootNode if you are unsure where the node is located
	def addSubNodeObjById(self, nodeId_, newNode_, uniqueLevel_=-1, startNode_ = ""):
		thisNode = self
		startNode = startNode_
		
		# Has node search been restricted to a specific endNode?
		if startNode_ == "":
			#N => Assume thisNode sub-infoTree 
			startNode = thisNode

		# Find the reference node
		thisParrentNode=""
		while(thisNode != ""):
			# Is this the node we are looking for?
			if(thisNode.nodeId_.lower() == nodeId_.lower()):
				thisParrentNode = thisNode.parrentNode_
				break

			# Get next node
			thisNode = thisNode.getNextNode(startNode)

		# Was the ref. node found?
		if(thisParrentNode == ""):
			# NO
			self.error_ = "addSubNodeObjById: Unable to find node with Id " + nodeId_			 
			return self

		# Auto discover item type and update thisNode uniquenessLevel
		# Is this parrentNode a dict object?
		if thisParrentNode.isOrderedDict():
			#Y => Set uniqunessLevel to peerNode uniqueness since a dict cannot contain duplicate keys
			uniqueLevel_ = 2

		# Has uniquenessLevel been specified?
		if uniqueLevel_ < 0:
			#N => Use/Enherit thisNodes
			uniqueLevel_ = thisNode.uniqueLevel_
		
		# Is node->value unique?
		# Is it infoTree Uniqueness?
		if(uniqueLevel_ == 1):
			# Does this node allready exist?
			thisRootNode = thisNode.getRootNode()
			existingNode = thisRootNode.findNodeByItem(newNode_.name_, newNode_.item_)
			if(existingNode != ""):
				# Node exist just update frequency "match count"
				existingNode.freq_ += 1				   
				return self
		# Is it peerNode Uniqueness?
		if(uniqueLevel_ == 2):
			# Does this node allready exist as a peerNode?
			existingNode = thisNode.findPeerNodeByItem(newNode_.name_, newNode_.item_)
			if(existingNode != ""):
				# Node exist just update frequency "match count"
				existingNode.freq_ += 1
				return self
		# Is it subNode Uniqueness?
		if(uniqueLevel_ == 3):
			# Does this node allready exist as a subNode?
			existingNode = thisNode.findSubNodeByItem(newNode_.name_, newNode_.item_)
			if(existingNode != ""):
				# Node exist just update freq "match count"
				existingNode.freq_ += 1
				return self
		# Is it sub-infoTree Uniqueness
		if(uniqueLevel_ == 4):
			# Does this node allready exist as a subNode?
			existingNode = thisNode.findNodeByItem(newNode_.name_, newNode_.item_)
			if(existingNode != ""):
				# Node exist just update freq "match count"
				existingNode.freq_ += 1
				return self
		
		# Assume the ref. node was found
		# update this parrentNodes subNode structure "sub-infoTree"
		# Does this subNode allready Exist?
		for node in thisParrentNode.subNodes_:
			# Is newNode == to someNode?
			if newNode_.name_ == node.name_:
				#Y => Signal tryed to add existing node
				self.error_ = "addSubNodeObjById: node " + newNode_.name_ + " allready exist in sub-nodeTree of parrentNode " + thisNode.name_
				# Forced exit node allready exists
				return self

		# Assume the node does not exist		
		# Ensure the newSubNode has been associated/linked to thisNodes, has thisNode as parrentNode
		newNode_.parrentNode_ = thisNode
		# Ensure the newSubNode has the specified uniqueness level
		newNode_.uniqueLevel_ = uniqueLevel_		   
		
		# Add the new subNode
		thisNode.subNodes_.append(newNode_)

		# Update sub node count
		thisNode.lastSubNodeIx_ += 1
		# Ensure nodeIx is has lastNode ix so it can be fixed 
		newNode_.nodeIx_ = thisNode.lastSubNodeIx_		

		# Fix newSubNode & its sub-infoTree nodeId's
		newNode_.updateSubinfoTreeNodeIds()

		# Auto discover item type and update this parrentNodes json object structure "sub-infoTree"
		# Is this parrentNode a dict object?
		if thisNode.isOrderedDict():
			#Y => Has this key allready been added?
			if not newNode_.name_ in thisNode.item_.keys():
				#N => Add the new dict item, insert not supported for dicts so we must recreate the sub-infoTree of all nodes after the ref node
				thisNode.item_[newNode_.name_] = newNode_.item_				
				
		# Is this parrentNode a list Object?
		if thisNode.isList():
			#Y
			# Has this item allready been added?
			if thisNode.getNodeByItem(newNode_.name_, newNode_.item_) == "":			
				#N => Add new list item, hence nodeix + 1 => after node at ix
				thisNode.item_.append(newNode_.item_)

		# Update new nodes sub-infoTree to reflect its json object structure
		#newNode_.setValue()				

		return newNode_

	# Add new subNodeObj (by value) to Node Specified by Name as new last-subNode, Search from thisNode and to end of its sub-infoTree unless startNode has been specified
	# use rootNode if you are unsure where the node is located
	def addSubNodeObjByName(self, name_, newNode_, uniqueLevel_=-1, startNode_ = ""):
		thisNode = self
		startNode = startNode_
		
		# Has node search been restricted to a specific endNode?
		if startNode_ == "":
			#N => Assume thisNode sub-infoTree 
			startNode = thisNode

		# Find the reference node
		thisParrentNode=""
		while(thisNode != ""):
			# Is this the node we are looking for?
			if(thisNode.name_.lower() == name_.lower()):
				thisParrentNode = thisNode.parrentNode_
				break

			# Get next node
			thisNode = thisNode.getNextNode(startNode)

		# Was the ref. node found?
		if(thisParrentNode == ""):
			# NO
			self.error_ = "addSubNodeObjByName: Unable to find node with name " + name_			   
			return self

		# Auto discover item type and update thisNode uniquenessLevel
		# Is this parrentNode a dict object?
		if thisParrentNode.isOrderedDict():
			#Y => Set uniqunessLevel to peerNode uniqueness since a dict cannot contain duplicate keys
			uniqueLevel_ = 2

		# Has uniquenessLevel been specified?
		if uniqueLevel_ < 0:
			#N => Use/Enherit thisNodes
			uniqueLevel_ = thisNode.uniqueLevel_
		
		# Is node->value unique?
		# Is it infoTree Uniqueness?
		if(uniqueLevel_ == 1):
			# Does this node allready exist?
			thisRootNode = thisNode.getRootNode()
			existingNode = thisRootNode.findNodeByName(newNode_.name_)
			if(existingNode != ""):
				# Node exist just update frequency "match count"
				existingNode.freq_ += 1				   
				return self
		# Is it peerNode Uniqueness?
		if(uniqueLevel_ == 2):
			# Does this node allready exist as a peerNode?
			existingNode = thisNode.findPeerNodeByName(newNode_.name_)
			if(existingNode != ""):
				# Node exist just update frequency "match count"
				existingNode.freq_ += 1
				return self
		# Is it subNode Uniqueness?
		if(uniqueLevel_ == 3):
			# Does this node allready exist as a subNode?
			existingNode = thisNode.findSubNodeByName(newNode_.name_)
			if(existingNode != ""):
				# Node exist just update freq "match count"
				existingNode.freq_ += 1
				return self
		# Is it sub-infoTree Uniqueness
		if(uniqueLevel_ == 4):
			# Does this node allready exist as a subNode?
			existingNode = thisNode.findNodeByName(newNode_.name_)
			if(existingNode != ""):
				# Node exist just update freq "match count"
				existingNode.freq_ += 1
				return self
		
		# Assume the ref. node was found
		# update this parrentNodes subNode structure "sub-infoTree"
		# Does this subNode allready Exist?
		for node in thisParrentNode.subNodes_:
			# Is newNode == to someNode?
			if newNode_.name_ == node.name_:
				#Y => Signal tryed to add existing node
				self.error_ = "addSubNodeObjByName: node " + newNode_.name_ + " allready exist in sub-nodeTree of parrentNode " + thisNode.name_
				# Forced exit node allready exists
				return self

		# Assume the node does not exist
		# Ensure the newSubNode has been associated/linked to thisNodes, has thisNode as parentNode
		newNode_.parrentNode_ = thisNode
		# Ensure the newSubNode has the specified uniqueness level
		newNode_.uniqueLevel_ = uniqueLevel_		   
		
		# Add the new subNode
		thisNode.subNodes_.append(newNode_)

		# Update sub node count
		thisNode.lastSubNodeIx_ += 1
		# Ensure nodeIx is has lastNode ix so it can be fixed 
		newNode_.nodeIx_ = thisNode.lastSubNodeIx_		

		# Fix newPeerNode & its sub-infoTree nodeId's
		newNode_.updateSubinfoTreeNodeIds()

		# Auto discover item type and update this parrentNodes json object structure "sub-infoTree"
		# Is this parrentNode a dict object?
		if thisNode.isOrderedDict():
			#Y => Has this key allready been added?
			if not newNode_.name_ in thisNode.item_.keys():
				#N => Add the new dict item, insert not supported for dicts so we must recreate the sub-infoTree of all nodes after the ref node
				thisNode.item_[newNode_.name_] = newNode_.item_				
				
		# Is this parrentNode a list Object?
		if thisNode.isList():
			#Y
			# Has this item allready been added?
			if thisNode.getNodeByItem(newNode_.name_, newNode_.item_) == "":			
				#N => Add new list item, hence nodeix + 1 => after node at ix
				thisNode.item_.append(newNode_.item_)

		# Update new nodes sub-infoTree to reflect its json object structure
		#newNode_.setValue()				

		return newNode_

	# Add new subNodeObj (by value) to Node Specified by Value as new last-subNode, Search from thisNode and to end of its sub-infoTree unless startNode has been specified
	# use rootNode if you are unsure where the node is located
	def addSubNodeObjByValue(self, value_, newNode_, uniqueLevel_=-1, startNode_ = ""):
		thisNode = self
		startNode = startNode_
		
		# Has node search been restricted to a specific endNode?
		if startNode_ == "":
			#N => Assume thisNode sub-infoTree 
			startNode = thisNode

		# Find the reference node
		thisParrentNode=""
		while(thisNode != ""):
			# Is this the node we are looking for?
			# Is thisNode and value a ordered dict object
			if thisNode.isOrderedDict() and thisNode.isOrderedDict(value_):
				#Y => Is this the value we are looking for
				if thisNode.item_ == value_:
					#Y
					thisParrentNode = thisNode
					break

			# Is thisNode and value a list object
			if thisNode.isList() and thisNode.isList(value_):
				#Y => Is this the value we are looking for
				if thisNode.item_ == value_:
					#Y
					thisParrentNode = thisNode
					break					

			# Is thisNode and value a string
			if thisNode.isString() and thisNode.isString(value_):
				#Y => Is this the value we are looking for
				if(thisNode.item_.lower() == value_.lower()):
					#Y
					thisParrentNode = thisNode
					break

			# Is thisNode and value a number
			if thisNode.isNumber() and thisNode.isNumber(value_):
				#Y => Is this the value we are looking for
				if thisNode.item_ == value_:
					#Y
					thisParrentNode = thisNode
					break

			# Get next node
			thisNode = thisNode.getNextNode(startNode)

		# Was the ref. node found?
		if(thisParrentNode == ""):
			# NO
			self.error_ = "addSubNodeObjByName: Unable to find node with name " + name_			   
			return self

		# Auto discover item type and update thisNode uniquenessLevel
		# Is this parrentNode a dict object?
		if thisParrentNode.isOrderedDict():
			#Y => Set uniqunessLevel to peerNode uniqueness since a dict cannot contain duplicate keys
			uniqueLevel_ = 2

		# Has uniquenessLevel been specified?
		if uniqueLevel_ < 0:
			#N => Use/Enherit thisNodes
			uniqueLevel_ = thisNode.uniqueLevel_
		
		# Is node->value unique?
		# Is it infoTree Uniqueness?
		if(uniqueLevel_ == 1):
			# Does this node allready exist?
			thisRootNode = thisNode.getRootNode()
			existingNode = thisRootNode.findNodeByName(newNode_.name_)
			if(existingNode != ""):
				# Node exist just update frequency "match count"
				existingNode.freq_ += 1				   
				return self
		# Is it peerNode Uniqueness?
		if(uniqueLevel_ == 2):
			# Does this node allready exist as a peerNode?
			existingNode = thisNode.findPeerNodeByName(newNode_.name_)
			if(existingNode != ""):
				# Node exist just update frequency "match count"
				existingNode.freq_ += 1
				return self
		# Is it subNode Uniqueness?
		if(uniqueLevel_ == 3):
			# Does this node allready exist as a subNode?
			existingNode = thisNode.findSubNodeByName(newNode_.name_)
			if(existingNode != ""):
				# Node exist just update freq "match count"
				existingNode.freq_ += 1
				return self
		# Is it sub-infoTree Uniqueness
		if(uniqueLevel_ == 4):
			# Does this node allready exist as a subNode?
			existingNode = thisNode.findNodeByName(newNode_.name_)
			if(existingNode != ""):
				# Node exist just update freq "match count"
				existingNode.freq_ += 1
				return self
		
		# Assume the ref. node was found
		# update this parrentNodes subNode structure "sub-infoTree"
		# Does this subNode allready Exist?
		for node in thisParrentNode.subNodes_:
			# Is newNode == to someNode?
			if newNode_.name_ == node.name_:
				#Y => Signal tryed to add existing node
				self.error_ = "addSubNodeObjByName: node " + newNode_.name_ + " allready exist in sub-nodeTree of parrentNode " + thisNode.name_
				# Forced exit node allready exists
				return self

		# Assume the node does not exist
		# Ensure the newSubNode has been associated/linked to thisNodes, has thisNode as parentNode
		newNode_.parrentNode_ = thisNode
		# Ensure the newSubNode has the specified uniqueness level
		newNode_.uniqueLevel_ = uniqueLevel_		   
		
		# Add the new subNode
		thisNode.subNodes_.append(newNode_)

		# Update sub node count
		thisNode.lastSubNodeIx_ += 1
		# Ensure nodeIx is has lastNode ix so it can be fixed 
		newNode_.nodeIx_ = thisNode.lastSubNodeIx_		

		# Fix newPeerNode & its sub-infoTree nodeId's
		newNode_.updateSubinfoTreeNodeIds()

		# Auto discover item type and update this parrentNodes json object structure "sub-infoTree"
		# Is this parrentNode a dict object?
		if thisNode.isOrderedDict():
			#Y => Has this key allready been added?
			if not newNode_.name_ in thisNode.item_.keys():
				#N => Add the new dict item, insert not supported for dicts so we must recreate the sub-infoTree of all nodes after the ref node
				thisNode.item_[newNode_.name_] = newNode_.item_				
				
		# Is this parrentNode a list Object?
		if thisNode.isList():
			#Y
			# Has this item allready been added?
			if thisNode.getNodeByItem(newNode_.name_, newNode_.item_) == "":			
				#N => Add new list item, hence nodeix + 1 => after node at ix
				thisNode.item_.append(newNode_.item_)

		# Update new nodes sub-infoTree to reflect its json object structure
		#newNode_.setValue()				

		return newNode_

	# Add new subNodeObj (by value) to thisNodes peerNode specified by Ix as new last-subNode
	def addSubNodeObjByIx(self, nodeIx_, newNode_, uniqueLevel_=-1):
		thisNode = self
		thisParrentNode = thisNode.parrentNode_
			 
		# Is ix valid?
		if nodeIx_ < 0 or nodeIx_ > thisParrentNode.lastSubNodeIx_:
			#N => Signal failed to add Node
			self.error_ = "addSubNodeObjByIx: Cannot find a peerNode at ix " + str(nodeIx_)
			return self

		# Find the Ref. Node
		thisNode = thisParrentNode.subNodes_[nodeIx_]
		thisParrentNode = thisNode

		# Auto discover item type and update thisNode uniquenessLevel
		# Is this parrentNode a dict object?
		if thisParrentNode.isOrderedDict():
			#Y => Set uniqunessLevel to peerNode uniqueness since a dict cannot contain duplicate keys
			uniqueLevel_ = 2

		# Has uniqueness level been specified?
		if uniqueLevel_ < 0:
			#N => Use/Enherit thisNodes
			uniqueLevel_ = thisNode.uniqueLevel_

		# Is this rootNode?
		if(thisParrentNode == ""):
			# YES => rootNode does not have peerNodes
			self.error_ = "addSubNodeObjByIx: rootNode does have peerNodes!!"
			return self

		# Is node->value unique?
		# Is it infoTree Uniqueness?
		if(uniqueLevel_ == 1):
			# Does this node allready exist?
			thisRootNode = thisNode.getRootNode()
			existingNode = thisRootNode.findNodeByItem(newNode_.name_, newNode_.item_)
			if(existingNode != ""):
				# Node exist just update frequency "match count"
				existingNode.freq_ += 1				   
				return self
		# Is it peerNode Uniqueness?
		if(uniqueLevel_ == 2):
			# Does this node allready exist as a peerNode?
			existingNode = thisNode.findPeerNodeByItem(newNode_.name_, newNode_.item_)
			if(existingNode != ""):
				# Node exist just update frequency "match count"
				existingNode.freq_ += 1
				return self
		# Is it subNode Uniqueness?
		if(uniqueLevel_ == 3):
			# Does this node allready exist as a subNode?
			existingNode = thisNode.findSubNodeByItem(newNode_.name_, newNode_.item_)
			if(existingNode != ""):
				# Node exist just update freq "match count"
				existingNode.freq_ += 1
				return self
		# Is it sub-infoTree Uniqueness
		if(uniqueLevel_ == 4):
			# Does this node allready exist as a subNode?
			existingNode = thisNode.findNodeByItem(newNode_.name_, newNode_.item_)
			if(existingNode != ""):
				# Node exist just update freq "match count"
				existingNode.freq_ += 1
				return self

		# Assume the node does not exist
		# update this parrentNodes subNode structure "sub-infoTree"
		# Does this subNode allready Exist?
		for node in thisParrentNode.subNodes_:
			# Is newNode == to someNode?
			if newNode_.name_ == node.name_:
				#Y => Signal tryed to add existing node
				self.error_ = "addSubNodeObjByIx: node " + newNode_.name_ + " allready exist in sub-nodeTree of parrentNode " + thisParrentNode.name_
				# Forced exit node allready exists
				return self

		# Ensure the newPeerNode has been associated/linked to thisNodes parrentNode
		newNode_.parrentNode_ = thisNode.parrentNode_
		# Ensure the newPeerNode has the specified uniqueness level
		newNode_.uniqueLevel_ = uniqueLevel_

		# Add the new peerNode
		thisParrentNode.subNodes_.append(newNode_)
		
		# Update sub node count
		thisParrentNode.lastSubNodeIx_ += 1
		# Ensure nodeIx has lastNode ix so it can be fixed 
		newNode_.nodeIx_ = thisParrentNode.lastSubNodeIx_

		# Fix newPeerNode & its sub-infoTree nodeId's
		newNode_.updateSubinfoTreeNodeIds()

		# Auto discover item type and update this parrentNodes json object structure "sub-infoTree"
		# Is this parrentNode a dict object?
		if thisParrentNode.isOrderedDict():
			#Y => Has this key allready been added?
			if not newNode_.name_ in thisParrentNode.item_.keys():
				#N => Add the new dict item, insert not supported for dicts so we must recreate the sub-infoTree of all nodes after the ref node
				thisParrentNode.item_[newNode_.name_] = newNode_.item_				
				
		# Is this parrentNode a list Object?
		if thisParrentNode.isList():
			#Y
			# Has this item allready been added?
			if thisParrentNode.getNodeByItem(newNode_.name_, newNode_.item_) == "":			
				#N => Add new list item, hence nodeix + 1 => after node at ix
				thisParrentNode.item_.append(newNode_.item_)

		# Update new nodes sub-infoTree to reflect its json object structure
		#newNode_.setValue()		

		return newNode_

# ------------------- Add Node Helper/Wrapper Methdos ------------------------------
# --------------------	Add Node Helper/Wrapper Methods -----------------
	# Add new Node (by value) on same parrentNode/nodeChain as thisNode, as new last-subNode
	# STATUS: TESTED->OK
	def addNode(self, name_="", item_="", uniqueLevel_=-1):
		thisNode = self

		# Create new node
		newNode = jsonNode(name_, item_, thisNode.parrentNode_, thisNode.nodeLevelSeparator_)

		# Was the new node created?
		if newNode.error_ != "":
			#N => Signal failed to add new subNode
			self.error_ = "addNode: Failed to Create jsonNode: " + newNode.error_
			return self

		# Add the new node as new lastNode 
		thisNode = thisNode.addNodeObj(newNode, uniqueLevel_)

		# Update new nodes sub-infoTree to reflect its json object structure
		thisNode.setValue()		

		return thisNode
	
	# Add new Node (by value) relative to Node Specified by Id as new last-subNode, Search from thisNode and to end of its sub-infoTree unless startNode has been specified
	# use rootNode if you are unsure where the node is located
	def addNodeById(self, nodeId_, name_="", item_="", uniqueLevel_=-1, startNode_ = ""):
		thisNode = self

		# Create new node
		newNode = jsonNode(name_, item_, thisNode.parrentNode_, thisNode.nodeLevelSeparator_)

		# Was the new node created?
		if newNode.error_ != "":
			#N => Signal failed to add new subNode
			self.error_ = "addNodeById: Failed to Create jsonNode: " + newNode.error_
			return self

		# Add the new node as new lastNode on same node as thisNode
		thisNode = thisNode.addNodeObjById(nodeId_, newNode, uniqueLevel_)

		# Update new nodes sub-infoTree to reflect its json object structure
		thisNode.setValue()		

		return thisNode

	# Add new Node (by value) relative to "same parrent as" Node Specified by Name as new last-subNode, Search from thisNode and to end of its sub-infoTree
	# use rootNode if you are unsure where the node is located
	def addNodeByName(self, nodeName_, name_="", item_="", uniqueLevel_=-1, startNode_ = ""):
		thisNode = self

		# Create new node
		newNode = jsonNode(name_, item_, thisNode.parrentNode_, thisNode.nodeLevelSeparator_)
		
		# Was the new node created?
		if newNode.error_ != "":
			#N => Signal failed to add new subNode
			self.error_ = "addNodeByName: Failed to Create jsonNode: " + newNode.error_
			return self		

		# Add the new peerNode as new lastNode on same node as thisNode
		thisNode = thisNode.addNodeObjByName(nodeName_, newNode, uniqueLevel_)

		# Update new nodes sub-infoTree to reflect its json object structure
		thisNode.setValue()		

		return thisNode

	# Add new Node (by value) relative to "same parrent as" Node Specified by Value as new last-subNode, Search from thisNode and to end of its sub-infoTree
	# use rootNode if you are unsure where the node is located
	def addNodeByValue(self, value_, name_="", item_="", uniqueLevel_=-1, startNode_ = ""):
		thisNode = self

		# Create new node
		newNode = jsonNode(name_, item_, thisNode.parrentNode_, thisNode.nodeLevelSeparator_)
		
		# Was the new node created?
		if newNode.error_ != "":
			#N => Signal failed to add new subNode
			self.error_ = "addNodeByValue: Failed to Create jsonNode: " + newNode.error_
			return self		

		# Add the new peerNode as new lastNode on same node as thisNode
		thisNode = thisNode.addNodeObjByValue(value_, newNode, uniqueLevel_, startNode_)

		# Update new nodes sub-infoTree to reflect its json object structure
		thisNode.setValue()		

		return thisNode

	# Add new Node (by value) relative to Node Specified by Id as new last-subNode, Search from thisNode and to end of its sub-infoTree unless startNode has been specified
	# use rootNode if you are unsure where the node is located
	def addNodeByIx(self, nodeIx_, name_="", item_="", uniqueLevel_=-1):
		thisNode = self

		# Create new node
		newNode = jsonNode(name_, item_, thisNode.parrentNode_, thisNode.nodeLevelSeparator_)

		# Was the new node created?
		if newNode.error_ != "":
			#N => Signal failed to add new subNode
			self.error_ = "addNodeByIx: Failed to Create jsonNode: " + newNode.error_
			return self

		# Add the new node as new lastNode on same node as thisNode
		thisNode = thisNode.addNodeObjByIx(nodeIx_, newNode, uniqueLevel_)

		# Update new nodes sub-infoTree to reflect its json object structure
		thisNode.setValue()		

		return thisNode

#------------------------------------------------------
#-------------- Add peerNode Helper/Wrapper Methods --------
	# Add new peerNode (by value) on same parrentNode/nodeChain as thisNode, as new last-peerNode
	# STATUS: TESTED->OK
	def addPeerNode(self, name_="", item_="", uniqueLevel_=-1):
		thisNode = self

		# Create new node
		newNode = jsonNode(name_, item_, thisNode.parrentNode_, thisNode.nodeLevelSeparator_)

		# Was the new node created?
		if newNode.error_ != "":
			#N => Signal failed to add new subNode
			self.error_ = "addPeerNode: Failed to Create jsonNode: " + newNode.error_
			return self

		# Add the new node as new lastNode 
		thisNode = thisNode.addPeerNodeObj(newNode, uniqueLevel_)

		# Update new nodes sub-infoTree to reflect its json object structure
		thisNode.setValue()		

		return thisNode

	# Add new peerNode (by value) relative to "same parrent as" Node Specified by Id as new last-peerNode, Search from thisNode and to end of its sub-infoTree
	# use rootNode if you are unsure where the node is located
	def addPeerNodeById(self, nodeId_, name_="", item_="", uniqueLevel_=-1):
		thisNode = self

		# Create new node
		newNode = jsonNode(name_, item_, thisNode.parrentNode_, thisNode.nodeLevelSeparator_)

		# Was the new node created?
		if newNode.error_ != "":
			#N => Signal failed to add new subNode
			self.error_ = "addPeerNodeById: Failed to Create jsonNode: " + newNode.error_
			return self

		# Add the new node as new lastNode on same node as thisNode
		thisNode = thisNode.addPeerNodeObjById(nodeId_, newNode, uniqueLevel_)

		# Update new nodes sub-infoTree to reflect its json object structure
		thisNode.setValue()		

		return thisNode

	# Add new peerNode (by value) relative to "same parrent as" Node Specified by Name as new last-peerNode, Search from thisNode and to end of its sub-infoTree
	# use rootNode if you are unsure where the node is located
	def addPeerNodeByName(self, nodeName_, name_="", item_="", uniqueLevel_=-1):
		thisNode = self

		# Create new node
		newNode = jsonNode(name_, item_, thisNode.parrentNode_, thisNode.nodeLevelSeparator_)
		
		# Was the new node created?
		if newNode.error_ != "":
			#N => Signal failed to add new subNode
			self.error_ = "addPeerNodeByName: Failed to Create jsonNode: " + newNode.error_
			return self		

		# Add the new peerNode as new lastNode on same node as thisNode
		thisNode = thisNode.addPeerNodeObjByName(nodeName_, newNode, uniqueLevel_)

		# Update new nodes sub-infoTree to reflect its json object structure
		thisNode.setValue()		

		return thisNode

	# Add new peerNode (by value) relative to "same parrent as" Node Specified by Value as new last-peerNode, Search from thisNode and to end of its sub-infoTree
	# use rootNode if you are unsure where the node is located
	def addPeerNodeByValue(self, value_, name_="", item_="", uniqueLevel_=-1):
		thisNode = self

		# Create new node
		newNode = jsonNode(name_, item_, thisNode.parrentNode_, thisNode.nodeLevelSeparator_)
		
		# Was the new node created?
		if newNode.error_ != "":
			#N => Signal failed to add new subNode
			self.error_ = "addPeerNodeByValue: Failed to Create jsonNode: " + newNode.error_
			return self		

		# Add the new peerNode as new lastNode on same node as thisNode
		thisNode = thisNode.addPeerNodeObjByValue(value_, newNode, uniqueLevel_)

		# Update new nodes sub-infoTree to reflect its json object structure
		thisNode.setValue()		

		return thisNode

	# Add copy of new peerNode (by object) on same parrentNode/nodeChain as thisNode as new lastNode
	def addPeerNodeObjCopy(self, newNode_, uniqueLevel_=-1):
		thisNode = self

		# Create new node as copy of otherNode
		newNode = newNode_.copyNodeObj()

		# Was the new node created?
		if newNode == "":
			#N => Signal failed to create copy of peerNode
			self.error_ = "addPeerNodeObjCopy: Failed to Copy jsonNode: " + newNode_.error_
			return self		

		# Add the new node as new lastNode
		thisNode = thisNode.addPeerNodeObj(newNode, uniqueLevel_)

		# Update new nodes sub-infoTree to reflect its json object structure
		thisNode.setValue()		

		return thisNode

#-------- Add subNode Helper/Wrapper Methods ------------
	# Add new subNode (by value) to thisNode as new last-subNode
	# STATUS: TESTED->OK
	def addSubNode(self, name_="", item_="", uniqueLevel_=0):
		thisNode = self
		
		# Create new node
		newNode = jsonNode(name_, item_, thisNode, thisNode.nodeLevelSeparator_)

		# Was the node created?
		if newNode.error_ != "":
			#N => Signal failed to add new subNode
			self.error_ = "addSubNode: Failed to Create jsonNode: " + newNode.error_
			return self

		# Add the new subNode to thisNode
		thisNode = thisNode.addSubNodeObj(newNode, uniqueLevel_)

		# Update new nodes sub-infoTree to reflect its json object structure
		thisNode.setValue()		

		return thisNode	   

	# Add new subNode (by value) to Node Specified by Id as new last-subNode, Search from thisNode and to end of its sub-infoTree unless startNode has been specified
	# use rootNode if you are unsure where the node is located
	def addSubNodeById(self, nodeId_, name_="", item_="", uniqueLevel_=-1, startNode_ = ""):
		thisNode = self

		# Create new node
		newNode = jsonNode(name_, item_, thisNode, thisNode.nodeLevelSeparator_)

		# Was the new node created?
		if newNode.error_ != "":
			#N => Signal failed to add new subNode
			self.error_ = "addPeerNodeById: Failed to Create jsonNode: " + newNode.error_
			return self

		# Add the new node as new lastNode on same node as thisNode
		thisNode = thisNode.addSubNodeObjById(nodeId_, newNode, uniqueLevel_)

		# Update new nodes sub-infoTree to reflect its json object structure
		thisNode.setValue()		

		return thisNode

	# Add new subNode (by value) to Node Specified by Name as new last-subNode, Search from thisNode and to end of its sub-infoTree unless startNode has been specified
	# use rootNode if you are unsure where the node is located
	def addSubNodeByName(self, nodeName_, name_="", item_="", uniqueLevel_=-1, startNode_ = ""):
		thisNode = self

		# Create new node
		newNode = jsonNode(name_, item_, thisNode, thisNode.nodeLevelSeparator_)
		
		# Was the new node created?
		if newNode.error_ != "":
			#N => Signal failed to add new subNode
			self.error_ = "addSubNodeByName: Failed to Create jsonNode: " + newNode.error_
			return self		

		# Add the new peerNode as new lastNode on same node as thisNode
		thisNode = thisNode.addSubNodeObjByName(nodeName_, newNode, uniqueLevel_)

		# Update new nodes sub-infoTree to reflect its json object structure
		thisNode.setValue()		

		return thisNode

	# Add new subNode (by value) to Node Specified by Value as new last-subNode, Search from thisNode and to end of its sub-infoTree unless startNode has been specified
	# use rootNode if you are unsure where the node is located
	def addSubNodeByValue(self, value_, name_="", item_="", uniqueLevel_=-1, startNode_ = ""):
		thisNode = self

		# Create new node
		newNode = jsonNode(name_, item_, thisNode, thisNode.nodeLevelSeparator_)
		
		# Was the new node created?
		if newNode.error_ != "":
			#N => Signal failed to add new subNode
			self.error_ = "addSubNodeByValue: Failed to Create jsonNode: " + newNode.error_
			return self		

		# Add the new peerNode as new lastNode on same node as thisNode
		thisNode = thisNode.addSubNodeObjByValue(value_, newNode, uniqueLevel_, startNode_)

		# Update new nodes sub-infoTree to reflect its json object structure
		thisNode.setValue()		

		return thisNode

	# Add new subNode (by value) to thisNodes peerNode specified by Ix as new last-subNode
	# use rootNode if you are unsure where the node is located
	def addSubNodeByIx(self, nodeIx_, name_="", item_="", uniqueLevel_=-1):
		thisNode = self

		# Create new node
		newNode = jsonNode(name_, item_, thisNode, thisNode.nodeLevelSeparator_)

		# Was the new node created?
		if newNode.error_ != "":
			#N => Signal failed to add new subNode
			self.error_ = "addSubNodeByIx: Failed to Create jsonNode: " + newNode.error_
			return self

		# Add the new node as new lastNode on same node as thisNode
		thisNode = thisNode.addSubNodeObjByIx(nodeIx_, newNode, uniqueLevel_)

		# Update new nodes sub-infoTree to reflect its json object structure
		thisNode.setValue()		

		return thisNode

	# Add copy of new subNodeObj (by object) to thisNode as new last-subNode
	def addSubNodeObjCopy(self, newNode_, uniqueLevel_=-1):
		thisNode = self
	
		# Create copy of otherNode
		newNode = newNode_.copyNodeObj()

		# Was the new node created?
		if newNode == "":
			#N => Signal failed to create copy of subNode
			self.error_ = "addSubNodeObjCopy: Failed to Copy jsonNode: " + newNode_.error_
			return self		

		# Add the new subNode to thisNode
		thisNode = thisNode.addSubNodeObj(newNode, uniqueLevel_)

		# Update new nodes sub-infoTree to reflect its json object structure
		thisNode.setValue()		

		return thisNode

#----------------------
# ------------------------- INSERT node Handling (Search from thisNode to end of its sub-infoTree) -----
	# Insert new nodeObj on same parrentNode/nodeChain as thisNode & relative to "after" thisNode
	def insertNodeObj(self, newNode_, uniqueLevel_=-1):
		thisNode = self
		thisParrentNode = thisNode.parrentNode_

		# Is this rootNode?
		if(thisParrentNode == ""):
			# YES => rootNode does not have peerNodes
			self.error_ = "insertNodeObj: rootNode does have peerNodes!!"
			return self		

		# Auto discover item type and update thisNode uniquenessLevel
		# Is this parrentNode a dict object?
		if thisParrentNode.isOrderedDict():
			#Y => Set uniqunessLevel to peerNode uniqueness since a dict cannot contain duplicate keys
			uniqueLevel_ = 2

		# Has uniquenessLevel been specified?
		if uniqueLevel_ < 0 :
			#N => Use/Enherit thisNodes
			uniqueLevel_ = thisNode.uniqueLevel_

		# Is this nodeIx last-subNode?
		if thisNode.nodeIx_ == thisParrentNode.lastSubNodeIx_:
			#Y => Signal attempt to insert peerNode at invalid ix
			self.error_ = "insertNodeObj: Cannot insert a peerNode after last-peerNode, use addPeerNode for this action"
			return self						

		# Is node->value unique?
		# Is it infoTree Uniqueness?
		if(uniqueLevel_ == 1):
			# Does this node allready exist?
			thisRootNode = thisNode.getRootNode()
			existingNode = thisRootNode.findNodeByItem(newNode_.name_, newNode_.item_)
			if(existingNode != ""):
				# Node exist just update frequency "match count"
				existingNode.freq_ += 1				   
				return self
		# Is it peerNode Uniqueness?
		if(uniqueLevel_ == 2):
			# Does this node allready exist as a peerNode?
			existingNode = thisNode.findPeerNodeByItem(newNode_.name_, newNode_.item_)
			if(existingNode != ""):
				# Node exist just update frequency "match count"
				existingNode.freq_ += 1
				return self
		# Is it subNode Uniqueness?
		if(uniqueLevel_ == 3):
			# Does this node allready exist as a subNode?
			existingNode = thisNode.findSubNodeByItem(newNode_.name_, newNode_.item_)
			if(existingNode != ""):
				# Node exist just update freq "match count"
				existingNode.freq_ += 1
				return self
		# Is it sub-infoTree Uniqueness
		if(uniqueLevel_ == 4):
			# Does this node allready exist as a subNode?
			existingNode = thisNode.findNodeByItem(newNode_.name_, newNode_.item_)
			if(existingNode != ""):
				# Node exist just update freq "match count"
				existingNode.freq_ += 1
				return self

		# Assume the node does not exist
		# update this parrentNodes subNode structure "sub-infoTree"
		# Does this subNode allready Exist?
		for node in thisParrentNode.subNodes_:
			# Is newNode == to someNode?
			if newNode_.name_ == node.name_:
				#Y => Signal tryed to add existing node
				self.error_ = "insertNodeObj: node " + newNode_.name_ + " allready exist in sub-nodeTree of parrentNode " + thisParrentNode.name_
				# Forced exit node allready exists
				return self		

		# Ensure the newPeerNode has been associated/linked to thisNodes parrentNode
		newNode_.parrentNode_ = thisParrentNode
		# Ensure the newPeerNode has the specified uniqueness level
		newNode_.uniqueLevel_ = uniqueLevel_		 
		
		# Insert the new peerNode before node at ix, hence nodeix + 1 => after node at ix
		thisParrentNode.subNodes_.insert(thisNode.nodeIx_ + 1, newNode_)

		# Update sub node count
		thisParrentNode.lastSubNodeIx_ += 1
		# Ensure nodeIx is thisNode + 1 
		newNode_.nodeIx_ = thisNode.nodeIx_ + 1

		# Fix newPeerNode & its sub-infoTree nodeId's
		newNode_.updateSubinfoTreeNodeIds()

		# Auto discover item type and update this parrentNodes json object structure "sub-infoTree"
		# Is this parrentNode a dict object?
		if thisParrentNode.isOrderedDict():
			#Y => Has this key allready been added?
			if not newNode_.name_ in thisParrentNode.item_.keys():
				#Y => Insert the new dict item, insert not supported for dicts so we must recreate the sub-infoTree of all nodes after the ref node
				# nodeix + 1 => after node at ix
				thisParrentNode.insertDictItemByIx(thisNode.nodeIx_ + 1, newNode_.name_, newNode_.item_)

		# Is this parrentNode a list Object?
		if thisParrentNode.isList():
			#Y
			# Has this item allready been added?
			if thisParrentNode.getNodeByItem(newNode_.name_, newNode_.item_) == "":			
				#N => Insert new list item, hence nodeix + 1 => after node at ix
				thisParrentNode.item_.insert(thisNode.nodeIx_ + 1, newNode_.item_)

		# Update new nodes sub-infoTree to reflect its json object structure
		#newNode_.setValue()					

		return newNode_

	# Insert new nodeObj (by value) relative to "after" Node Specified by Id, Search from thisNode and to end of its sub-infoTree unless startNode has been specified
	# use rootNode if you are unsure where the node is located
	def insertNodeObjById(self, nodeId_, newNode_, uniqueLevel_=-1, startNode_ = ""):
		thisNode = self
		startNode = startNode_
		
		# Has node search been restricted to a specific endNode?
		if startNode_ == "":
			#N => Assume thisNode sub-infoTree 
			startNode = thisNode

		# Find the reference node
		thisParrentNode=""
		while(thisNode != ""):
			# Is this the node we are looking for?
			if(thisNode.nodeId_.lower() == nodeId_.lower()):
				thisParrentNode = thisNode.parrentNode_
				break

			# Get next node
			thisNode = thisNode.getNextNode(startNode)

		# Was the ref. node found?
		if(thisParrentNode == ""):
			# NO
			self.error_ = "insertNodeObjById: Unable to find node with Id" + nodeId_			
			return self

		# Is this nodeIx last-subNode?
		if thisNode.nodeIx_ == thisParrentNode.lastSubNodeIx_:
			#Y => Signal attempt to insert peerNode at invalid ix
			self.error_ = "insertNodeObjById: Cannot insert a peerNode after last-peerNode, use addPeerNode for this action"
			return self					
		
		# Auto discover item type and update thisNode uniquenessLevel
		# Is this parrentNode a dict object?
		if thisParrentNode.isOrderedDict():
			#Y => Set uniqunessLevel to peerNode uniqueness since a dict cannot contain duplicate keys
			uniqueLevel_ = 2			

		# Has a uniqunenessLevel been specified?
		if uniqueLevel_ < 0:
			#N => Use/Enherit thisNodes
			uniqueLevel_ = thisNode.uniqueLevel_

		# Is node->value unique?
		# Is it infoTree Uniqueness?
		if(uniqueLevel_ == 1):
			# Does this node allready exist?
			thisRootNode = thisNode.getRootNode()
			existingNode = thisRootNode.findNodeByItem(newNode_.name_, newNode_.item_)
			if(existingNode != ""):
				# Node exist just update frequency "match count"
				existingNode.freq_ += 1				   
				return self
		# Is it peerNode Uniqueness?
		if(uniqueLevel_ == 2):
			# Does this node allready exist as a peerNode?
			existingNode = thisNode.findPeerNodeByItem(newNode_.name_, newNode_.item_)
			if(existingNode != ""):
				# Node exist just update frequency "match count"
				existingNode.freq_ += 1
				return self
		# Is it subNode Uniqueness?
		if(uniqueLevel_ == 3):
			# Does this node allready exist as a subNode?
			existingNode = thisNode.findSubNodeByItem(newNode_.name_, newNode_.item_)
			if(existingNode != ""):
				# Node exist just update freq "match count"
				existingNode.freq_ += 1
				return self
		# Is it sub-infoTree Uniqueness
		if(uniqueLevel_ == 4):
			# Does this node allready exist as a subNode?
			existingNode = thisNode.findNodeByItem(newNode_.name_, newNode_.item_)
			if(existingNode != ""):
				# Node exist just update freq "match count"
				existingNode.freq_ += 1
				return self
		
		# Assume the ref. node was found
		# update this parrentNodes subNode structure "sub-infoTree"
		# Does this subNode allready Exist?
		for node in thisParrentNode.subNodes_:
			# Is newNode == to someNode?
			if newNode_.name_ == node.name_:
				#Y => Signal tryed to add existing node
				self.error_ = "insertNodeObjById: node " + newNode_.name_ + " allready exist in sub-nodeTree of parrentNode " + thisParrentNode.name_
				# Forced exit node allready exists
				return self

		# Assume the node does not exist		
		# Ensure the newPeerNode has been associated/linked to thisNodes parrentNode
		newNode_.parrentNode_ = thisParrentNode
		# Ensure the newPeerNode has the specified uniqueness level
		newNode_.uniqueLevel_ = uniqueLevel_		
		
		# Insert the new peerNode before node at ix, hence nodeix + 1 => after node at ix
		thisParrentNode.subNodes_.insert(thisNode.nodeIx_ + 1, newNode_)

		# Update sub node count
		thisParrentNode.lastSubNodeIx_ += 1
		# Ensure nodeIx is has peerNode ix so it can be fixed 
		newNode_.nodeIx_ = thisNode.nodeIx_ + 1

		# Fix newPeerNode & its sub-infoTree nodeId's
		newNode_.updateSubinfoTreeNodeIds()

		# Auto discover item type and update this parrentNodes json object structure "sub-infoTree"
		# Is this parrentNode a dict object?
		if thisParrentNode.isOrderedDict():
			#Y => Has this key allready been added?
			if not newNode_.name_ in thisParrentNode.item_.keys():
				#N => Insert the new dict item, insert not supported for dicts so we must recreate the sub-infoTree of all nodes after the ref node
				# nodeIx + 1 => after node at ix
				thisParrentNode.insertDictItemByIx(thisNode.nodeIx_ + 1, newNode_.name_, newNode_.item_)

		# Is this parrentNode a list Object?
		if thisParrentNode.isList():
			#Y
			# Has this item allready been added?
			if thisParrentNode.getNodeByItem(newNode_.name_, newNode_.item_) == "":			
				#N => Insert new list item, hence nodeix + 1 => after node at ix
				thisParrentNode.item_.insert(thisNode.nodeIx_ + 1, newNode_.item_)

		# Update new nodes sub-infoTree to reflect its json object structure
		#newNode_.setValue()					

		return newNode_	   

	# Insert new nodeObj (by value) relative to "After" Node Specified by name, Search from thisNode and to end of its sub-infoTree
	# use rootNode if you are unsure where the node is located
	def insertNodeObjByName(self, name_, newNode_, uniqueLevel_=-1, startNode_ = ""):
		thisNode = self
		startNode = startNode_

		# Find the reference node
		thisParrentNode=""
		while(thisNode != ""):
			# Is this the node we are looking for?
			if(thisNode.name_.lower() == name_.lower()):
				thisParrentNode = thisNode.parrentNode_
				break

			# Get next node
			thisNode = thisNode.getNextNode(startNode)

		# Was the ref. node found?
		if(thisParrentNode == ""):
			# NO
			self.error_ = "insertNodeObjByName: Unable to find node with name " + name_			   
			return self

		# Is this nodeIx last-subNode?
		if thisNode.nodeIx_ == thisParrentNode.lastSubNodeIx_:
			#Y => Signal attempt to insert peerNode at invalid ix
			self.error_ = "insertNodeObjByName: Cannot insert a peerNode after last-peerNode, use addPeerNode for this action"
			return self			

		# Auto discover item type and update thisNode uniquenessLevel
		# Is this parrentNode a dict object?
		if thisParrentNode.isOrderedDict():
			#Y => Set uniqunessLevel to peerNode uniqueness since a dict cannot contain duplicate keys
			uniqueLevel_ = 2			

		# Has a uniqunessLevel been specified?
		if uniqueLevel_ < 0:
			#N => Use/Enherit thisNodes
			uniqueLevel_ = thisNode.uniqueLevel_

		# Is node->value unique?
		# Is it infoTree Uniqueness?
		if(uniqueLevel_ == 1):
			# Does this node allready exist?
			thisRootNode = thisNode.getRootNode()
			existingNode = thisRootNode.findNodeByName(newNode_.name_)
			if(existingNode != ""):
				# Node exist just update frequency "match count"
				existingNode.freq_ += 1				   
				return self
		# Is it peerNode Uniqueness?
		if(uniqueLevel_ == 2):
			# Does this node allready exist as a peerNode?
			existingNode = thisNode.findPeerNodeByName(newNode_.name_)
			if(existingNode != ""):
				# Node exist just update frequency "match count"
				existingNode.freq_ += 1
				return self
		# Is it subNode Uniqueness?
		if(uniqueLevel_ == 3):
			# Does this node allready exist as a subNode?
			existingNode = thisNode.findSubNodeByName(newNode_.name_)
			if(existingNode != ""):
				# Node exist just update freq "match count"
				existingNode.freq_ += 1
				return self
		# Is it sub-infoTree Uniqueness
		if(uniqueLevel_ == 4):
			# Does this node allready exist as a subNode?
			existingNode = thisNode.findNodeByName(newNode_.name_)
			if(existingNode != ""):
				# Node exist just update freq "match count"
				existingNode.freq_ += 1
				return self
		
		# Assume the ref. node was found
		# update this parrentNodes subNode structure "sub-infoTree"
		# Does this subNode allready Exist?
		for node in thisParrentNode.subNodes_:
			# Is newNode == to someNode?
			if newNode_.name_ == node.name_:
				#Y => Signal tryed to add existing node
				self.error_ = "insertNodeObjByName: node " + newNode_.name_ + " allready exist in sub-nodeTree of parrentNode " + thisParrentNode.name_
				# Forced exit node allready exists
				return self

		# Assume the node does not exist
		# Ensure the newPeerNode has been associated/linked to thisNodes parrentNode
		newNode_.parrentNode_ = thisParrentNode
		# Ensure the newPeerNode has the specified uniqueness level
		newNode_.uniqueLevel_ = uniqueLevel_		 
		
		# Insert the new peerNode before node at ix, hence nodeix + 1 => after node at ix
		thisParrentNode.subNodes_.insert(thisNode.nodeIx_ + 1, newNode_)

		# Update sub node count
		thisParrentNode.lastSubNodeIx_ += 1
		# Ensure nodeIx is peerNode ix so it can be fixed 
		newNode_.nodeIx_ = thisNode.nodeIx_ + 1		   

		# Fix newPeerNode & its sub-infoTree nodeId's
		newNode_.updateSubinfoTreeNodeIds()

		# Auto discover item type and update this parrentNodes json object structure "sub-infoTree"
		# Is this parrentNode a dict object?
		if thisParrentNode.isOrderedDict():
			#Y => Has this key allready been added?
			if not newNode_.name_ in thisParrentNode.item_.keys():
				#N => Insert the new dict item, insert not supported for dicts so we must recreate the sub-infoTree of all nodes after the ref node
				thisParrentNode.insertDictItemByIx(thisNode.nodeIx_ + 1, newNode_.name_, newNode_.item_)

		# Is this parrentNode a list Object?
		if thisParrentNode.isList():
			#Y
			# Has this item allready been added?
			if thisParrentNode.getNodeByItem(newNode_.name_, newNode_.item_) == "":			
				#N => Insert new list item, hence nodeix + 1 => after node at ix
				thisParrentNode.item_.insert(thisNode.nodeIx_ + 1, newNode_.item_)

		# Update new nodes sub-infoTree to reflect its json object structure
		#newNode_.setValue()					

		return newNode_

	# Insert new nodeObj (by value) on same parrentNode/nodeChain as thisNode & relative to "after" nodeIx
	# use rootNode if you are unsure where the node is located
	def insertNodeObjByIx(self, nodeIx_, newNode_, uniqueLevel_=-1):
		thisNode = self

		# Get the referece Node
		thisParrentNode = thisNode.parrentNode_

		# is thisNode rootnode?
		if thisParrentNode == "":
			#Y => Signal attempt to insert peer on a root node
			self.error_ = "insertNodeObjByIx: rootNode does not have peer nodes"
			return self

		# Is this nodeIx_ valid?
		if nodeIx_ < 0 or nodeIx_ > thisParrentNode.lastSubNodeIx_:
			#N => Signal attempt to insert peern node at invalid ix
			self.error_ = "insertNodeObjByIx: last subNode Ix of parrenNode " + thisParrentNode.name_ + " is "+ thisParrentNode.lastSubNodeIx_ + ", hence nodeIx " + str(nodeIx_) + " is not a valid ix"
			return self

		# Is this nodeIx last-subNode?
		if nodeIx_ == thisParrentNode.lastSubNodeIx_:
			#Y => Signal attempt to insert peerNode at invalid ix
			self.error_ = "insertNodeObjByIx: Cannot insert a peerNode after last-peerNode, use addPeerNode for this action"
			return self

		# Assume specified ix is valid
		thisNode = thisParrentNode.subNodes_[nodeIx_]
		thisParrentNode = thisNode.parrentNode_

		# Auto discover item type and update thisNode uniquenessLevel
		# Is this parrentNode a dict object?
		if thisParrentNode.isOrderedDict():
			#Y => Set uniqunessLevel to peerNode uniqueness since a dict cannot contain duplicate keys
			uniqueLevel_ = 2			

		# Has uniquenessLevel been specified?
		if uniqueLevel_ < 0:
			#N => Use/Enheri thisNodes
			uniqueLevel_ = thisNode.uniqueLevel_

		# Is node->value unique?
		# Is it infoTree Uniqueness?
		if(uniqueLevel_ == 1):
			# Does this node allready exist?
			thisRootNode = thisNode.getRootNode()
			existingNode = thisRootNode.findNodeByItem(newNode_.name_, newNode_.item_)
			if(existingNode != ""):
				# Node exist just update frequency "match count"
				existingNode.freq_ += 1				   
				return self
		# Is it peerNode Uniqueness?
		if(uniqueLevel_ == 2):
			# Does this node allready exist as a peerNode?
			existingNode = thisNode.findPeerNodeByItem(newNode_.name_, newNode_.item_)
			if(existingNode != ""):
				# Node exist just update frequency "match count"
				existingNode.freq_ += 1
				return self
		# Is it subNode Uniqueness?
		if(uniqueLevel_ == 3):
			# Does this node allready exist as a subNode?
			existingNode = thisNode.findSubNodeByItem(newNode_.name_, newNode_.item_)
			if(existingNode != ""):
				# Node exist just update freq "match count"
				existingNode.freq_ += 1
				return self
		# Is it sub-infoTree Uniqueness
		if(uniqueLevel_ == 4):
			# Does this node allready exist as a subNode?
			existingNode = thisNode.findNodeByItem(newNode_.name_, newNode_.item_)
			if(existingNode != ""):
				# Node exist just update freq "match count"
				existingNode.freq_ += 1
				return self
		
		# Assume the ref. node was found
		# update this parrentNodes subNode structure "sub-infoTree"
		# Does this subNode allready Exist?
		for node in thisParrentNode.subNodes_:
			# Is newNode == to someNode?
			if newNode_.name_ == node.name_:
				#Y => Signal tryed to add existing node
				self.error_ = "insertNodeObjByIx: node " + newNode_.name_ + " allready exist in sub-nodeTree of parrentNode " + thisParrentNode.name_
				# Forced exit node allready exists
				return self

		# Assume the node does not exist
		# Ensure the newPeerNode has been associated/linked to thisNodes parrentNode
		newNode_.parrentNode_ = thisParrentNode
		# Ensure the newPeerNode has the specified uniqueness level
		newNode_.uniqueLevel_ = uniqueLevel_		 
		
		# Insert the new peerNode before node at ix, hence nodeix + 1 => after node at ix
		thisParrentNode.subNodes_.insert(nodeIx_ + 1, newNode_)

		# Update sub node count
		thisParrentNode.lastSubNodeIx_ += 1
		# Ensure nodeIx has insertedNode ix so it can be fixed 
		newNode_.nodeIx_ = thisNode.nodeIx_ + 1		   

		# Fix newPeerNode & its sub-infoTree nodeId's
		newNode_.updateSubinfoTreeNodeIds()

		# Auto discover item type and update this parrentNodes json object structure "sub-infoTree"
		# Is this parrentNode a dict object?
		if thisParrentNode.isOrderedDict():
			#Y => Has this key allready been added?
			if not newNode_.name_ in thisParrentNode.item_.keys():
				#N => Insert the new dict item, insert not supported for dicts so we must recreate the sub-infoTree of all nodes after the ref node
				# nodeIx + 1 => after node at ix
				thisParrentNode.insertDictItemByIx(nodeIx_ + 1, newNode_.name_, newNode_.item_)

		# Is this parrentNode a list Object?
		if thisParrentNode.isList():
			#Y
			# Has this item allready been added?
			if thisParrentNode.getNodeByItem(newNode_.name_, newNode_.item_) == "":			
				#N => Insert new list item, hence nodeix + 1 => after node at ix
				thisParrentNode.item_.insert(nodeIx_ + 1, newNode_.item_)

		# Update new nodes sub-infoTree to reflect its json object structure
		#newNode_.setValue()					

		return newNode_

	# Insert new nodeObj (by value) relative to "After" Node Specified by value, Search from thisNode and to end of its sub-infoTree
	# use rootNode if you are unsure where the node is located
	def insertNodeObjByValue(self, value_, newNode_, uniqueLevel_=-1, startNode_ = ""):
		thisNode = self
		startNode = startNode_

		# Find the reference node
		thisParrentNode=""
		while(thisNode != ""):
			# Is this the node we are looking for?
			# Is thisNode and value a ordered dict object
			if thisNode.isOrderedDict() and thisNode.isOrderedDict(value_):
				#Y => Is this the value we are looking for
				if thisNode.item_ == value_:
					#Y
					thisParrentNode = thisNode.parrentNode_
					break

			# Is thisNode and value a list object
			if thisNode.isList() and thisNode.isList(value_):
				#Y => Is this the value we are looking for
				if thisNode.item_ == value_:
					#Y
					thisParrentNode = thisNode.parrentNode_
					break					

			# Is thisNode and value a string
			if thisNode.isString() and thisNode.isString(value_):
				#Y => Is this the value we are looking for
				if(thisNode.item_.lower() == value_.lower()):
					#Y
					thisParrentNode = thisNode.parrentNode_
					break

			# Is thisNode and value a number
			if thisNode.isNumber() and thisNode.isNumber(value_):
				#Y => Is this the value we are looking for
				if thisNode.item_ == value_:
					#Y
					thisParrentNode = thisNode.parrentNode_
					break

			# Get next node
			thisNode = thisNode.getNextNode(startNode)

		# Was the ref. node found?
		if(thisParrentNode == ""):
			# NO
			self.error_ = "insertNodeObjByValue: Unable to find node with value " + sefl.getString(value_)			   
			return self

		# Is this nodeIx last-subNode?
		if thisNode.nodeIx_ == thisParrentNode.lastSubNodeIx_:
			#Y => Signal attempt to insert peerNode at invalid ix
			self.error_ = "insertNodeObjByValue: Cannot insert a peerNode after last-peerNode, use addPeerNode for this action"
			return self			

		# Auto discover item type and update thisNode uniquenessLevel
		# Is this parrentNode a dict object?
		if thisParrentNode.isOrderedDict():
			#Y => Set uniqunessLevel to peerNode uniqueness since a dict cannot contain duplicate keys
			uniqueLevel_ = 2			

		# Has a uniqunessLevel been specified?
		if uniqueLevel_ < 0:
			#N => Use/Enherit thisNodes
			uniqueLevel_ = thisNode.uniqueLevel_

		# Is node->value unique?
		# Is it infoTree Uniqueness?
		if(uniqueLevel_ == 1):
			# Does this node allready exist?
			thisRootNode = thisNode.getRootNode()
			existingNode = thisRootNode.findNodeByName(newNode_.name_)
			if(existingNode != ""):
				# Node exist just update frequency "match count"
				existingNode.freq_ += 1				   
				return self
		# Is it peerNode Uniqueness?
		if(uniqueLevel_ == 2):
			# Does this node allready exist as a peerNode?
			existingNode = thisNode.findPeerNodeByName(newNode_.name_)
			if(existingNode != ""):
				# Node exist just update frequency "match count"
				existingNode.freq_ += 1
				return self
		# Is it subNode Uniqueness?
		if(uniqueLevel_ == 3):
			# Does this node allready exist as a subNode?
			existingNode = thisNode.findSubNodeByName(newNode_.name_)
			if(existingNode != ""):
				# Node exist just update freq "match count"
				existingNode.freq_ += 1
				return self
		# Is it sub-infoTree Uniqueness
		if(uniqueLevel_ == 4):
			# Does this node allready exist as a subNode?
			existingNode = thisNode.findNodeByName(newNode_.name_)
			if(existingNode != ""):
				# Node exist just update freq "match count"
				existingNode.freq_ += 1
				return self
		
		# Assume the ref. node was found
		# update this parrentNodes subNode structure "sub-infoTree"
		# Does this subNode allready Exist?
		for node in thisParrentNode.subNodes_:
			# Is newNode == to someNode?
			if newNode_.name_ == node.name_:
				#Y => Signal tryed to add existing node
				self.error_ = "insertNodeObjByValue: node " + newNode_.name_ + " allready exist in sub-nodeTree of parrentNode " + thisParrentNode.name_
				# Forced exit node allready exists
				return self

		# Assume the node does not exist
		# Ensure the newPeerNode has been associated/linked to thisNodes parrentNode
		newNode_.parrentNode_ = thisParrentNode
		# Ensure the newPeerNode has the specified uniqueness level
		newNode_.uniqueLevel_ = uniqueLevel_		 
		
		# Insert the new peerNode before node at ix, hence nodeix + 1 => after node at ix
		thisParrentNode.subNodes_.insert(thisNode.nodeIx_ + 1, newNode_)

		# Update sub node count
		thisParrentNode.lastSubNodeIx_ += 1
		# Ensure nodeIx is peerNode ix so it can be fixed 
		newNode_.nodeIx_ = thisNode.nodeIx_ + 1		   

		# Fix newPeerNode & its sub-infoTree nodeId's
		newNode_.updateSubinfoTreeNodeIds()

		# Auto discover item type and update this parrentNodes json object structure "sub-infoTree"
		# Is this parrentNode a dict object?
		if thisParrentNode.isOrderedDict():
			#Y => Has this key allready been added?
			if not newNode_.name_ in thisParrentNode.item_.keys():
				#N => Insert the new dict item, insert not supported for dicts so we must recreate the sub-infoTree of all nodes after the ref node
				thisParrentNode.insertDictItemByIx(thisNode.nodeIx_ + 1, newNode_.name_, newNode_.item_)

		# Is this parrentNode a list Object?
		if thisParrentNode.isList():
			#Y
			# Has this item allready been added?
			if thisParrentNode.getNodeByItem(newNode_.name_, newNode_.item_) == "":			
				#N => Insert new list item, hence nodeix + 1 => after node at ix
				thisParrentNode.item_.insert(thisNode.nodeIx_ + 1, newNode_.item_)

		# Update new nodes sub-infoTree to reflect its json object structure
		#newNode_.setValue()					

		return newNode_

#------------------------ INSERT peerNode Handling (Search in thisNodes peerNodes) ---------------------
	# Insert new peerNodeObj on same parrentNode/nodeChain as thisNode & relative to "after" thisNode
	def insertPeerNodeObj(self, newNode_, uniqueLevel_=-1):
		# Get thisNodes parrentNode
		thisNode = self
		thisParrentNode = thisNode.parrentNode_
		
		# Is this rootNode?
		if thisParrentNode == "":
			#Y => Signal fail
			self.error_ = "insertPeerNodeObj: rootNodes does not have peerNodes"
			return self

		# Auto discover item type and update thisNode uniquenessLevel
		# Is this parrentNode a dict object?
		if thisParrentNode.isOrderedDict():
			#Y => Set uniqunessLevel to peerNode uniqueness since a dict cannot contain duplicate keys
			uniqueLevel_ = 2

		# Has uniquenessLevel been specified?
		if uniqueLevel_ < 0 :
			#N => Use/Enherit thisNodes
			uniqueLevel_ = thisNode.uniqueLevel_

		# Is this nodeIx last-subNode?
		if thisNode.nodeIx_ == thisParrentNode.lastSubNodeIx_:
			#Y => Signal attempt to insert peerNode at invalid ix
			self.error_ = "insertPeerNodeObj: Cannot insert a peerNode after last-peerNode, use addPeerNode for this action"
			return self						

		# Is node->value unique?
		# Is it infoTree Uniqueness?
		if(uniqueLevel_ == 1):
			# Does this node allready exist?
			thisRootNode = thisNode.getRootNode()
			existingNode = thisRootNode.findNodeByItem(newNode_.name_, newNode_.item_)
			if(existingNode != ""):
				# Node exist just update frequency "match count"
				existingNode.freq_ += 1				   
				return self
		# Is it peerNode Uniqueness?
		if(uniqueLevel_ == 2):
			# Does this node allready exist as a peerNode?
			existingNode = thisNode.findPeerNodeByItem(newNode_.name_, newNode_.item_)
			if(existingNode != ""):
				# Node exist just update frequency "match count"
				existingNode.freq_ += 1
				return self
		# Is it subNode Uniqueness?
		if(uniqueLevel_ == 3):
			# Does this node allready exist as a subNode?
			existingNode = thisNode.findSubNodeByItem(newNode_.name_, newNode_.item_)
			if(existingNode != ""):
				# Node exist just update freq "match count"
				existingNode.freq_ += 1
				return self
		# Is it sub-infoTree Uniqueness
		if(uniqueLevel_ == 4):
			# Does this node allready exist as a subNode?
			existingNode = thisNode.findNodeByItem(newNode_.name_, newNode_.item_)
			if(existingNode != ""):
				# Node exist just update freq "match count"
				existingNode.freq_ += 1
				return self

		# Assume the node does not exist
		# update this parrentNodes subNode structure "sub-infoTree"
		# Does this subNode allready Exist?
		for node in thisParrentNode.subNodes_:
			# Is newNode == to someNode?
			if newNode_.name_ == node.name_:
				#Y => Signal tryed to add existing node
				self.error_ = "insertPeerNodeObj: node " + newNode_.name_ + " allready exist in sub-nodeTree of parrentNode " + thisParrentNode.name_
				# Forced exit node allready exists
				return self		

		# Ensure the newPeerNode has been associated/linked to thisNodes parrentNode
		newNode_.parrentNode_ = thisParrentNode
		# Ensure the newPeerNode has the specified uniqueness level
		newNode_.uniqueLevel_ = uniqueLevel_		 
		
		# Insert the new peerNode before node at ix, hence nodeix + 1 => after node at ix
		thisParrentNode.subNodes_.insert(thisNode.nodeIx_ + 1, newNode_)

		# Update sub node count
		thisParrentNode.lastSubNodeIx_ += 1
		# Ensure nodeIx is thisNode + 1 
		newNode_.nodeIx_ = thisNode.nodeIx_ + 1

		# Fix newPeerNode & its sub-infoTree nodeId's
		newNode_.updateSubinfoTreeNodeIds()

		# Auto discover item type and update this parrentNodes json object structure "sub-infoTree"
		# Is this parrentNode a dict object?
		if thisParrentNode.isOrderedDict():
			#Y => Has this key allready been added?
			if not newNode_.name_ in thisParrentNode.item_.keys():
				#Y => Insert the new dict item, insert not supported for dicts so we must recreate the sub-infoTree of all nodes after the ref node
				# nodeIx + 1 => after node at ix
				thisParrentNode.insertDictItemByIx(thisNode.nodeIx_ + 1, newNode_.name_, newNode_.item_)

		# Is this parrentNode a list Object?
		if thisParrentNode.isList():
			#Y
			# Has this item allready been added?
			if thisParrentNode.getNodeByItem(newNode_.name_, newNode_.item_) == "":			
				#N => Insert new list item, hence nodeix + 1 => after node at ix
				thisParrentNode.item_.insert(thisNode.nodeIx_ + 1, newNode_.item_)

		# Update new nodes sub-infoTree to reflect its json object structure
		#newNode_.setValue()					

		return newNode_

	# Insert new peerNodeObj (by value) relative to "after" Node Specified by Id, Search in thisNode peerNodes
	# use rootNode if you are unsure where the node is located
	def insertPeerNodeObjById(self, nodeId_, newNode_, uniqueLevel_=-1):
		thisNode = self
		thisParrentNode = thisNode.parrentNode_

		# Is this rootNode?
		if thisParrentNode == "":
			#Y => Signal fail
			self.error_ = "insertPeerNodeObjById: rootNodes does not have peerNodes"
			return self

		# Find the reference node
		thisParrentNode=""
		for node in thisNode.parrentNode_.subNodes_:
			# Is this the node we are looking for?
			if(node.nodeId_.lower() == nodeId_.lower()):
				thisParrentNode = node.parrentNode_
				thisNode = node
				break

		# Was the ref. node found?
		if(thisParrentNode == ""):
			# NO
			self.error_ = "insertPeerNodeObjById: Unable to find node with Id " + nodeId_			
			return self

		# Is this nodeIx last-subNode?
		if thisNode.nodeIx_ == thisParrentNode.lastSubNodeIx_:
			#Y => Signal attempt to insert peerNode at invalid ix
			self.error_ = "insertPeerNodeObjById: Cannot insert a peerNode after last-peerNode, use addPeerNode for this action"
			return self					
		
		# Auto discover item type and update thisNode uniquenessLevel
		# Is this parrentNode a dict object?
		if thisParrentNode.isOrderedDict():
			#Y => Set uniqunessLevel to peerNode uniqueness since a dict cannot contain duplicate keys
			uniqueLevel_ = 2			

		# Has a uniqunenessLevel been specified?
		if uniqueLevel_ < 0:
			#N => Use/Enherit thisNodes
			uniqueLevel_ = thisNode.uniqueLevel_

		# Is node->value unique?
		# Is it infoTree Uniqueness?
		if(uniqueLevel_ == 1):
			# Does this node allready exist?
			thisRootNode = thisNode.getRootNode()
			existingNode = thisRootNode.findNodeByItem(newNode_.name_, newNode_.item_)
			if(existingNode != ""):
				# Node exist just update frequency "match count"
				existingNode.freq_ += 1				   
				return self
		# Is it peerNode Uniqueness?
		if(uniqueLevel_ == 2):
			# Does this node allready exist as a peerNode?
			existingNode = thisNode.findPeerNodeByItem(newNode_.name_, newNode_.item_)
			if(existingNode != ""):
				# Node exist just update frequency "match count"
				existingNode.freq_ += 1
				return self
		# Is it subNode Uniqueness?
		if(uniqueLevel_ == 3):
			# Does this node allready exist as a subNode?
			existingNode = thisNode.findSubNodeByItem(newNode_.name_, newNode_.item_)
			if(existingNode != ""):
				# Node exist just update freq "match count"
				existingNode.freq_ += 1
				return self
		# Is it sub-infoTree Uniqueness
		if(uniqueLevel_ == 4):
			# Does this node allready exist as a subNode?
			existingNode = thisNode.findNodeByItem(newNode_.name_, newNode_.item_)
			if(existingNode != ""):
				# Node exist just update freq "match count"
				existingNode.freq_ += 1
				return self
		
		# Assume the ref. node was found
		# update this parrentNodes subNode structure "sub-infoTree"
		# Does this subNode allready Exist?
		for node in thisParrentNode.subNodes_:
			# Is newNode == to someNode?
			if newNode_.name_ == node.name_:
				#Y => Signal tryed to add existing node
				self.error_ = "insertPeerNodeObjById: node " + newNode_.name_ + " allready exist in sub-nodeTree of parrentNode " + thisParrentNode.name_
				# Forced exit node allready exists
				return self

		# Assume the node does not exist		
		# Ensure the newPeerNode has been associated/linked to thisNodes parrentNode
		newNode_.parrentNode_ = thisParrentNode
		# Ensure the newPeerNode has the specified uniqueness level
		newNode_.uniqueLevel_ = uniqueLevel_		
		
		# Insert the new peerNode before node at ix, hence nodeix + 1 => after node at ix
		thisParrentNode.subNodes_.insert(thisNode.nodeIx_ + 1, newNode_)

		# Update sub node count
		thisParrentNode.lastSubNodeIx_ += 1
		# Ensure nodeIx is has peerNode ix so it can be fixed 
		newNode_.nodeIx_ = thisNode.nodeIx_ + 1

		# Fix newPeerNode & its sub-infoTree nodeId's
		newNode_.updateSubinfoTreeNodeIds()

		# Auto discover item type and update this parrentNodes json object structure "sub-infoTree"
		# Is this parrentNode a dict object?
		if thisParrentNode.isOrderedDict():
			#Y => Has this key allready been added?
			if not newNode_.name_ in thisParrentNode.item_.keys():
				#N => Insert the new dict item, insert not supported for dicts so we must recreate the sub-infoTree of all nodes after the ref node
				# nodeIx + 1 => after node at ix
				thisParrentNode.insertDictItemByIx(thisNode.nodeIx_ + 1, newNode_.name_, newNode_.item_)

		# Is this parrentNode a list Object?
		if thisParrentNode.isList():
			#Y
			# Has this item allready been added?
			if thisParrentNode.getNodeByItem(newNode_.name_, newNode_.item_) == "":			
				#N => Insert new list item, hence nodeix + 1 => after node at ix
				thisParrentNode.item_.insert(thisNode.nodeIx_ + 1, newNode_.item_)

		# Update new nodes sub-infoTree to reflect its json object structure
		#newNode_.setValue()					

		return newNode_	   

	# Insert new peerNodeObj (by value) relative to "After" Node Specified by name, Search in thisNodes peerNodes
	# use rootNode if you are unsure where the node is located
	def insertPeerNodeObjByName(self, name_, newNode_, uniqueLevel_=-1):
		thisNode = self
		thisParrentNode = thisNode.parrentNode_

		# Is this rootNode?
		if thisParrentNode == "":
			#Y => Signal fail
			self.error_ = "insertPeerNodeObjByName: rootNodes does not have peerNodes"
			return self		

		# Find the reference node
		thisParrentNode=""
		for node in thisNode.parrentNode_.subNodes_:
			# Is this the node we are looking for?
			if(node.name_.lower() == name_.lower()):
				thisParrentNode = node.parrentNode_
				thisNode = node
				break

		# Was the ref. node found?
		if(thisParrentNode == ""):
			# NO
			self.error_ = "insertPeerNodeObjByName: Unable to find node with name " + name_			   
			return self

		# Is this nodeIx last-subNode?
		if thisNode.nodeIx_ == thisParrentNode.lastSubNodeIx_:
			#Y => Signal attempt to insert peerNode at invalid ix
			self.error_ = "insertPeerNodeObjByName: Cannot insert a peerNode after last-peerNode, use addPeerNode for this action"
			return self			

		# Auto discover item type and update thisNode uniquenessLevel
		# Is this parrentNode a dict object?
		if thisParrentNode.isOrderedDict():
			#Y => Set uniqunessLevel to peerNode uniqueness since a dict cannot contain duplicate keys
			uniqueLevel_ = 2			

		# Has a uniqunessLevel been specified?
		if uniqueLevel_ < 0:
			#N => Use/Enherit thisNodes
			uniqueLevel_ = thisNode.uniqueLevel_

		# Is node->value unique?
		# Is it infoTree Uniqueness?
		if(uniqueLevel_ == 1):
			# Does this node allready exist?
			thisRootNode = thisNode.getRootNode()
			existingNode = thisRootNode.findNodeByName(newNode_.name_)
			if(existingNode != ""):
				# Node exist just update frequency "match count"
				existingNode.freq_ += 1				   
				return self
		# Is it peerNode Uniqueness?
		if(uniqueLevel_ == 2):
			# Does this node allready exist as a peerNode?
			existingNode = thisNode.findPeerNodeByName(newNode_.name_)
			if(existingNode != ""):
				# Node exist just update frequency "match count"
				existingNode.freq_ += 1
				return self
		# Is it subNode Uniqueness?
		if(uniqueLevel_ == 3):
			# Does this node allready exist as a subNode?
			existingNode = thisNode.findSubNodeByName(newNode_.name_)
			if(existingNode != ""):
				# Node exist just update freq "match count"
				existingNode.freq_ += 1
				return self
		# Is it sub-infoTree Uniqueness
		if(uniqueLevel_ == 4):
			# Does this node allready exist as a subNode?
			existingNode = thisNode.findNodeByName(newNode_.name_)
			if(existingNode != ""):
				# Node exist just update freq "match count"
				existingNode.freq_ += 1
				return self
		
		# Assume the ref. node was found
		# update this parrentNodes subNode structure "sub-infoTree"
		# Does this subNode allready Exist?
		for node in thisParrentNode.subNodes_:
			# Is newNode == to someNode?
			if newNode_.name_ == node.name_:
				#Y => Signal tryed to add existing node
				self.error_ = "insertPeerNodeObjByName: node " + newNode_.name_ + " allready exist in sub-nodeTree of parrentNode " + thisParrentNode.name_
				# Forced exit node allready exists
				return self

		# Assume the node does not exist
		# Ensure the newPeerNode has been associated/linked to thisNodes parrentNode
		newNode_.parrentNode_ = thisParrentNode
		# Ensure the newPeerNode has the specified uniqueness level
		newNode_.uniqueLevel_ = uniqueLevel_		 
		
		# Insert the new peerNode before node at ix, hence nodeix + 1 => after node at ix
		thisParrentNode.subNodes_.insert(thisNode.nodeIx_ + 1, newNode_)

		# Update sub node count
		thisParrentNode.lastSubNodeIx_ += 1
		# Ensure nodeIx is peerNode ix so it can be fixed 
		newNode_.nodeIx_ = thisNode.nodeIx_ + 1		   

		# Fix newPeerNode & its sub-infoTree nodeId's
		newNode_.updateSubinfoTreeNodeIds()

		# Auto discover item type and update this parrentNodes json object structure "sub-infoTree"
		# Is this parrentNode a dict object?
		if thisParrentNode.isOrderedDict():
			#Y => Has this key allready been added?
			if not newNode_.name_ in thisParrentNode.item_.keys():
				#N => Insert the new dict item, insert not supported for dicts so we must recreate the sub-infoTree of all nodes after the ref node
				thisParrentNode.insertDictItemByIx(thisNode.nodeIx_ + 1, newNode_.name_, newNode_.item_)

		# Is this parrentNode a list Object?
		if thisParrentNode.isList():
			#Y
			# Has this item allready been added?
			if thisParrentNode.getNodeByItem(newNode_.name_, newNode_.item_) == "":			
				#N => Insert new list item, hence nodeix + 1 => after node at ix
				thisParrentNode.item_.insert(thisNode.nodeIx_ + 1, newNode_.item_)

		# Update new nodes sub-infoTree to reflect its json object structure
		#newNode_.setValue()					

		return newNode_

	# Insert new peerNodeObj (by value) on same parrentNode/nodeChain as thisNode & relative to "after" nodeIx, Search in thisNode peerNodes
	# use rootNode if you are unsure where the node is located
	def insertPeerNodeObjByIx(self, nodeIx_, newNode_, uniqueLevel_=-1):
		# Get thisNode parrentNode
		thisNode = self
		thisParrentNode = thisNode.parrentNode_

		# is thisNode rootnode?
		if thisParrentNode == "":
			#Y => Signal attempt to insert peer on a root node
			self.error_ = "insertPeerNodeObjByIx: rootNode does not have peer nodes"
			return self

		# Is this nodeIx_ valid?
		if nodeIx_ < 0 or nodeIx_ > thisParrentNode.lastSubNodeIx_:
			#N => Signal attempt to insert peern node at invalid ix
			self.error_ = "insertPeerNodeObjByIx: last subNode Ix of parrenNode " + thisNode.name_ + " is "+ thisNode.lastSubNodeIx_ + ", hence nodeIx " + str(nodeIx_) + " is not a valid ix"
			return self

		# Is this nodeIx last-subNode?
		if nodeIx_ == thisParrentNode.lastSubNodeIx_:
			#Y => Signal attempt to insert peerNode at invalid ix
			self.error_ = "insertPeerNodeObjByIx: Cannot insert a peerNode after last-peerNode, use addPeerNode for this action"
			return self

		# Assume specified ix is valid
		thisNode = thisParrentNode.subNodes_[nodeIx_]

		# Auto discover item type and update thisNode uniquenessLevel
		# Is this parrentNode a dict object?
		if thisParrentNode.isOrderedDict():
			#Y => Set uniqunessLevel to peerNode uniqueness since a dict cannot contain duplicate keys
			uniqueLevel_ = 2			

		# Has uniquenessLevel been specified?
		if uniqueLevel_ < 0:
			#N => Use/Enheri thisNodes
			uniqueLevel_ = thisNode.uniqueLevel_

		# Is node->value unique?
		# Is it infoTree Uniqueness?
		if(uniqueLevel_ == 1):
			# Does this node allready exist?
			thisRootNode = thisNode.getRootNode()
			existingNode = thisRootNode.findNodeByItem(newNode_.name_, newNode_.item_)
			if(existingNode != ""):
				# Node exist just update frequency "match count"
				existingNode.freq_ += 1				   
				return self
		# Is it peerNode Uniqueness?
		if(uniqueLevel_ == 2):
			# Does this node allready exist as a peerNode?
			existingNode = thisNode.findPeerNodeByItem(newNode_.name_, newNode_.item_)
			if(existingNode != ""):
				# Node exist just update frequency "match count"
				existingNode.freq_ += 1
				return self
		# Is it subNode Uniqueness?
		if(uniqueLevel_ == 3):
			# Does this node allready exist as a subNode?
			existingNode = thisNode.findSubNodeByItem(newNode_.name_, newNode_.item_)
			if(existingNode != ""):
				# Node exist just update freq "match count"
				existingNode.freq_ += 1
				return self
		# Is it sub-infoTree Uniqueness
		if(uniqueLevel_ == 4):
			# Does this node allready exist as a subNode?
			existingNode = thisNode.findNodeByItem(newNode_.name_, newNode_.item_)
			if(existingNode != ""):
				# Node exist just update freq "match count"
				existingNode.freq_ += 1
				return self
		
		# Assume the ref. node was found
		# update this parrentNodes subNode structure "sub-infoTree"
		# Does this subNode allready Exist?
		for node in thisParrentNode.subNodes_:
			# Is newNode == to someNode?
			if newNode_.name_ == node.name_:
				#Y => Signal tryed to add existing node
				self.error_ = "insertPeerNodeObjByIx: node " + newNode_.name_ + " allready exist in sub-nodeTree of parrentNode " + thisParrentNode.name_
				# Forced exit node allready exists
				return self

		# Assume the node does not exist
		# Ensure the newPeerNode has been associated/linked to thisNodes parrentNode
		newNode_.parrentNode_ = thisParrentNode
		# Ensure the newPeerNode has the specified uniqueness level
		newNode_.uniqueLevel_ = uniqueLevel_		 
		
		# Insert the new peerNode before node at ix, hence nodeix + 1 => after node at ix
		thisParrentNode.subNodes_.insert(nodeIx_ + 1, newNode_)

		# Update sub node count
		thisParrentNode.lastSubNodeIx_ += 1
		# Ensure nodeIx has insertedNode ix so it can be fixed 
		newNode_.nodeIx_ = nodeIx_ + 1		   

		# Fix newPeerNode & its sub-infoTree nodeId's
		newNode_.updateSubinfoTreeNodeIds()

		# Auto discover item type and update this parrentNodes json object structure "sub-infoTree"
		# Is this parrentNode a dict object?
		if thisParrentNode.isOrderedDict():
			#Y => Has this key allready been added?
			if not newNode_.name_ in thisParrentNode.item_.keys():
				#N => Insert the new dict item, insert not supported for dicts so we must recreate the sub-infoTree of all nodes after the ref node
				# nodeIx + 1 => after node at ix
				thisParrentNode.insertDictItemByIx(nodeIx_ + 1, newNode_.name_, newNode_.item_)

		# Is this parrentNode a list Object?
		if thisParrentNode.isList():
			#Y
			# Has this item allready been added?
			if thisParrentNode.getNodeByItem(newNode_.name_, newNode_.item_) == "":			
				#N => Insert new list item, hence nodeix + 1 => after node at ix
				thisParrentNode.item_.insert(nodeIx_ + 1, newNode_.item_)

		# Update new nodes sub-infoTree to reflect its json object structure
		#newNode_.setValue()					

		return newNode_

	# Insert new peerNodeObj (by value) relative to "After" Node Specified by value, Search in thisNode peerNodes
	# use rootNode if you are unsure where the node is located
	def insertPeerNodeObjByValue(self, value_, newNode_, uniqueLevel_=-1):
		thisNode = self
		thisParrentNode = thisNode.parrentNode_

		# Is this rootNode?
		if thisParrentNode == "":
			#Y => Signal fail
			self.error_ = "insertPeerNodeObjByValue: rootNodes does not have peerNodes"
			return self

		# Find the reference node
		thisParrentNode=""
		for node in thisNode.parrentNode_.subNodes_:
			# Is this the node we are looking for?
			# Is thisNode and value a ordered dict object
			if node.isOrderedDict() and node.isOrderedDict(value_):
				#Y => Is this the value we are looking for
				if node.item_ == value_:
					#Y
					thisParrentNode = node.parrentNode_
					thisNode = node
					break

			# Is thisNode and value a list object
			if node.isList() and node.isList(value_):
				#Y => Is this the value we are looking for
				if node.item_ == value_:
					#Y
					thisParrentNode = node.parrentNode_
					thisNode = node
					break					

			# Is thisNode and value a string
			if node.isString() and node.isString(value_):
				#Y => Is this the value we are looking for
				if(node.item_.lower() == value_.lower()):
					#Y
					thisParrentNode = node.parrentNode_
					thisNode = node
					break

			# Is thisNode and value a number
			if node.isNumber() and node.isNumber(value_):
				#Y => Is this the value we are looking for
				if node.item_ == value_:
					#Y
					thisParrentNode = node.parrentNode_
					thisNode = node
					break

		# Was the ref. node found?
		if(thisParrentNode == ""):
			# NO
			self.error_ = "insertPeerNodeObjByValue: Unable to find node with value " + self.getString(value_)			   
			return self

		# Is this nodeIx last-subNode?
		if thisNode.nodeIx_ == thisParrentNode.lastSubNodeIx_:
			#Y => Signal attempt to insert peerNode at invalid ix
			self.error_ = "insertPeerNodeObjByValue: Cannot insert a peerNode after last-peerNode, use addPeerNode for this action"
			return self			

		# Auto discover item type and update thisNode uniquenessLevel
		# Is this parrentNode a dict object?
		if thisParrentNode.isOrderedDict():
			#Y => Set uniqunessLevel to peerNode uniqueness since a dict cannot contain duplicate keys
			uniqueLevel_ = 2			

		# Has a uniqunessLevel been specified?
		if uniqueLevel_ < 0:
			#N => Use/Enherit thisNodes
			uniqueLevel_ = thisNode.uniqueLevel_

		# Is node->value unique?
		# Is it infoTree Uniqueness?
		if(uniqueLevel_ == 1):
			# Does this node allready exist?
			thisRootNode = thisNode.getRootNode()
			existingNode = thisRootNode.findNodeByName(newNode_.name_)
			if(existingNode != ""):
				# Node exist just update frequency "match count"
				existingNode.freq_ += 1				   
				return self
		# Is it peerNode Uniqueness?
		if(uniqueLevel_ == 2):
			# Does this node allready exist as a peerNode?
			existingNode = thisNode.findPeerNodeByName(newNode_.name_)
			if(existingNode != ""):
				# Node exist just update frequency "match count"
				existingNode.freq_ += 1
				return self
		# Is it subNode Uniqueness?
		if(uniqueLevel_ == 3):
			# Does this node allready exist as a subNode?
			existingNode = thisNode.findSubNodeByName(newNode_.name_)
			if(existingNode != ""):
				# Node exist just update freq "match count"
				existingNode.freq_ += 1
				return self
		# Is it sub-infoTree Uniqueness
		if(uniqueLevel_ == 4):
			# Does this node allready exist as a subNode?
			existingNode = thisNode.findNodeByName(newNode_.name_)
			if(existingNode != ""):
				# Node exist just update freq "match count"
				existingNode.freq_ += 1
				return self
		
		# Assume the ref. node was found
		# update this parrentNodes subNode structure "sub-infoTree"
		# Does this subNode allready Exist?
		for node in thisParrentNode.subNodes_:
			# Is newNode == to someNode?
			if newNode_.name_ == node.name_:
				#Y => Signal tryed to add existing node
				self.error_ = "insertPeerNodeObjByValue: node " + newNode_.name_ + " allready exist in sub-nodeTree of parrentNode " + thisParrentNode.name_
				# Forced exit node allready exists
				return self

		# Assume the node does not exist
		# Ensure the newPeerNode has been associated/linked to thisNodes parrentNode
		newNode_.parrentNode_ = thisParrentNode
		# Ensure the newPeerNode has the specified uniqueness level
		newNode_.uniqueLevel_ = uniqueLevel_		 
		
		# Insert the new peerNode before node at ix, hence nodeix + 1 => after node at ix
		thisParrentNode.subNodes_.insert(thisNode.nodeIx_ + 1, newNode_)

		# Update sub node count
		thisParrentNode.lastSubNodeIx_ += 1
		# Ensure nodeIx is peerNode ix so it can be fixed 
		newNode_.nodeIx_ = thisNode.nodeIx_ + 1		   

		# Fix newPeerNode & its sub-infoTree nodeId's
		newNode_.updateSubinfoTreeNodeIds()

		# Auto discover item type and update this parrentNodes json object structure "sub-infoTree"
		# Is this parrentNode a dict object?
		if thisParrentNode.isOrderedDict():
			#Y => Has this key allready been added?
			if not newNode_.name_ in thisParrentNode.item_.keys():
				#N => Insert the new dict item, insert not supported for dicts so we must recreate the sub-infoTree of all nodes after the ref node
				thisParrentNode.insertDictItemByIx(thisNode.nodeIx_ + 1, newNode_.name_, newNode_.item_)

		# Is this parrentNode a list Object?
		if thisParrentNode.isList():
			#Y
			# Has this item allready been added?
			if thisParrentNode.getNodeByItem(newNode_.name_, newNode_.item_) == "":			
				#N => Insert new list item, hence nodeix + 1 => after node at ix
				thisParrentNode.item_.insert(thisNode.nodeIx_ + 1, newNode_.item_)

		# Update new nodes sub-infoTree to reflect its json object structure
		#newNode_.setValue()					

		return newNode_

#------------------------ INSERT subNode Handling (Search in thisNodes subNodes) ---------------------
# HER ER JEG I REDESIGN søge område afgrænset til peerNode, subNodes...
# TODO: Ensure that methods only checks wether a given node exists in peerNodes, subNodes... to i dont care about similar nodes found in sub-infoTree, hence just lke json model
	# Insert new subNodeObj on thisNodes & relative to "after" node specified by nodeIx
	def insertSubNodeObj(self, nodeIx_, newNode_, uniqueLevel_=-1):
		thisNode = self
		thisParrentNode = thisNode

		# Is this nodeIx_ valid?
		if nodeIx_ < 0 or nodeIx_ > thisParrentNode.lastSubNodeIx_:
			#N => Signal attempt to insert peern node at invalid ix
			self.error_ = "insertSubNodeObj: last subNode Ix of parrenNode " + thisParrentNode.name_ + " is "+ thisParrentNode.lastSubNodeIx_ + ", hence nodeIx " + str(nodeIx_) + " is not a valid ix"
			return self

		# Assume specified ix is valid
		thisNode = thisParrentNode.subNodes_[nodeIx_]

		# Auto discover item type and update thisNode uniquenessLevel
		# Is this parrentNode a dict object?
		if thisParrentNode.isOrderedDict():
			#Y => Set uniqunessLevel to peerNode uniqueness since a dict cannot contain duplicate keys
			uniqueLevel_ = 2		

		# Has a uniqunessLevel been specified?
		if uniqueLevel_ < 0:
			#N => Use/Enherit thisNodes
			uniqueLevel_ = thisNode.uniqueLevel_
		
		# Is node->value unique?
		# Is it infoTree Uniqueness?
		if(uniqueLevel_ == 1):
			# Does this node allready exist?
			thisRootNode = thisNode.getRootNode()
			existingNode = thisRootNode.findNodeByItem(newNode_.name_, newNode_.item_)
			if(existingNode != ""):
				# Node exist just update frequency "match count"
				existingNode.freq_ += 1				   
				return self
		# Is it peerNode Uniqueness?
		if(uniqueLevel_ == 2):
			# Does this node allready exist as a peerNode?
			existingNode = thisNode.findPeerNodeByItem(newNode_.name_, newNode_.item_)
			if(existingNode != ""):
				# Node exist just update frequency "match count"
				existingNode.freq_ += 1
				return self
		# Is it subNode Uniqueness?
		if(uniqueLevel_ == 3):
			# Does this node allready exist as a subNode?
			existingNode = thisNode.findSubNodeByItem(newNode_.name_, newNode_.item_)
			if(existingNode != ""):
				# Node exist just update freq "match count"
				existingNode.freq_ += 1
				return self
		# Is it sub-infoTree Uniqueness
		if(uniqueLevel_ == 4):
			# Does this node allready exist as a subNode?
			existingNode = thisNode.findNodeByItem(newNode_.name_, newNode_.item_)
			if(existingNode != ""):
				# Node exist just update freq "match count"
				existingNode.freq_ += 1
				return self

		# Assume the ref. node was found
		# update this parrentNodes subNode structure "sub-infoTree"
		# Does this subNode allready Exist?
		for node in thisParrentNode.subNodes_:
			# Is newNode == to someNode?
			if newNode_.name_ == node.name_:
				#Y => Signal tryed to add existing node
				self.error_ = "insertSubNodeObj: node " + newNode_.name_ + " allready exist in sub-nodeTree of parrentNode " + thisParrentNode.name_
				# Forced exit node allready exists
				return self

		# Assume the node does not exist
		# Ensure the newSubNode has been associated/linked to thisNodes, has thisNode as parrentNode
		newNode_.parrentNode_ = thisParrentNode
		# Ensure the newSubNode has the specified uniqueness level
		newNode_.uniqueLevel_ = uniqueLevel_		   
		
		# insert the new subNode, hence nodeix + 1 => after node at ix
		thisParrentNode.subNodes_.insert(nodeIx_ + 1, newNode_)

		# Update sub node count
		thisParrentNode.lastSubNodeIx_ += 1
		# Ensure nodeIx is has lastNode ix so it can be fixed 
		newNode_.nodeIx_ = thisParrentNode.lastSubNodeIx_		

		# Fix newPeerNode & its sub-infoTree nodeId's
		newNode_.updateSubinfoTreeNodeIds()

		# Auto discover item type and update this parrentNodes json object structure "sub-infoTree"
		# Is this parrentNode a dict object?
		if thisParrentNode.isOrderedDict():
			#Y => Has this key allready been added?
			if not newNode_.name_ in thisParrentNode.item_.keys():
				#N => Insert the new dict item, insert not supported for dicts so we must recreate the sub-infoTree of all nodes after the ref node
				# nodeIx + 1 => after node at ix
				thisParrentNode.insertDictItemByIx(nodeIx_ + 1, newNode_.name_, newNode_.item_)

		# Is this parrentNode a list Object?
		if thisParrentNode.isList():
			#Y
			# Has this item allready been added?
			if thisParrentNode.getNodeByItem(newNode_.name_, newNode_.item_) == "":			
				#N => Add new list item, hence nodeix + 1 => after node at ix
				thisParrentNode.item_.insert(nodeIx_ + 1, newNode_.item_)

		# Update new nodes sub-infoTree to reflect its json object structure
		#newNode_.setValue()			

		return newNode_

	# Insert new subNodeObj (by value) on thisNode & relative to "after" node specified nodeId, Search in thisNode subNodes
	# use rootNode if you are unsure where the node is located
	def insertSubNodeObjById(self, nodeId_, newNode_, uniqueLevel_=-1):
		thisNode = self
		thisParrentNode = thisNode
		
		# Find the reference node
		thisParrentNode=""
		for node in thisNode.parrentNode_.subNodes_:
			# Is this the node we are looking for?
			if(node.nodeId_.lower() == nodeId_.lower()):
				thisParrentNode = thisNode
				thisNode = node
				break

		# Was the ref. node found?
		if(thisParrentNode == ""):
			# NO
			self.error_ = "insertSubNodeObjById: Unable to find node with Id " + nodeId_			
			return self

		# Is this nodeIx last-subNode?
		if thisNode.nodeIx_ == thisParrentNode.lastSubNodeIx_:
			#Y => Signal attempt to insert peerNode at invalid ix
			self.error_ = "insertSubNodeObjById: Cannot insert a subNode after last-subNode, use addSubNode for this action"
			return self			

		# Auto discover item type and update thisNode uniquenessLevel
		# Is this parrentNode a dict object?
		if thisParrentNode.isOrderedDict():
			#Y => Set uniqunessLevel to peerNode uniqueness since a dict cannot contain duplicate keys
			uniqueLevel_ = 2			

		# Has uniquenessLevel been specified?
		if uniqueLevel_ < 0:
			#N => Use/Enherit thisNodes
			uniqueLevel_ = thisNode.uniqueLevel_
		
		# Is node->value unique?
		# Is it infoTree Uniqueness?
		if(uniqueLevel_ == 1):
			# Does this node allready exist?
			thisRootNode = thisNode.getRootNode()
			existingNode = thisRootNode.findNodeByItem(newNode_.name_, newNode_.item_)
			if(existingNode != ""):
				# Node exist just update frequency "match count"
				existingNode.freq_ += 1				   
				return self
		# Is it peerNode Uniqueness?
		if(uniqueLevel_ == 2):
			# Does this node allready exist as a peerNode?
			existingNode = thisNode.findPeerNodeByItem(newNode_.name_, newNode_.item_)
			if(existingNode != ""):
				# Node exist just update frequency "match count"
				existingNode.freq_ += 1
				return self
		# Is it subNode Uniqueness?
		if(uniqueLevel_ == 3):
			# Does this node allready exist as a subNode?
			existingNode = thisNode.findSubNodeByItem(newNode_.name_, newNode_.item_)
			if(existingNode != ""):
				# Node exist just update freq "match count"
				existingNode.freq_ += 1
				return self
		# Is it sub-infoTree Uniqueness
		if(uniqueLevel_ == 4):
			# Does this node allready exist as a subNode?
			existingNode = thisNode.findNodeByItem(newNode_.name_, newNode_.item_)
			if(existingNode != ""):
				# Node exist just update freq "match count"
				existingNode.freq_ += 1
				return self
		
		# Assume the ref. node was found
		# update this parrentNodes subNode structure "sub-infoTree"
		# Does this subNode allready Exist?
		for node in thisParrentNode.subNodes_:
			# Is newNode == to someNode?
			if newNode_.name_ == node.name_:
				#Y => Signal tryed to add existing node
				self.error_ = "insertSubNodeObjById: node " + newNode_.name_ + " allready exist in sub-nodeTree of parrentNode " + thisParrentNode.name_
				# Forced exit node allready exists
				return self

		# Assume the node does not exist
		# Ensure the newSubNode has been associated/linked to thisNode, has thisNode as parrentNode
		newNode_.parrentNode_ = thisParrentNode
		# Ensure the newSubNode has the specified uniqueness level
		newNode_.uniqueLevel_ = uniqueLevel_		   
		
		# Insert the new subNode, hence nodeix + 1 => after node at ix
		thisParrentNode.subNodes_.insert(thisNode.nodeIx_ + 1, newNode_)

		# Update sub node count
		thisParrentNode.lastSubNodeIx_ += 1
		# Ensure nodeIx is has lastNode ix so it can be fixed 
		newNode_.nodeIx_ = thisParrentNode.lastSubNodeIx_		

		# Fix newSubNode & its sub-infoTree nodeId's
		newNode_.updateSubinfoTreeNodeIds()

		# Auto discover item type and update this parrentNodes json object structure "sub-infoTree"
		# Is this parrentNode a dict object?
		if thisParrentNode.isOrderedDict():
			#Y => Has this key allready been added?
			if not newNode_.name_ in thisParrentNode.item_.keys():
				#N => Insert the new dict item, insert not supported for dicts so we must recreate the sub-infoTree of all nodes after the ref node
				# nodeIx + 1 => after node at ix
				thisParrentNode.insertDictItemByIx(thisNode.nodeIx_ + 1, newNode_.name_, newNode_.item_)

		# Is this parrentNode a list Object?
		if thisParrentNode.isList():
			#Y
			# Has this item allready been added?
			if thisParrentNode.getNodeByItem(newNode_.name_, newNode_.item_) == "":			
				#N => Insert new list item, hence nodeix + 1 => after node at ix
				thisParrentNode.item_.insert(thisNode.nodeIx_ + 1, newNode_.item_)

		# Update new nodes sub-infoTree to reflect its json object structure
		#newNode_.setValue()					

		return newNode_	  

	# Insert new subNodeObj (by value) on thisNode & relative to "after" node specified by name, Search in thisNodes subNodes
	# use rootNode if you are unsure where the node is located
	def insertSubNodeObjByName(self, name_, newNode_, uniqueLevel_=-1):
		thisNode = self
		thisParrentNode = thisNode
		
		# Find the reference node
		thisParrentNode=""
		for node in thisNode.parrentNode_.subNodes_:
			# Is this the node we are looking for?
			if(node.name_.lower() == name_.lower()):
				thisParrentNode = thisNode
				thisNode = node
				break

		# Was the ref. node found?
		if(thisParrentNode == ""):
			# NO
			self.error_ = "insertSubNodeObjByName: Unable to find node with name " + name_			  
			return self

		# Is this nodeIx last-subNode?
		if thisNode.nodeIx_ == thisParrentNode.lastSubNodeIx_:
			#Y => Signal attempt to insert peerNode at invalid ix
			self.error_ = "insertSubNodeObjByName: Cannot insert a subNode after last-subNode, use addSubNode for this action"
			return self			

		# Auto discover item type and update thisNode uniquenessLevel
		# Is this parrentNode a dict object?
		if thisParrentNode.isOrderedDict():
			#Y => Set uniqunessLevel to peerNode uniqueness since a dict cannot contain duplicate keys
			uniqueLevel_ = 2						

		# Has uniquenessLevel been specified?
		if uniqueLevel_ < 0:
			#N => Use/Enherit thisNodes
			uniqueLevel_ = thisNode.uniqueLevel_
		
		# Is node->value unique?
		# Is it infoTree Uniqueness?
		if(uniqueLevel_ == 1):
			# Does this node allready exist?
			thisRootNode = thisNode.getRootNode()
			existingNode = thisRootNode.findNodeByName(newNode_.name_)
			if(existingNode != ""):
				# Node exist just update frequency "match count"
				existingNode.freq_ += 1				   
				return self
		# Is it peerNode Uniqueness?
		if(uniqueLevel_ == 2):
			# Does this node allready exist as a peerNode?
			existingNode = thisNode.findPeerNodeByName(newNode_.name_)
			if(existingNode != ""):
				# Node exist just update frequency "match count"
				existingNode.freq_ += 1
				return self
		# Is it subNode Uniqueness?
		if(uniqueLevel_ == 3):
			# Does this node allready exist as a subNode?
			existingNode = thisNode.findSubNodeByName(newNode_.name_)
			if(existingNode != ""):
				# Node exist just update freq "match count"
				existingNode.freq_ += 1
				return self
		# Is it sub-infoTree Uniqueness
		if(uniqueLevel_ == 4):
			# Does this node allready exist as a subNode?
			existingNode = thisNode.findNodeByName(newNode_.name_)
			if(existingNode != ""):
				# Node exist just update freq "match count"
				existingNode.freq_ += 1
				return self

		# Assume the ref. node was found
		# update this parrentNodes subNode structure "sub-infoTree"
		# Does this subNode allready Exist?
		for node in thisParrentNode.subNodes_:
			# Is newNode == to someNode?
			if newNode_.name_ == node.name_:
				#Y => Signal tryed to add existing node
				self.error_ = "insertSubNodeObjByName: node " + newNode_.name_ + " allready exist in sub-nodeTree of parrentNode " + thisParrentNode.name_
				# Forced exit node allready exists
				return self

		# Assume the node does not exist
		# Ensure the newSubNode has been associated/linked to thisNodes, has thisNode as parrentNode
		newNode_.parrentNode_ = thisParrentNode
		# Ensure the newSubNode has the specified uniqueness level
		newNode_.uniqueLevel_ = uniqueLevel_	   
		
		# Insert the new subNode, hence nodeix + 1 => after node at ix
		thisParrentNode.subNodes_.insert(thisNode.nodeIx_ + 1, newNode_)

		# Update sub node count
		thisParrentNode.lastSubNodeIx_ += 1
		# Ensure nodeIx is has insertedNode ix so it can be fixed 
		newNode_.nodeIx_ = thisNode.nodeIx_ + 1		

		# Fix newSubNode & its sub-infoTree nodeId's
		newNode_.updateSubinfoTreeNodeIds()

		# Auto discover item type and update this parrentNodes json object structure "sub-infoTree"
		# Is this parrentNode a dict object?
		if thisParrentNode.isOrderedDict():
			#Y => Has this key allready been added?
			if not newNode_.name_ in thisParrentNode.item_.keys():
				#N => Insert the new dict item, insert not supported for dicts so we must recreate the sub-infoTree of all nodes after the ref node
				# hence nodeix + 1 => after node at ix
				thisParrentNode.insertDictItemByIx(thisNode.nodeIx_ + 1, newNode_.name_, newNode_.item_)

		# Is this parrentNode a list Object?
		if thisParrentNode.isList():
			#Y
			# Has this item allready been added?
			if thisParrentNode.getNodeByItem(newNode_.name_, newNode_.item_) == "":			
				#N => Insert new list item, hence nodeix + 1 => after node at ix
				thisParrentNode.item_.insert(thisNode.nodeIx_ + 1, newNode_.item_)

		# Update new nodes sub-infoTree to reflect its json object structure
		#newNode_.setValue()					
		
		return newNode_

	# Insert new subNodeObj (by value) on thisNode & relative to "after" node specified by nodeIx
	# use rootNode if you are unsure where the node is located
	def insertSubNodeObjByIx(self, nodeIx_, newNode_, uniqueLevel_=-1):
		thisNode = self
		thisParrentNode = thisNode

		# Is this nodeIx last-subNode?
		if nodeIx_ == thisParrentNode.lastSubNodeIx_:
			#Y => Signal attempt to insert peerNode at invalid ix
			self.error_ = "insertSubNodeObjByIx: Cannot insert a subNode after last-subNode, use addSubNode for this action"
			return self

		# Is this nodeIx_ valid?
		if nodeIx_ < 0 or nodeIx_ > thisNode.lastSubNodeIx_:
			#N => Signal attempt to insert peern node at invalid ix
			self.error_ = "insertSubNodeObjByIx: last subNode Ix of parrenNode " + thisNode.name_ + " is "+ thisNode.lastSubNodeIx_ + ", hence nodeIx " + str(nodeIx_) + " is not a valid ix"
			return self			

		# Auto discover item type and update thisNode uniquenessLevel
		# Is this parrentNode a dict object?
		if thisParrentNode.isOrderedDict():
			#Y => Set uniqunessLevel to peerNode uniqueness since a dict cannot contain duplicate keys
			uniqueLevel_ = 2						

		# Has uniquenessLevel been specified?
		if uniqueLevel_ < 0:
			#N => Use/Enherit thisNodes
			uniqueLevel_ = thisNode.uniqueLevel_

		# Is node->value unique?
		# Is it infoTree Uniqueness?
		if(uniqueLevel_ == 1):
			# Does this node allready exist?
			thisRootNode = thisNode.getRootNode()
			existingNode = thisRootNode.findNodeByItem(newNode_.name_, newNode_.item_)
			if(existingNode != ""):
				# Node exist just update frequency "match count"
				existingNode.freq_ += 1				   
				return self
		# Is it peerNode Uniqueness?
		if(uniqueLevel_ == 2):
			# Does this node allready exist as a peerNode?
			existingNode = thisNode.findPeerNodeByItem(newNode_.name_, newNode_.item_)
			if(existingNode != ""):
				# Node exist just update frequency "match count"
				existingNode.freq_ += 1
				return self
		# Is it subNode Uniqueness?
		if(uniqueLevel_ == 3):
			# Does this node allready exist as a subNode?
			existingNode = thisNode.findSubNodeByItem(newNode_.name_, newNode_.item_)
			if(existingNode != ""):
				# Node exist just update freq "match count"
				existingNode.freq_ += 1
				return self
		# Is it sub-infoTree Uniqueness
		if(uniqueLevel_ == 4):
			# Does this node allready exist as a subNode?
			existingNode = thisNode.findNodeByItem(newNode_.name_, newNode_.item_)
			if(existingNode != ""):
				# Node exist just update freq "match count"
				existingNode.freq_ += 1
				return self
					 
		# Assume the ref. node was found
		# update this parrentNodes subNode structure "sub-infoTree"
		# Does this subNode allready Exist?
		for node in thisParrentNode.subNodes_:
			# Is newNode == to someNode?
			if newNode_.name_ == node.name_:
				#Y => Signal tryed to add existing node
				self.error_ = "insertSubNodeObjByIx: node " + newNode_.name_ + " allready exist in sub-nodeTree of parrentNode " + thisParrentNode.name_
				# Forced exit node allready exists
				return self

		# Assume the node does not exist
		# Ensure the newSubNode has been associated/linked to thisNodes, has thisNode as parrentNode
		newNode_.parrentNode_ = thisParrentNode
		# Ensure the newSubNode has the specified uniqueness level
		newNode_.uniqueLevel_ = uniqueLevel_			
		
		# Insert the new subNode, hence nodeix + 1 => after node at ix
		thisParrentNode.subNodes_.insert(nodeIx_ + 1, newNode_)

		# Update sub node count
		thisParrentNode.lastSubNodeIx_ += 1
		# Ensure nodeIx is has insertedNode ix so it can be fixed 
		newNode_.nodeIx_ = nodeIx_ + 1		

		# Fix newPeerNode & its sub-infoTree nodeId's
		newNode_.updateSubinfoTreeNodeIds()

		# Auto discover item type and update this parrentNodes json object structure "sub-infoTree"
		# Is this parrentNode a dict object?
		if thisParrentNode.isOrderedDict():
			#Y => Has this key allready been added?
			if not newNode_.name_ in thisParrentNode.item_.keys():
				#N => Insert the new dict item, insert not supported for dicts so we must recreate the sub-infoTree of all nodes after the ref node
				# nodeIx + 1 => after node at ix
				thisParrentNode.insertDictItemByIx(nodeIx_ + 1, newNode_.name_, newNode_.item_)

		# Is this parrentNode a list Object?
		if thisParrentNode.isList():
			#Y
			# Has this item allready been added?
			if thisParrentNode.getNodeByItem(newNode_.name_, newNode_.item_) == "":			
				#N => Insert new list item, hence nodeix + 1 => after node at ix
				thisParrentNode.item_.insert(nodeIx_ + 1, newNode_.item_)

		# Update new nodes sub-infoTree to reflect its json object structure
		#newNode_.setValue()					

		return newNode_		  

	# Insert new subNodeObj (by value) on thisNode & relative to "after" node specified by value, Search in thisNodes subNodes
	# use rootNode if you are unsure where the node is located
	def insertSubNodeObjByValue(self, value_, newNode_, uniqueLevel_=-1):
		thisNode = self
		thisParrentNode = thisNode
		
		# Find the reference node
		thisParrentNode=""
		for node in thisNode.parrentNode_.subNodes_:
			# Is this the node we are looking for?
			# Is thisNode and value a ordered dict object
			if node.isOrderedDict() and node.isOrderedDict(value_):
				#Y => Is this the value we are looking for
				if node.item_ == value_:
					#Y
					thisParrentNode = node.parrentNode_
					thisNode = node
					break

			# Is thisNode and value a list object
			if node.isList() and node.isList(value_):
				#Y => Is this the value we are looking for
				if node.item_ == value_:
					#Y
					thisParrentNode = node.parrentNode_
					thisNode = node
					break					

			# Is thisNode and value a string
			if node.isString() and node.isString(value_):
				#Y => Is this the value we are looking for
				if(node.item_.lower() == value_.lower()):
					#Y
					thisParrentNode = node.parrentNode_
					thisNode = node
					break

			# Is thisNode and value a number
			if node.isNumber() and node.isNumber(value_):
				#Y => Is this the value we are looking for
				if node.item_ == value_:
					#Y
					thisParrentNode = node.parrentNode_
					thisNode = node
					break

		# Was the ref. node found?
		if(thisParrentNode == ""):
			# NO
			self.error_ = "insertSubNodeObjByValue: Unable to find node with value " + self.getString(value_)			  
			return self

		# Is this nodeIx last-subNode?
		if thisNode.nodeIx_ == thisParrentNode.lastSubNodeIx_:
			#Y => Signal attempt to insert peerNode at invalid ix
			self.error_ = "insertSubNodeObjByValue: Cannot insert a subNode after last-subNode, use addSubNode for this action"
			return self						

		# Auto discover item type and update thisNode uniquenessLevel
		# Is this parrentNode a dict object?
		if thisParrentNode.isOrderedDict():
			#Y => Set uniqunessLevel to peerNode uniqueness since a dict cannot contain duplicate keys
			uniqueLevel_ = 2						

		# Has uniquenessLevel been specified?
		if uniqueLevel_ < 0:
			#N => Use/Enherit thisNodes
			uniqueLevel_ = thisNode.uniqueLevel_
		
		# Is node->value unique?
		# Is it infoTree Uniqueness?
		if(uniqueLevel_ == 1):
			# Does this node allready exist?
			thisRootNode = thisNode.getRootNode()
			existingNode = thisRootNode.findNodeByName(newNode_.name_)
			if(existingNode != ""):
				# Node exist just update frequency "match count"
				existingNode.freq_ += 1				   
				return self
		# Is it peerNode Uniqueness?
		if(uniqueLevel_ == 2):
			# Does this node allready exist as a peerNode?
			existingNode = thisNode.findPeerNodeByName(newNode_.name_)
			if(existingNode != ""):
				# Node exist just update frequency "match count"
				existingNode.freq_ += 1
				return self
		# Is it subNode Uniqueness?
		if(uniqueLevel_ == 3):
			# Does this node allready exist as a subNode?
			existingNode = thisNode.findSubNodeByName(newNode_.name_)
			if(existingNode != ""):
				# Node exist just update freq "match count"
				existingNode.freq_ += 1
				return self
		# Is it sub-infoTree Uniqueness
		if(uniqueLevel_ == 4):
			# Does this node allready exist as a subNode?
			existingNode = thisNode.findNodeByName(newNode_.name_)
			if(existingNode != ""):
				# Node exist just update freq "match count"
				existingNode.freq_ += 1
				return self

		# Assume the ref. node was found
		# update this parrentNodes subNode structure "sub-infoTree"
		# Does this subNode allready Exist?
		for node in thisParrentNode.subNodes_:
			# Is newNode == to someNode?
			if newNode_.name_ == node.name_:
				#Y => Signal tryed to add existing node
				self.error_ = "insertSubNodeObjByValue: node " + newNode_.name_ + " allready exist in sub-nodeTree of parrentNode " + thisParrentNode.name_
				# Forced exit node allready exists
				return self

		# Assume the node does not exist
		# Ensure the newSubNode has been associated/linked to thisNodes, has thisNode as parrentNode
		newNode_.parrentNode_ = thisParrentNode
		# Ensure the newSubNode has the specified uniqueness level
		newNode_.uniqueLevel_ = uniqueLevel_	   
		
		# Insert the new subNode, hence nodeix + 1 => after node at ix
		thisParrentNode.subNodes_.insert(thisNode.nodeIx_ + 1, newNode_)

		# Update sub node count
		thisParrentNode.lastSubNodeIx_ += 1
		# Ensure nodeIx is has insertedNode ix so it can be fixed 
		newNode_.nodeIx_ = thisNode.nodeIx_ + 1		

		# Fix newSubNode & its sub-infoTree nodeId's
		newNode_.updateSubinfoTreeNodeIds()

		# Auto discover item type and update this parrentNodes json object structure "sub-infoTree"
		# Is this parrentNode a dict object?
		if thisParrentNode.isOrderedDict():
			#Y => Has this key allready been added?
			if not newNode_.name_ in thisParrentNode.item_.keys():
				#N => Insert the new dict item, insert not supported for dicts so we must recreate the sub-infoTree of all nodes after the ref node
				# hence nodeix + 1 => after node at ix
				thisParrentNode.insertDictItemByIx(thisNode.nodeIx_ + 1, newNode_.name_, newNode_.item_)

		# Is this parrentNode a list Object?
		if thisParrentNode.isList():
			#Y
			# Has this item allready been added?
			if thisParrentNode.getNodeByItem(newNode_.name_, newNode_.item_) == "":			
				#N => Insert new list item, hence nodeix + 1 => after node at ix
				thisParrentNode.item_.insert(thisNode.nodeIx_ + 1, newNode_.item_)

		# Update new nodes sub-infoTree to reflect its json object structure
		#newNode_.setValue()					
		
		return newNode_

#--------------------------		  

#----------- Insert Helper/Wrapper Methods -----------------------------
#----------- Insert Node Helper/Wrapper methods (Search from thisNode to end of sub-infoTree)-----------------
# Build to search entire sub-infoTree of thisNode
	# Insert new node on same parrentNode/nodeChain as thisNode & relative to "after" thisNode
	# STATUS: TESTED->OK
	def insertNode(self, name_="", item_="", uniqueLevel_=-1):
		thisNode = self

		# Create new node
		newNode = jsonNode(name_, item_, thisNode.parrentNode_, thisNode.nodeLevelSeparator_)

		# Was the new node created?
		if newNode.error_ != "":
			#N => Signal failed to add new subNode
			self.error_ = "insertNode: Failed to Create jsonNode: " + newNode.error_
			return self

		# Insert the new node as after thisNode 
		thisNode = thisNode.insertNodeObj(newNode, uniqueLevel_)

		# Update new nodes sub-infoTree to reflect its json object structure
		thisNode.setValue()		

		return thisNode
	
	# Insert new node (by value) relative to "after" Node Specified by Id, Search from thisNode and to end of its sub-infoTree unless startNode has been specified
	# use rootNode if you are unsure where the node is located
	def insertNodeById(self, nodeId_, name_="", item_="", uniqueLevel_=-1, startNode_ = ""):
		thisNode = self

		# Create new node
		newNode = jsonNode(name_, item_, thisNode.parrentNode_, thisNode.nodeLevelSeparator_)

		# Was the new node created?
		if newNode.error_ != "":
			#N => Signal failed to add new subNode
			self.error_ = "insertNodeById: Failed to Create jsonNode: " + newNode.error_
			return self

		# Insert the new node after node specified by id
		thisNode = thisNode.insertNodeObjById(nodeId_, newNode, uniqueLevel_, startNode_)

		# Update new nodes sub-infoTree to reflect its json object structure
		thisNode.setValue()		

		return thisNode

	# Insert new node (by value) relative to "After" Node Specified by name, Search from thisNode and to end of its sub-infoTree
	# use rootNode if you are unsure where the node is located
	def insertNodeByName(self, nodeName_, name_="", item_="", uniqueLevel_=-1, startNode_ = ""):
		thisNode = self

		# Create new node
		newNode = jsonNode(name_, item_, thisNode.parrentNode_, thisNode.nodeLevelSeparator_)
		
		# Was the new node created?
		if newNode.error_ != "":
			#N => Signal failed to add new subNode
			self.error_ = "insertNodeByName: Failed to Create jsonNode: " + newNode.error_
			return self		

		# Insert the new node after node specified by name
		thisNode = thisNode.insertNodeObjByName(nodeName_, newNode, uniqueLevel_, startNode_)

		# Update new nodes sub-infoTree to reflect its json object structure
		thisNode.setValue()		

		return thisNode

	# Insert new node (by value) on same parrentNode/nodeChain as thisNode & relative to "after" nodeIx
	# use rootNode if you are unsure where the node is located
	def insertNodeByIx(self, nodeIx_, name_="", item_="", uniqueLevel_=-1):
		thisNode = self

		# Create new node
		newNode = jsonNode(name_, item_, thisNode.parrentNode_, thisNode.nodeLevelSeparator_)

		# Was the new node created?
		if newNode.error_ != "":
			#N => Signal failed to add new subNode
			self.error_ = "insertNodeByIx: Failed to Create jsonNode: " + newNode.error_
			return self

		# Insert the new node after node specified by ix
		thisNode = thisNode.insertNodeObjByIx(nodeIx_, newNode, uniqueLevel_)

		# Update new nodes sub-infoTree to reflect its json object structure
		thisNode.setValue()		

		return thisNode

	# Insert new node (by value) relative to "After" Node Specified by value, Search from thisNode and to end of its sub-infoTree
	# use rootNode if you are unsure where the node is located
	def insertNodeByValue(self, value_, name_="", item_="", uniqueLevel_=-1, startNode_ = ""):
		thisNode = self

		# Create new node
		newNode = jsonNode(name_, item_, thisNode.parrentNode_, thisNode.nodeLevelSeparator_)
		
		# Was the new node created?
		if newNode.error_ != "":
			#N => Signal failed to add new subNode
			self.error_ = "insertNodeByValue: Failed to Create jsonNode: " + newNode.error_
			return self		

		# Insert the new node after node specified by value
		thisNode = thisNode.insertNodeObjByValue(value_, newNode, uniqueLevel_, startNode_)

		# Update new nodes sub-infoTree to reflect its json object structure
		thisNode.setValue()		

		return thisNode

# -------------- Insert peerNode Helper/Wrapper methods (Search in thisNodes peerNodes) ----------------
# Build to search only peerNodes, parrentNode->subNodes/nodeChain

	# Insert new peerNode (by value) on same parrentNode/nodeChain as thisNode & relative to "after" thisNode
	def insertPeerNode(self, name_="", item_="", uniqueLevel_=-1):
		thisNode = self

		# Create new node
		newNode = jsonNode(name_, item_, thisNode.parrentNode_, thisNode.nodeLevelSeparator_)

		# Was the node created?
		if newNode.error_ != "":
			#N => Signal failed to add new subNode
			self.error_ = "insertPeerNode: Failed to Create jsonNode: " + newNode.error_
			return self		

		# Insert the new node rel to thisNode
		thisNode = thisNode.insertPeerNodeObj(newNode, uniqueLevel_)

		# Update new nodes sub-infoTree to reflect its json object structure
		thisNode.setValue()		

		return thisNode

	# Insert new peerNode (by value) relative to "after" Node Specified by Id, Search in thisNode peerNodes
	# use rootNode if you are unsure where the node is located
	def insertPeerNodeById(self, nodeId_, name_="", item_="", uniqueLevel_=-1):
		thisNode = self

		# Create new node
		newNode = jsonNode(name_, item_, thisNode.parrentNode_, thisNode.nodeLevelSeparator_)

		# Was the node created?
		if newNode.error_ != "":
			#N => Signal failed to add new subNode
			self.error_ = "insertPeerNodeById: Failed to Create jsonNode: " + newNode.error_
			return self		

		# Insert the new peerNode rel to thisNode
		thisNode = thisNode.insertPeerNodeObjById(nodeId_, newNode, uniqueLevel_)

		# Update new nodes sub-infoTree to reflect its json object structure
		thisNode.setValue()		

		return thisNode

	# Insert new peerNode (by value) relative to "After" Node Specified by name, Search in thisNodes peerNodes
	# use rootNode if you are unsure where the node is located
	def insertPeerNodeByName(self, nodeName_, name_="", item_="", uniqueLevel_=-1):
		thisNode = self

		# Create new node
		newNode = jsonNode(name_, item_, thisNode.parrentNode_, thisNode.nodeLevelSeparator_)

		# Was the node created?
		if newNode.error_ != "":
			#N => Signal failed to add new subNode
			self.error_ = "insertPeerNodeByName: Failed to Create jsonNode: " + newNode.error_
			return self		

		# Insert the new node rel to node specified by name
		thisNode = thisNode.insertPeerNodeObjByName(nodeName_, newNode, uniqueLevel_)

		# Update new nodes sub-infoTree to reflect its json object structure
		thisNode.setValue()		

		return thisNode

	# Insert new peerNode (by value) on same parrentNode/nodeChain as thisNode & relative to "after" nodeIx, Search in thisNode peerNodes
	# use rootNode if you are unsure where the node is located
	def insertPeerNodeByIx(self, nodeIx_, name_="", item_="", uniqueLevel_=-1):
		thisNode = self

		# Create new node
		newNode = jsonNode(name_, item_, thisNode.parrentNode_, thisNode.nodeLevelSeparator_)

		# Was the node created?
		if newNode.error_ != "":
			#N => Signal failed to add new subNode
			self.error_ = "insertPeerNodeByIx: Failed to Create jsonNode: " + newNode.error_
			return self		

		# Insert the new peerNode rel to thisNode
		thisNode = thisNode.insertPeerNodeObjByIx(nodeIx_, newNode, uniqueLevel_)

		# Update new nodes sub-infoTree to reflect its json object structure
		thisNode.setValue()		

		return thisNode		   

	# Insert new peerNode (by value) on same parrentNode/nodeChain as thisNode & relative to "After" Node Specified by value, Search in thisNode peerNodes
	# use rootNode if you are unsure where the node is located
	def insertPeerNodeByValue(self, value_, name_="", item_="", uniqueLevel_=-1):
		thisNode = self

		# Create new node
		newNode = jsonNode(name_, item_, thisNode.parrentNode_, thisNode.nodeLevelSeparator_)

		# Was the node created?
		if newNode.error_ != "":
			#N => Signal failed to add new subNode
			self.error_ = "insertPeerNodeByValue: Failed to Create jsonNode: " + newNode.error_
			return self		

		# Insert the new node rel. after node specified by value
		thisNode = thisNode.insertPeerNodeObjByValue(value_, newNode, uniqueLevel_)

		# Update new nodes sub-infoTree to reflect its json object structure
		thisNode.setValue()		

		return thisNode

	# Insert copy of new peerNode (by object) on same parrentNode/nodeChain as thisNode & relative to "after" thisNode
	def insertPeerNodeObjCopy(self, newNode_, uniqueLevel_=-1):
		thisNode = self

		# Create new node as copy of otherNode
		newNode = newNode_.copyNodeObj()

		# Was the node created?
		if newNode == "":
			#N => Signal failed to copy peerNode
			self.error_ = "insertPeerNodeObjCopy: Failed to Copy jsonNode: " + newNode_.error_
			return self		

		# Insert the new node rel to thisNode
		thisNode = thisNode.insertPeerNodeObj(newNode, uniqueLevel_)

		# Update new nodes sub-infoTree to reflect its json object structure
		thisNode.setValue()		

		return thisNode

#-------------- Insert subNode Helper methods (Search in thisNodes subNodes) ---------------------
# Build to search only thisNodes->subNodes/nodeChain	 
	# Insert new subNode on thisNodes & relative to "after" node specified by nodeIx
	def insertSubNode(self, nodeIx_, name_="", item_="", uniqueLevel_=-1):
		thisNode = self
		
		# Create new node
		newNode = jsonNode(name_, item_, thisNode, thisNode.nodeLevelSeparator_)

		# Was the node created?
		if newNode.error_ != "":
			#N => Signal failed to add new subNode
			self.error_ = "insertSubNode: Failed to Create jsonNode: " + newNode.error_
			return self		

		# Insert the new node rel. after node specified by ix
		thisNode = thisNode.insertSubNodeObj(nodeIx_, newNode, uniqueLevel_)

		# Update new nodes sub-infoTree to reflect its json object structure
		thisNode.setValue()		

		return thisNode
	
	# Insert new subNode (by value) on thisNode & relative to "after" node specified nodeId, Search in thisNode subNodes
	# use rootNode if you are unsure where the node is located
	def insertSubNodeById(self, nodeId_, name_="", item_="", uniqueLevel_=-1):
		thisNode = self
		
		# Create new subNode "Dont worry about parrentNode it is fixed by the core add subnode method"
		newNode = jsonNode(name_, item_, thisNode, thisNode.nodeLevelSeparator_)

		# Was the node created?
		if newNode.error_ != "":
			#N => Signal failed to add new subNode
			self.error_ = "insertSubNodeById: Failed to Create jsonNode: " + newNode.error_
			return self		

		# Insert the new Node rel. after node specified by id
		thisNode = thisNode.insertSubNodeObjById(nodeId_, newNode, uniqueLevel_)

		# Update new nodes sub-infoTree to reflect its json object structure
		thisNode.setValue()		

		return thisNode

	# Insert new subNode (by value) on thisNode & relative to "after" node specified by name, Search in thisNodes subNodes
	# use rootNode if you are unsure where the node is located
	def insertSubNodeByName(self, nodeName_, name_="", item_="", uniqueLevel_=-1):
		thisNode = self

		# Create new subNode
		newNode = jsonNode(name_, item_, thisNode, thisNode.nodeLevelSeparator_)

		# Was the node created?
		if newNode.error_ != "":
			#N => Signal failed to add new subNode
			self.error_ = "insertSubNodeByName: Failed to Create jsonNode: " + newNode.error_
			return self		

		# Insert the new Node rel. after node specified by name
		thisNode = thisNode.insertSubNodeObjByName(nodeName_, newNode, uniqueLevel_)

		# Update new nodes sub-infoTree to reflect its json object structure
		thisNode.setValue()		

		return thisNode

	# Insert new subNode (by value) on thisNode & relative to "after" node specified by nodeIx
	# use rootNode if you are unsure where the node is located
	def insertSubNodeByIx(self, nodeIx_, name_="", item_="", uniqueLevel_=-1):
		thisNode = self
		
		# Create new subNode "Dont worry about parrentNode it is fixed by the core add subnode method"
		newNode = jsonNode(name_, item_, thisNode, thisNode.nodeLevelSeparator_)

		# Was the node created?
		if newNode.error_ != "":
			#N => Signal failed to add new subNode
			self.error_ = "insertSubNodeByIx: Failed to Create jsonNode: " + newNode.error_
			return self		

		# Insert the new Node rel. after node specfied by ix
		thisNode = thisNode.insertSubNodeObjByIx(nodeIx_, newNode, uniqueLevel_)

		# Update new nodes sub-infoTree to reflect its json object structure
		thisNode.setValue()		

		return thisNode		   

	# Insert new subNode (by value) on thisNode & relative to "after" node specified by value, Search in thisNodes subNodes
	# use rootNode if you are unsure where the node is located
	def insertSubNodeByValue(self, value_, name_="", item_="", uniqueLevel_=-1):
		thisNode = self

		# Create new subNode
		newNode = jsonNode(name_, item_, thisNode, thisNode.nodeLevelSeparator_)

		# Was the node created?
		if newNode.error_ != "":
			#N => Signal failed to add new subNode
			self.error_ = "insertSubNodeByValue: Failed to Create jsonNode: " + newNode.error_
			return self		

		# Insert the new Node rel. after node specfied by value
		thisNode = thisNode.insertSubNodeObjByValue(value_, newNode, uniqueLevel_)

		# Update new nodes sub-infoTree to reflect its json object structure
		thisNode.setValue()		

		return thisNode

	# Insert copy of new subNodeObj (by object) to thisNode & relative to "after" nodeIx
	def insertSubNodeObjCopy(self, nodeIx_, newNode_, uniqueLevel_=-1):
		thisNode = self

		# Create copy of otherNode
		newNode = newNode_.copyNodeObj()

		# Was the node created?
		if newNode == "":
			#N => Signal failed to copy peerNode
			self.error_ = "insertSubNodeObjCopy: Failed to Copy jsonNode: " + newNode_.error_
			return self		

		# Insert the new node rel to nodeIx
		thisNode = thisNode.insertSubNodeObj(nodeIx_, newNode, uniqueLevel_)

		# Update new nodes sub-infoTree to reflect its json object structure
		thisNode.setValue()		

		return thisNode
		
#-------------------------------------------------

#----------- REPLACE node handling (Search from thisNode to end of sub-infoTree)-----------------------
# TODO: Implement core functions like add & insert nodes and used wrapper/helper functions that calls them!! (OK)
	# replace thisNode with the otherNode
	def replaceNodeObj(self, otherNode_, uniqueLevel_=-1):
		thisNode = self		   
		thisParrentNode = thisNode.parrentNode_
				
		# Is this rootNode?
		if(thisParrentNode == ""):
			# YES => rootNodes cannot be replaced
			self.error_ = "replaceNodeObj: rootNodes cannot be replaced!!"
			return self

		# Auto discover item type and update thisNode uniquenessLevel
		# Is this parrentNode a dict object?
		if thisParrentNode.isOrderedDict():
			#Y => Set uniqunessLevel to peerNode uniqueness since a dict cannot contain duplicate keys
			uniqueLevel_ = 2

		# Has uniquenessLevel been specified?
		if uniqueLevel_ < 0:
			#N => Use/Enerit thisNodes
			uniqueLevel_ = thisNode.uniqueLevel_											 					

		# Is node->value unique?
		# Is it infoTree Uniqueness?
		if(uniqueLevel_ == 1):
			# Does this node allready exist?
			thisRootNode = thisNode.getRootNode()
			existingNode = thisRootNode.findNodeByValue(otherNode_.item_)
			if(existingNode != ""):
				# Node exit just update frequency "match count"
				existingNode.freq_ += 1
				return self
		# Is it peerNode Uniqueness?
		if(uniqueLevel_ == 2):
			# Does this node allready exist as a peerNode?
			existingNode = thisNode.findPeerNodeByValue(otherNode_.item_)
			if(existingNode != ""):
				# Node exist just update frequency "match count"
				existingNode.freq_ += 1
				return self
		# Is it subNode Uniqueness?
		if(uniqueLevel_ == 3):
			# Does this node allready exist as a subNode?
			existingNode = thisNode.findSubNodeByValue(otherNode_.item_)
			if(existingNode != ""):
				# Node exist just update freq "match count"
				existingNode.freq_ += 1
				return self
		# Is it sub-infoTree Uniqueness
		if(uniqueLevel_ == 4):
			# Does this node allready exist as a subNode?
			existingNode = thisNode.findNodeByValue(otherNode_.item_)
			if(existingNode != ""):
				# Node exist just update freq "match count"
				existingNode.freq_ += 1
				return self

		# update this parrentNodes subNode structure "sub-infoTree"
		# Get thisNode ix
		ix = thisNode.nodeIx_
		# Fix parrentNode association/Link to thisNodes parrentNode
		otherNode_.parrentNode_ = thisParrentNode
		# Ensure the otherNode has the specified uniqueness level
		otherNode_.uniqueLevel_ = uniqueLevel_		  
		# Replace the node
		thisParrentNode.subNodes_[ix] = otherNode_
		# Fix nodeIds for the swapped node and its sub-infoTree
		thisParrentNode.subNodes_[ix].updateSubinfoTreeNodeIds()

		# Auto discover item type and update this parrentNodes json object structure "sub-infoTree"
		# Is this parrentNode a dict object?
		if thisParrentNode.isOrderedDict():
			#Y => Has this key allready been added?
			if not otherNode_.name_ in thisParrentNode.item_.keys():
				#N => Replace with new dict item, replace not supported for dicts so we must recreate the sub-infoTree of all nodes after the ref node
				thisParrentNode.replaceDictItemByKey(thisNode.name_, otherNode_.name_, otherNode_.item_)

		# Is this parrentNode a list Object?
		if thisParrentNode.isList():
			#Y => Replace thisItem with otherItem
			thisParrentNode.item_.replace(thisNode.nodeIx_, otherNode_.item_)

		# Update new nodes sub-infoTree to reflect its json object structure
		#otherNode_.setValue()					

		return thisParrentNode.subNodes_[ix]

	# Replace thisNode with a copy of otherNode_
	def replaceNodeObjCopy(self, otherNode_, uniqueLevel_=-1):
		thisNode = self
		thisParrentNode = thisNode.parrentNode_

		# Is this rootNode?
		if(thisNode.parrentNode_ == ""):
			# YES => rootNodes cannot be replaced
			self.error_ = "replaceNodeObjCopy: rootNodes cannot be replaced!!"			  
			return self

		# Auto discover item type and update thisNode uniquenessLevel
		# Is this parrentNode a dict object?
		if thisParrentNode.isOrderedDict():
			#Y => Set uniqunessLevel to peerNode uniqueness since a dict cannot contain duplicate keys
			uniqueLevel_ = 2

		# Has uniquenessLevel been specified?
		if uniqueLevel_ < 0:
			#N => Use/Enerit thisNodes
			uniqueLevel_ = self.uniqueLevel_		 

		# Is node->value unique?
		# Is it infoTree Uniqueness?
		if(uniqueLevel_ == 1):
			# Does this node allready exist?
			thisRootNode = thisNode.getRootNode()
			existingNode = thisRootNode.findNodeByValue(otherNode_.item_)
			if(existingNode != ""):
				# Node exit just update frequency "match count"
				existingNode.freq_ += 1
				return self
		# Is it peerNode Uniqueness?
		if(uniqueLevel_ == 2):
			# Does this node allready exist as a peerNode?
			existingNode = thisNode.findPeerNodeByValue(otherNode_.item_)
			if(existingNode != ""):
				# Node exist just update frequency "match count"
				existingNode.freq_ += 1
				return self
		# Is it subNode Uniqueness?
		if(uniqueLevel_ == 3):
			# Does this node allready exist as a subNode?
			existingNode = thisNode.findSubNodeByValue(otherNode_.item_)
			if(existingNode != ""):
				# Node exist just update freq "match count"
				existingNode.freq_ += 1
				return self
		# Is it sub-infoTree Uniqueness
		if(uniqueLevel_ == 4):
			# Does this node allready exist as a subNode?
			existingNode = thisNode.findNodeByValue(otherNode_.item_)
			if(existingNode != ""):
				# Node exist just update freq "match count"
				existingNode.freq_ += 1
				return self

		# Create Copy of otherNode
		otherNode = otherNode_.copyNodeObj()

		# update this parrentNodes subNode structure "sub-infoTree"
		# Get thisNodes ix
		ix = thisNode.nodeIx_
				
		# Fix thisNodes association/linking to parrentNode
		otherNode.parrentNode_ = thisParrentNode
		# Ensure the otherNode has the specified uniqueness level
		otherNode.uniqueLevel_ = uniqueLevel_		 
		# Replace subNode
		thisParrentNode.subNodes_[ix] = otherNode_
		# Fix subNode & its sub-infoTree nodeIds
		thisParrentNode.subNodes_[ix].updateSubinfoTreeNodeIds()

		# Auto discover item type and update this parrentNodes json object structure "sub-infoTree"
		# Is this parrentNode a dict object?
		if thisParrentNode.isOrderedDict():
			#Y => Has this key allready been added?
			if not otherNode_.name_ in thisParrentNode.item_.keys():
				#N => Replace with new dict item, replace not supported for dicts so we must recreate the sub-infoTree of all nodes after the ref node
				thisParrentNode.replaceDictItemByKey(thisNode.name_, otherNode_.name_, otherNode_.item_)

		# Is this parrentNode a list Object?
		if thisParrentNode.isList():
			#Y => Replace thisItem with otherItem
			thisParrentNode.item_.replace(thisNode.nodeIx_, otherNode_.item_)
			
		# Update new nodes sub-infoTree to reflect its json object structure
		#otherNode_.setValue()					

		return thisParrentNode.subNodes_[ix]	   

	# replace node specified by Id with otherNode, Search from thisNode to end of its sub-infoTree
	def replaceNodeObjById(self, nodeId_, otherNode_, uniqueLevel_=-1, startNode_ = ""):
		thisNode = self 
		startNode = startNode_
		
		# Has node search been restricted to a specific endNode?
		if startNode_ == "":
			#N => Assume thisNode sub-infoTree 
			startNode = thisNode

		# Find node specified by id
		thisParrentNode = ""
		while(thisNode != ""):
			# is this the node we are looking for?
			if(thisNode.nodeId_.lower() == nodeId_.lower()):
				# Node located
				thisParrentNode = thisNode.parrentNode_
				break

			# Get next node
			thisNode = thisNode.getNextNode(startNode)
		
		# Was the node found?
		if(thisParrentNode == ""):
			# NO
			self.error_ = "replaceNodeObjById: Unable to find node with Id " + nodeId_			  
			return self

		# Auto discover item type and update thisNode uniquenessLevel
		# Is this parrentNode a dict object?
		if thisParrentNode.isOrderedDict():
			#Y => Set uniqunessLevel to peerNode uniqueness since a dict cannot contain duplicate keys
			uniqueLevel_ = 2							

		# Has uniquenessLevel been specified?
		if uniqueLevel_ < 0:
			#N => Use/Enerit thisNodes
			uniqueLevel_ = thisNode.uniqueLevel_

		# Is node->value unique?
		# Is it infoTree Uniqueness?
		if(uniqueLevel_ == 1):
			# Does this node allready exist?
			thisRootNode = thisNode.getRootNode()
			existingNode = thisRootNode.findNodeByValue(otherNode_.item_)
			if(existingNode != ""):
				# Node exit just update frequency "match count"
				existingNode.freq_ += 1
				return self
		# Is it peerNode Uniqueness?
		if(uniqueLevel_ == 2):
			# Does this node allready exist as a peerNode?
			existingNode = thisNode.findPeerNodeByValue(otherNode_.item_)
			if(existingNode != ""):
				# Node exist just update frequency "match count"
				existingNode.freq_ += 1
				return self
		# Is it subNode Uniqueness?
		if(uniqueLevel_ == 3):
			# Does this node allready exist as a subNode?
			existingNode = thisNode.findSubNodeByValue(otherNode_.item_)
			if(existingNode != ""):
				# Node exist just update freq "match count"
				existingNode.freq_ += 1
				return self
		# Is it sub-infoTree Uniqueness
		if(uniqueLevel_ == 4):
			# Does this node allready exist as a subNode?
			existingNode = thisNode.findNodeByValue(otherNode_.item_)
			if(existingNode != ""):
				# Node exist just update freq "match count"
				existingNode.freq_ += 1
				return self		   
						
		# Assume the node was found
		# update this parrentNodes subNode structure "sub-infoTree"

		# Assume the node does not exist		
		ix = thisNode.nodeIx_

		# Fix parrentNode association/Link to thisNode
		otherNode_.parrentNode_ = thisParrentNode
		# Ensure the otherNode has the specified uniqueness level
		otherNode_.uniqueLevel_ = uniqueLevel_		  
		# Replace the node
		thisParrentNode.subNodes_[ix] = otherNode_

		# Fix nodeIds for the swapped node and its sub-infoTree
		thisParrentNode.subNodes_[ix].updateSubinfoTreeNodeIds()

		# Auto discover item type and update this parrentNodes json object structure "sub-infoTree"
		# Is this parrentNode a dict object?
		if thisParrentNode.isOrderedDict():
			#Y => Does this key allready exist?
			if not otherNode_.name_ in thisParrentNode.item_.keys():
				#N => Replace with new dict item, replace not supported for dicts so we must recreate the sub-infoTree of all nodes after the ref node
				thisParrentNode.replaceDictItemByKey(thisNode.name_, otherNode_.name_, otherNode_.item_)

		# Is this parrentNode a list Object?
		if thisParrentNode.isList():
			#Y => Replace thisItem with otherItem
			thisParrentNode.item_.replace(thisNode.nodeIx_, otherNode_.item_)

		# Update new nodes sub-infoTree to reflect its json object structure
		#otherNode_.setValue()			

		return thisParrentNode.subNodes_[ix]

	# replace node specified by name with otherNode, relative search from thisNode to end of its sub-infoTree
	def replaceNodeObjByName(self, name_, otherNode_, uniqueLevel_=-1, startNode_ = ""):
		thisNode = self 
		startNode = startNode_
		
		# Find node by name
		thisParrentNode = ""
		while(thisNode != ""):
			# is this the node we are looking for?
			if(thisNode.name_.lower() == name_.lower()):
				# Node located
				thisParrentNode = thisNode.parrentNode_
				break

			# Get next node
			thisNode = thisNode.getNextNode(startNode)
				
		# Was ref. Node found?
		if(thisParrentNode == ""):
			# NO 
			self.error_ = "replaceNodeObjByName: Unable to find node with name " + name_			
			return self

		# Auto discover item type and update thisNode uniquenessLevel
		# Is this parrentNode a dict object?
		if thisParrentNode.isOrderedDict():
			#Y => Set uniqunessLevel to peerNode uniqueness since a dict cannot contain duplicate keys
			uniqueLevel_ = 2											 		

		# Has uniquenessLevel been specified?
		if uniqueLevel_ < 0:
			#N => Use/Enerit thisNodes
			uniqueLevel_ = thisNode.uniqueLevel_		

		# Is node->value unique?
		# Is it infoTree Uniqueness?
		if(uniqueLevel_ == 1):
			# Does this node allready exist?
			thisRootNode = thisNode.getRootNode()
			existingNode = thisRootNode.findNodeByValue(otherNode_.item_)
			if(existingNode != ""):
				# Node exit just update frequency "match count"
				existingNode.freq_ += 1
				return self
		# Is it peerNode Uniqueness?
		if(uniqueLevel_ == 2):
			# Does this node allready exist as a peerNode?
			existingNode = thisNode.findPeerNodeByValue(otherNode_.item_)
			if(existingNode != ""):
				# Node exist just update frequency "match count"
				existingNode.freq_ += 1
				return self
		# Is it subNode Uniqueness?
		if(uniqueLevel_ == 3):
			# Does this node allready exist as a subNode?
			existingNode = thisNode.findSubNodeByValue(otherNode_.item_)
			if(existingNode != ""):
				# Node exist just update freq "match count"
				existingNode.freq_ += 1
				return self
		# Is it sub-infoTree Uniqueness
		if(uniqueLevel_ == 4):
			# Does this node allready exist as a subNode?
			existingNode = thisNode.findNodeByValue(otherNode_.item_)
			if(existingNode != ""):
				# Node exist just update freq "match count"
				existingNode.freq_ += 1
				return self		   

		# Assume the node was found
		# update this parrentNodes subNode structure "sub-infoTree"
		ix = thisNode.nodeIx_

		# Fix parrentNode association/Link to thisNode
		otherNode_.parrentNode_ = thisParrentNode
		# Ensure the otherNode has the specified uniqueness level
		otherNode_.uniqueLevel_ = uniqueLevel_		  
		# Replace the node
		thisParrentNode.subNodes_[ix] = otherNode_

		# Fix nodeIds for the swapped node and its sub-infoTree
		thisParrentNode.subNodes_[ix].updateSubinfoTreeNodeIds()

		# Auto discover item type and update this parrentNodes json object structure "sub-infoTree"
		# Is this parrentNode a dict object?
		if thisParrentNode.isOrderedDict():
			#Y => Has this key allready been added?
			if not otherNode_.name_ in thisParrentNode.item_.keys():
				#N => Replace with new dict item, replace not supported for dicts so we must recreate the sub-infoTree of all nodes after the ref node
				thisParrentNode.replaceDictItemByKey(thisNode.name_, otherNode_.name_, otherNode_.item_)

		# Is this parrentNode a list Object?
		if thisParrentNode.isList():
			#Y => Replace thisItem with otherItem
			thisParrentNode.item_.replace(thisNode.nodeIx_, otherNode_.item_)

		# Update new nodes sub-infoTree to reflect its json object structure
		#otherNode_.setValue()					

		return thisParrentNode.subNodes_[ix]		

	# replace node specified by value with otherNode, relative search from thisNode to end of its sub-infoTree
	def replaceNodeObjByValue(self, value_, otherNode_, uniqueLevel_=-1, startNode_ = ""):
		thisNode = self 
		startNode = startNode_
		
		# Find the reference node
		thisParrentNode=""
		while(thisNode != ""):
			# Is this the node we are looking for?
			# Is thisNode and value a ordered dict object
			if thisNode.isOrderedDict() and thisNode.isOrderedDict(value_):
				#Y => Is this the value we are looking for
				if thisNode.item_ == value_:
					#Y
					thisParrentNode = thisNode.parrentNode_
					break

			# Is thisNode and value a list object
			if thisNode.isList() and thisNode.isList(value_):
				#Y => Is this the value we are looking for
				if thisNode.item_ == value_:
					#Y
					thisParrentNode = thisNode.parrentNode_
					break					

			# Is thisNode and value a string
			if thisNode.isString() and thisNode.isString(value_):
				#Y => Is this the value we are looking for
				if(thisNode.item_.lower() == value_.lower()):
					#Y
					thisParrentNode = thisNode.parrentNode_
					break

			# Is thisNode and value a number
			if thisNode.isNumber() and thisNode.isNumber(value_):
				#Y => Is this the value we are looking for
				if thisNode.item_ == value_:
					#Y
					thisParrentNode = thisNode.parrentNode_
					break

			# Get next node
			thisNode = thisNode.getNextNode(startNode)
				
		# Was ref. Node found?
		if(thisParrentNode == ""):
			# NO 
			self.error_ = "replaceNodeObjByValue: Unable to find node with value " + self.getString(value_)			
			return self

		# Auto discover item type and update thisNode uniquenessLevel
		# Is this parrentNode a dict object?
		if thisParrentNode.isOrderedDict():
			#Y => Set uniqunessLevel to peerNode uniqueness since a dict cannot contain duplicate keys
			uniqueLevel_ = 2											 		

		# Has uniquenessLevel been specified?
		if uniqueLevel_ < 0:
			#N => Use/Enerit thisNodes
			uniqueLevel_ = thisNode.uniqueLevel_		

		# Is node->value unique?
		# Is it infoTree Uniqueness?
		if(uniqueLevel_ == 1):
			# Does this node allready exist?
			thisRootNode = thisNode.getRootNode()
			existingNode = thisRootNode.findNodeByValue(otherNode_.item_)
			if(existingNode != ""):
				# Node exit just update frequency "match count"
				existingNode.freq_ += 1
				return self
		# Is it peerNode Uniqueness?
		if(uniqueLevel_ == 2):
			# Does this node allready exist as a peerNode?
			existingNode = thisNode.findPeerNodeByValue(otherNode_.item_)
			if(existingNode != ""):
				# Node exist just update frequency "match count"
				existingNode.freq_ += 1
				return self
		# Is it subNode Uniqueness?
		if(uniqueLevel_ == 3):
			# Does this node allready exist as a subNode?
			existingNode = thisNode.findSubNodeByValue(otherNode_.item_)
			if(existingNode != ""):
				# Node exist just update freq "match count"
				existingNode.freq_ += 1
				return self
		# Is it sub-infoTree Uniqueness
		if(uniqueLevel_ == 4):
			# Does this node allready exist as a subNode?
			existingNode = thisNode.findNodeByValue(otherNode_.item_)
			if(existingNode != ""):
				# Node exist just update freq "match count"
				existingNode.freq_ += 1
				return self		   

		# Assume the node was found
		# update this parrentNodes subNode structure "sub-infoTree"
		ix = thisNode.nodeIx_

		# Fix parrentNode association/Link to thisNode
		otherNode_.parrentNode_ = thisParrentNode
		# Ensure the otherNode has the specified uniqueness level
		otherNode_.uniqueLevel_ = uniqueLevel_		  
		# Replace the node
		thisParrentNode.subNodes_[ix] = otherNode_

		# Fix nodeIds for the swapped node and its sub-infoTree
		thisParrentNode.subNodes_[ix].updateSubinfoTreeNodeIds()

		# Auto discover item type and update this parrentNodes json object structure "sub-infoTree"
		# Is this parrentNode a dict object?
		if thisParrentNode.isOrderedDict():
			#Y => Has this key allready been added?
			if not otherNode_.name_ in thisParrentNode.item_.keys():
				#N => Replace with new dict item, replace not supported for dicts so we must recreate the sub-infoTree of all nodes after the ref node
				thisParrentNode.replaceDictItemByKey(thisNode.name_, otherNode_.name_, otherNode_.item_)

		# Is this parrentNode a list Object?
		if thisParrentNode.isList():
			#Y => Replace thisItem with otherItem
			thisParrentNode.item_.replace(thisNode.nodeIx_, otherNode_.item_)

		# Update new nodes sub-infoTree to reflect its json object structure
		#otherNode_.setValue()					

		return thisParrentNode.subNodes_[ix]		

#-------- replace peerNode handling (Search in thisNode peerNodes)-----------
	# Replace peerNodeObj on same parrentNode/nodeChain as thisNode & relative to "after" thisNode
	def replacePeerNodeObj(self, otherNode_, uniqueLevel_=-1):
		thisNode = self		   
		thisParrentNode = thisNode.parrentNode_
				
		# Is this rootNode?
		if(thisParrentNode == ""):
			# YES => rootNodes cannot be replaced
			self.error_ = "replacePeerNodeObj: rootNodes cannot be replaced!!"
			return self

		# Is thisNode last subNode?
		if thisNode.nodeIx_ == thisParrentNode.lastSubNodeIx_:
			#Y => Signal fail
			self.error_ = "replacePeerNodeObj: Cannot replace subNode after last-subNode"
			return self

		# Auto discover item type and update thisNode uniquenessLevel
		# Is this parrentNode a dict object?
		if thisParrentNode.isOrderedDict():
			#Y => Set uniqunessLevel to peerNode uniqueness since a dict cannot contain duplicate keys
			uniqueLevel_ = 2

		# Has uniquenessLevel been specified?
		if uniqueLevel_ < 0:
			#N => Use/Enerit thisNodes
			uniqueLevel_ = thisNode.uniqueLevel_											 					

		# Is node->value unique?
		# Is it infoTree Uniqueness?
		if(uniqueLevel_ == 1):
			# Does this node allready exist?
			thisRootNode = thisNode.getRootNode()
			existingNode = thisRootNode.findNodeByValue(otherNode_.item_)
			if(existingNode != ""):
				# Node exit just update frequency "match count"
				existingNode.freq_ += 1
				return self
		# Is it peerNode Uniqueness?
		if(uniqueLevel_ == 2):
			# Does this node allready exist as a peerNode?
			existingNode = thisNode.findPeerNodeByValue(otherNode_.item_)
			if(existingNode != ""):
				# Node exist just update frequency "match count"
				existingNode.freq_ += 1
				return self
		# Is it subNode Uniqueness?
		if(uniqueLevel_ == 3):
			# Does this node allready exist as a subNode?
			existingNode = thisNode.findSubNodeByValue(otherNode_.item_)
			if(existingNode != ""):
				# Node exist just update freq "match count"
				existingNode.freq_ += 1
				return self
		# Is it sub-infoTree Uniqueness
		if(uniqueLevel_ == 4):
			# Does this node allready exist as a subNode?
			existingNode = thisNode.findNodeByValue(otherNode_.item_)
			if(existingNode != ""):
				# Node exist just update freq "match count"
				existingNode.freq_ += 1
				return self

		# update this parrentNodes subNode structure "sub-infoTree"
		# Get node after thisNode ix
		ix = thisNode.nodeIx_ + 1

		# Fix parrentNode association/Link to thisNodes parrentNode
		otherNode_.parrentNode_ = thisParrentNode
		# Ensure the otherNode has the specified uniqueness level
		otherNode_.uniqueLevel_ = uniqueLevel_		  
		# Replace the node
		thisParrentNode.subNodes_[ix] = otherNode_
		# Fix nodeIds for the swapped node and its sub-infoTree
		thisParrentNode.subNodes_[ix].updateSubinfoTreeNodeIds()

		# Auto discover item type and update this parrentNodes json object structure "sub-infoTree"
		# Is this parrentNode a dict object?
		if thisParrentNode.isOrderedDict():
			#Y => Has this key allready been added?
			if not otherNode_.name_ in thisParrentNode.item_.keys():
				#N => Replace with new dict item, replace not supported for dicts so we must recreate the sub-infoTree of all nodes after the ref node
				thisParrentNode.replaceDictItemByKey(thisNode.nodeIx_ + 1, otherNode_.name_, otherNode_.item_)

		# Is this parrentNode a list Object?
		if thisParrentNode.isList():
			#Y => Replace thisItem with otherItem
			thisParrentNode.item_.replace(thisNode.nodeIx_ + 1, otherNode_.item_)

		# Update new nodes sub-infoTree to reflect its json object structure
		#otherNode_.setValue()					

		return thisParrentNode.subNodes_[ix]

	# replace thisNodes peerNode specified by nodeId with the otherNode, Search in thisNode peerNodes
	def replacePeerNodeObjById(self, nodeId_, otherNode_, uniqueLevel_=-1):
		thisNode = self
		thisParrentNode = thisNode.parrentNode_

		# Is this rootNdoe?
		if thisParrentNode == "":
			#Y => Signal fail
			self.error_ = "replacePeerNodeObjById: rootNodes does not have peerNodes"
			return self

		# Find peerNode with specified nodeId
		thisParrentNode = ""
		ix = 0
		for node in thisNode.parrentNode_.subNodes_:
			# is This the node we are looking for?
			if(node.nodeId_.lower() == nodeId_.lower()):
				thisParrentNode = node.parrentNode_
				thisNode = node
				break

		# was the node found?
		if(thisParrentNode == ""):
			# NO
			self.error_ = "replacePeerNodeObjById: Unable to find node with Id " + nodeId_			 
			return self

		# Auto discover item type and update thisNode uniquenessLevel
		# Is this parrentNode a dict object?
		if thisParrentNode.isOrderedDict():
			#Y => Set uniqunessLevel to peerNode uniqueness since a dict cannot contain duplicate keys
			uniqueLevel_ = 2

		# Has uniquenessLevel been specified?
		if uniqueLevel_ < 0:
			#N => Use/Enerit thisNodes
			uniqueLevel_ = self.uniqueLevel_		
		
		# Is node->value unique?
		# Is it infoTree Uniqueness?
		if(uniqueLevel_ == 1):
			# Does this node allready exist?
			thisRootNode = thisNode.getRootNode()
			existingNode = thisRootNode.findNodeByValue(otherNode_.item_)
			if(existingNode != ""):
				# Node exit just update frequency "match count"
				existingNode.freq_ += 1
				return self
		# Is it peerNode Uniqueness?
		if(uniqueLevel_ == 2):
			# Does this node allready exist as a peerNode?
			existingNode = thisNode.findPeerNodeByValue(otherNode_.item_)
			if(existingNode != ""):
				# Node exist just update frequency "match count"
				existingNode.freq_ += 1
				return self
		# Is it subNode Uniqueness?
		if(uniqueLevel_ == 3):
			# Does this node allready exist as a subNode?
			existingNode = thisNode.findSubNodeByValue(otherNode_.item_)
			if(existingNode != ""):
				# Node exist just update freq "match count"
				existingNode.freq_ += 1
				return self
		# Is it sub-infoTree Uniqueness
		if(uniqueLevel_ == 4):
			# Does this node allready exist as a subNode?
			existingNode = thisNode.findNodeByValue(otherNode_.item_)
			if(existingNode != ""):
				# Node exist just update freq "match count"
				existingNode.freq_ += 1
				return self

		# Get subNode specifed by Ix
		ix = thisNode.nodeIx_

		# fix/Ensure the otherSubNode_ is associated/linked to thisNodes Parrent before the replace
		otherNode_.parrentNode_ = thisParrentNode
		# Ensure the otherSubNode has the specified uniqueness level
		otherNode_.uniqueLevel_ = uniqueLevel_		 

		# Replacse thisNode with otherNode
		thisParrentNode.subNodes_[ix] = otherNode_

		# Fix thisNodes sub-infoTree association/linking to parrentNode
		for node in thisParrentNode.subNodes_[ix].subNodes_:
			# fix subNodes association/link to parrentNode
			node.parrentNode_ = thisNode
				
		# Fix thisNode & its sub-infoTree nodeIds
		thisParrentNode.subNodes_[ix].updateSubinfoTreeNodeIds()

		# Auto discover item type and update this parrentNodes json object structure "sub-infoTree"
		# Is this parrentNode a dict object?
		if thisParrentNode.isOrderedDict():
			#Y => Replace with new dict item, replace not supported for dicts so we must recreate the sub-infoTree of all nodes after the ref node
			thisParrentNode.replaceDictItemByKey(thisNode.name_, otherNode_.name_, otherNode_.item_)

		# Is this parrentNode a list Object?
		if thisParrentNode.isList():
			#Y => Replace thisItem with otherItem
			thisParrentNode.item_.replace(thisNode.nodeIx_, otherNode_.item_)
			
		# Update new nodes sub-infoTree to reflect its json object structure
		#otherSubNode_.setValue()					

		return thisParrentNode.subNodes_[ix]

	# replace thisNodes peerNode specified by name with the otherNode, Search in thisNode peerNodes
	def replacePeerNodeObjByName(self, name_, otherNode_, uniqueLevel_=-1):
		thisNode = self
		thisParrentNode = thisNode.parrentNode_

		# Is this rootNode?
		if thisParrentNode == "":
			#Y => Signal fail
			self.error_ = "replacePeerNodeObjByName: rootNodes does not have peerNodes"
			return self

		# Find peerNode with specified nodeId
		thisParrentNode = ""
		ix = 0
		for node in thisNode.parrentNode_.subNodes_:
			# is This the node we are looking for?
			if(node.name_.lower() == name_.lower()):
				thisParrentNode = node.parrentNode_
				thisNode = node
				break

		# was the node found?
		if(thisParrentNode == ""):
			# NO
			self.error_ = "replacePeerNodeObjByName: Unable to find node with name " + name_			   
			return self

		# Auto discover item type and update thisNode uniquenessLevel
		# Is this parrentNode a dict object?
		if thisParrentNode.isOrderedDict():
			#Y => Set uniqunessLevel to peerNode uniqueness since a dict cannot contain duplicate keys
			uniqueLevel_ = 2

		# Has uniquenessLevel been specified?
		if uniqueLevel_ < 0:
			#N => Use/Enerit thisNodes
			uniqueLevel_ = self.uniqueLevel_		
		
		# Is node->value unique?
		# Is it infoTree Uniqueness?
		if(uniqueLevel_ == 1):
			# Does this node allready exist?
			thisRootNode = thisNode.getRootNode()
			existingNode = thisRootNode.findNodeByValue(otherNode_.item_)
			if(existingNode != ""):
				# Node exit just update frequency "match count"
				existingNode.freq_ += 1
				return self
		# Is it peerNode Uniqueness?
		if(uniqueLevel_ == 2):
			# Does this node allready exist as a peerNode?
			existingNode = thisNode.findPeerNodeByValue(otherNode_.item_)
			if(existingNode != ""):
				# Node exist just update frequency "match count"
				existingNode.freq_ += 1
				return self
		# Is it subNode Uniqueness?
		if(uniqueLevel_ == 3):
			# Does this node allready exist as a subNode?
			existingNode = thisNode.findSubNodeByValue(otherNode_.item_)
			if(existingNode != ""):
				# Node exist just update freq "match count"
				existingNode.freq_ += 1
				return self
		# Is it sub-infoTree Uniqueness
		if(uniqueLevel_ == 4):
			# Does this node allready exist as a subNode?
			existingNode = thisNode.findNodeByValue(otherNode_.item_)
			if(existingNode != ""):
				# Node exist just update freq "match count"
				existingNode.freq_ += 1
				return self
		
		# Get subNode specified by Ix
		ix = thisNode.nodeIx_

		# fix/Ensure the otherSubNode_ is associated/linked to thisNodes Parrent before the replace
		otherNode_.parrentNode_ = thisParrentNode
		# Ensure the otherSubNode has the specified uniqueness level
		otherNode_.uniqueLevel_ = uniqueLevel_		 

		# Replacse thisSubNode with otherSubNode
		thisParrentNode.subNodes_[ix] = otherNode_		  

		# Fix thisSubNodes sub-infoTree association/linking to parrentNode
		for node in thisParrentNode.subNodes_[ix].subNodes_:
			# fix subNodes association/link to parrentNode
			node.parrentNode_ = thisNode
				
		# Fix thisSubNode & its sub-infoTree nodeIds
		thisParrentNode.subNodes_[ix].updateSubinfoTreeNodeIds()

		# Auto discover item type and update this parrentNodes json object structure "sub-infoTree"
		# Is this parrentNode a dict object?
		if thisParrentNode.isOrderedDict():
			#Y => Replace with new dict item, replace not supported for dicts so we must recreate the sub-infoTree of all nodes after the ref node
			thisParrentNode.replaceDictItemByKey(thisNode.name_, otherNode_.name_, otherNode_.item_)

		# Is this parrentNode a list Object?
		if thisParrentNode.isList():
			#Y => Replace thisItem with otherItem
			thisParrentNode.item_.replace(thisNode.nodeIx_, otherNode_.item_)

		# Update new nodes sub-infoTree to reflect its json object structure
		#otherSubNode_.setValue()					

		return thisParrentNode.subNodes_[ix]

	# replace thisNodes peerNode specified by nodeIx with the otherNode, Search in thisNodes peerNodes
	def replacePeerNodeObjByIx(self, nodeIx_, otherNode_, uniqueLevel_=-1):
		thisNode = self
		thisParrentNode = thisNode.parrentNode_

		# Is this rootNode?
		if thisParrentNode == "":
			#Y => Signal fail
			self.error_ = "replacePeerNodeObjByIx: rootNodes does not have peerNodes"
			return self

		# Find node specified by ix
		# Is this nodeIx_ valid?
		if nodeIx_ < 0 or nodeIx_ > thisParrentNode.lastSubNodeIx_:
			#N => Signal attempt to insert peern node at invalid ix
			self.error_ = "replacePeerNodeObjByIx: last peerNode Ix of parrenNode " + thisParrentNode.name_ + " is "+ thisParrentNode.lastSubNodeIx_ + ", hence nodeIx " + str(nodeIx_) + " is not a valid ix"
			return self

		# Get peerNode specified by Ix
		thisNode = thisParrentNode.subNodes_[nodeIx_]

		# Auto discover item type and update thisNode uniquenessLevel
		# Is this parrentNode a dict object?
		if thisParrentNode.isOrderedDict():
			#Y => Set uniqunessLevel to peerNode uniqueness since a dict cannot contain duplicate keys
			uniqueLevel_ = 2		

		# Has uniquenessLevel been specified?
		if uniqueLevel_ < 0:
			#N => Use/Enerit thisNodes
			uniqueLevel_ = self.uniqueLevel_		
		
		# Is node->value unique?
		# Is it infoTree Uniqueness?
		if(uniqueLevel_ == 1):
			# Does this node allready exist?
			thisRootNode = thisNode.getRootNode()
			existingNode = thisRootNode.findNodeByValue(otherNode_.item_)
			if(existingNode != ""):
				# Node exit just update frequency "match count"
				existingNode.freq_ += 1
				return self
		# Is it peerNode Uniqueness?
		if(uniqueLevel_ == 2):
			# Does this node allready exist as a peerNode?
			existingNode = thisNode.findPeerNodeByValue(otherNode_.item_)
			if(existingNode != ""):
				# Node exist just update frequency "match count"
				existingNode.freq_ += 1
				return self
		# Is it subNode Uniqueness?
		if(uniqueLevel_ == 3):
			# Does this node allready exist as a subNode?
			existingNode = thisNode.findSubNodeByValue(otherNode_.item_)
			if(existingNode != ""):
				# Node exist just update freq "match count"
				existingNode.freq_ += 1
				return self
		# Is it sub-infoTree Uniqueness
		if(uniqueLevel_ == 4):
			# Does this node allready exist as a subNode?
			existingNode = thisNode.findNodeByValue(otherNode_.item_)
			if(existingNode != ""):
				# Node exist just update freq "match count"
				existingNode.freq_ += 1
				return self

		# fix/Ensure the otherSubNode_ is associated/linked to thisNodes Parrent before the replace
		otherNode_.parrentNode_ = thisParrentNode
		# Ensure the otherSubNode has the specified uniqueness level
		otherNode_.uniqueLevel_ = uniqueLevel_

		# Replacse thisSubNode with otherSubNode
		thisParrentNode.subNodes_[nodeIx_] = otherNode_

		# Fix thisNodes sub-infoTree association/linking to parrentNode
		for node in thisParrentNode.subNodes_[nodeIx_].subNodes_:
			# fix subNodes association/link to parrentNode
			node.parrentNode_ = thisNode
				
		# Fix thisSubNode & its sub-infoTree nodeIds
		thisParrentNode.subNodes_[nodeIx_].updateSubinfoTreeNodeIds()

		# Auto discover item type and update this parrentNodes json object structure "sub-infoTree"
		# Is this parrentNode a dict object?
		if thisParrentNode.isOrderedDict():
			#Y => Has this key allready been added?
			if not otherNode_.name_ in thisParrentNode.item_.keys():
				#N => Replace with new dict item, replace not supported for dicts so we must recreate the sub-infoTree of all nodes after the ref node
				thisParrentNode.replaceDictItemByKey(thisNode.name_, otherNode_.name_, otherNode_.item_)

		# Is this parrentNode a list Object?
		if thisParrentNode.isList():
			#Y => Replace thisItem with otherItem
			thisParrentNode.item_.replace(thisNode.nodeIx_, otherNode_.item_)

		# Update new nodes sub-infoTree to reflect its json object structure
		#otherSubNode_.setValue()					

		return thisParrentNode.subNodes_[nodeIx_]				  

	# replace thisNodes peerNode specified by value with the otherNode, Search in thisNode peerNodes
	def replacePeerNodeObjByValue(self, value_, otherNode_, uniqueLevel_=-1):
		thisNode = self
		thisParrentNode = thisNode.parrentNode_

		# Find subNode with specified nodeId
		thisParrentNode = ""
		ix = 0
		for node in thisNode.parrentNode_.subNodes_:
			# Is this the node we are looking for?
			# Is thisNode and value a ordered dict object
			if node.isOrderedDict() and node.isOrderedDict(value_):
				#Y => Is this the value we are looking for
				if node.item_ == value_:
					#Y
					thisParrentNode = node.parrentNode_
					thisNode = node
					break

			# Is thisNode and value a list object
			if node.isList() and node.isList(value_):
				#Y => Is this the value we are looking for
				if node.item_ == value_:
					#Y
					thisParrentNode = node.parrentNode_
					thisNode = node
					break					

			# Is thisNode and value a string
			if node.isString() and node.isString(value_):
				#Y => Is this the value we are looking for
				if(node.item_.lower() == value_.lower()):
					#Y
					thisParrentNode = node.parrentNode_
					thisNode = node
					break

			# Is thisNode and value a number
			if node.isNumber() and node.isNumber(value_):
				#Y => Is this the value we are looking for
				if node.item_ == value_:
					#Y
					thisParrentNode = node.parrentNode_
					thisNode = node
					break

		# was the node found?
		if(thisParrentNode == ""):
			# NO
			self.error_ = "replaceSubNodeObjByName: Unable to find node with value " + self.getString(value_)			   
			return self

		# Auto discover item type and update thisNode uniquenessLevel
		# Is this parrentNode a dict object?
		if thisParrentNode.isOrderedDict():
			#Y => Set uniqunessLevel to peerNode uniqueness since a dict cannot contain duplicate keys
			uniqueLevel_ = 2

		# Has uniquenessLevel been specified?
		if uniqueLevel_ < 0:
			#N => Use/Enerit thisNodes
			uniqueLevel_ = self.uniqueLevel_		
		
		# Is node->value unique?
		# Is it infoTree Uniqueness?
		if(uniqueLevel_ == 1):
			# Does this node allready exist?
			thisRootNode = thisNode.getRootNode()
			existingNode = thisRootNode.findNodeByValue(otherNode_.item_)
			if(existingNode != ""):
				# Node exit just update frequency "match count"
				existingNode.freq_ += 1
				return self
		# Is it peerNode Uniqueness?
		if(uniqueLevel_ == 2):
			# Does this node allready exist as a peerNode?
			existingNode = thisNode.findPeerNodeByValue(otherNode_.item_)
			if(existingNode != ""):
				# Node exist just update frequency "match count"
				existingNode.freq_ += 1
				return self
		# Is it subNode Uniqueness?
		if(uniqueLevel_ == 3):
			# Does this node allready exist as a subNode?
			existingNode = thisNode.findSubNodeByValue(otherNode_.item_)
			if(existingNode != ""):
				# Node exist just update freq "match count"
				existingNode.freq_ += 1
				return self
		# Is it sub-infoTree Uniqueness
		if(uniqueLevel_ == 4):
			# Does this node allready exist as a subNode?
			existingNode = thisNode.findNodeByValue(otherNode_.item_)
			if(existingNode != ""):
				# Node exist just update freq "match count"
				existingNode.freq_ += 1
				return self
		
		# Get subNode specified by Ix
		ix = thisNode.nodeIx_

		# fix/Ensure the otherSubNode_ is associated/linked to thisNodes Parrent before the replace
		otherNode_.parrentNode_ = thisParrentNode
		# Ensure the otherSubNode has the specified uniqueness level
		otherNode_.uniqueLevel_ = uniqueLevel_		 

		# Replacse thisSubNode with otherSubNode
		thisParrentNode.subNodes_[ix] = otherNode_		  

		# Fix thisSubNodes sub-infoTree association/linking to parrentNode
		for node in thisParrentNode.subNodes_[ix].subNodes_:
			# fix subNodes association/link to parrentNode
			node.parrentNode_ = thisNode
				
		# Fix thisSubNode & its sub-infoTree nodeIds
		thisParrentNode.subNodes_[ix].updateSubinfoTreeNodeIds()

		# Auto discover item type and update this parrentNodes json object structure "sub-infoTree"
		# Is this parrentNode a dict object?
		if thisParrentNode.isOrderedDict():
			#Y => Replace with new dict item, replace not supported for dicts so we must recreate the sub-infoTree of all nodes after the ref node
			thisParrentNode.replaceDictItemByKey(thisNode.name_, otherNode_.name_, otherNode_.item_)

		# Is this parrentNode a list Object?
		if thisParrentNode.isList():
			#Y => Replace thisItem with otherItem
			thisParrentNode.item_.replace(thisNode.nodeIx_, otherNode_.item_)

		# Update new nodes sub-infoTree to reflect its json object structure
		#otherSubNode_.setValue()					

		return thisParrentNode.subNodes_[ix]

	# Replace thisNodes peerNode specified by nodeIx with copy of otherNode, Search in thisNodes peerNodes
	def replacePeerNodeObjCopy(self, nodeIx_, otherNode_, uniqueLevel_=-1):
		thisNode = self
		thisParrentNode = thisNode.parrentNode_

		# Is this rootNode?
		if thisParrentNode == "":
			#Y => Signal fail
			self.error_ = "replacePeerNodeObjByCopy: rootNodes does not have peerNodes"
			return self

		# Find node specified by ix
		# Is this nodeIx_ valid?
		if nodeIx_ < 0 or nodeIx_ > thisParrentNode.lastSubNodeIx_:
			#N => Signal attempt to insert peern node at invalid ix
			self.error_ = "replacePeerNodeObjByCopy: last peerNode Ix of parrenNode " + thisParrentNode.name_ + " is "+ thisParrentNode.lastSubNodeIx_ + ", hence nodeIx " + str(nodeIx_) + " is not a valid ix"
			return self			

		# Get peerNode specified by Ix
		thisNode = thisParrentNode.subNodes_[nodeIx_]

		# Auto discover item type and update thisNode uniquenessLevel
		# Is this parrentNode a dict object?
		if thisParrentNode.isOrderedDict():
			#Y => Set uniqunessLevel to peerNode uniqueness since a dict cannot contain duplicate keys
			uniqueLevel_ = 2		

		# Has uniquenessLevel been specified?
		if uniqueLevel_ < 0:
			#N => Use/Enerit thisNodes
			uniqueLevel_ = self.uniqueLevel_		

		# Is node->value unique?
		# Is it infoTree Uniqueness?
		if(uniqueLevel_ == 1):
			# Does this node allready exist?
			thisRootNode = thisNode.getRootNode()
			existingNode = thisRootNode.findNodeByValue(otherNode_.item_)
			if(existingNode != ""):
				# Node exit just update frequency "match count"
				existingNode.freq_ += 1
				return self
		# Is it peerNode Uniqueness?
		if(uniqueLevel_ == 2):
			# Does this node allready exist as a peerNode?
			existingNode = thisNode.findPeerNodeByValue(otherNode_.item_)
			if(existingNode != ""):
				# Node exist just update frequency "match count"
				existingNode.freq_ += 1
				return self
		# Is it subNode Uniqueness?
		if(uniqueLevel_ == 3):
			# Does this node allready exist as a subNode?
			existingNode = thisNode.findSubNodeByValue(otherNode_.item_)
			if(existingNode != ""):
				# Node exist just update freq "match count"
				existingNode.freq_ += 1
				return self
		# Is it sub-infoTree Uniqueness
		if(uniqueLevel_ == 4):
			# Does this node allready exist as a subNode?
			existingNode = thisNode.findNodeByValue(otherNode_.item_)
			if(existingNode != ""):
				# Node exist just update freq "match count"
				existingNode.freq_ += 1
				return self		   
		
		# Create copy of otherSubNode
		otherNode = otherNode_.copyNodeObj()

		# fix/Ensure the otherSubNode_ is associated/linked to thisNodes Parrent before the replace
		otherNode.parrentNode_ = thisParrentNode
		# Ensure the otherSubNode has the specified uniqueness level
		otherNode_.uniqueLevel_ = uniqueLevel_		 

		# Replacse thisSubNode with otherSubNode
		thisParrentNode.subNodes_[nodeIx_] = otherNode_

		# Fix thisSubNodes sub-infoTree association/linking to parrentNode
		for node in thisParrentNode.subNodes_[nodeIx_].subNodes_:
			# fix subNodes association/link to parrentNode
			node.parrentNode_ = thisNode
				
		# Fix thisSubNode & its sub-infoTree nodeIds
		thisParrentNode.subNodes_[nodeIx_].updateSubinfoTreeNodeIds()

		# Auto discover item type and update this parrentNodes json object structure "sub-infoTree"
		# Is this parrentNode a dict object?
		if thisParrentNode.isOrderedDict():
			#Y => Replace with new dict item, replace not supported for dicts so we must recreate the sub-infoTree of all nodes after the ref node
			thisParrentNode.replaceDictItemByKey(thisNode.name_, otherNode_.name_, otherNode_.item_)

		# Is this parrentNode a list Object?
		if thisParrentNode.isList():
			#Y => Replace thisItem with otherItem
			thisParrentNode.item_.replace(thisNode.nodeIx_, otherNode_.item_)

		# Update new nodes sub-infoTree to reflect its json object structure
		#otherSubNode_.setValue()					

		return thisParrentNode.subNodes_[nodeIx_]

#-------- replace subNode handling (Search in thisNodes subNodes)------------
	# replace thisNodes sub-infoTree with the otherNodes sub-infoTree "replace nodeChain"
	def replaceSubinfoTreeObj(self, otherNode_):
		thisNode = self
		thisParrentNode = thisNode
		
		# update this parrentNodes subNode structure "sub-infoTree"		
		# Get thisNodes ix
		ix = thisNode.nodeIx_
				
		# Replace sub-infoTree
		thisParrentNode.subNodes_ = otherNode_.subNodes_
		thisParrentNode.lastSubNodeIx_ = otherNode_.lastSubNodeIx_

		# Fix thisNodes sub-infoTree association/linking to parrentNode
		for node in thisParrentNode.subNodes_:
			# fix subNodes association/link to parrentNode
			node.parrentNode_ = thisParrentNode

		# Fix subNode & its sub-infoTree nodeIds
		thisParrentNode.updateSubinfoTreeNodeIds()

		# Auto discover item type and update this parrentNodes json object structure "sub-infoTree"
		# Is this parrentNode a dict object?
		if thisParrentNode.isOrderedDict():
			#Y => Replace with new dict item, replace not supported for dicts so we must recreate the sub-infoTree of all nodes after the ref node			
			thisParrentNode.item_ = otherNode_.item_

		# Is this parrentNode a list Object?
		if thisParrentNode.isList():
			#Y => Replace thisItem with otherItem
			thisParrentNode.item_ = otherNode.item_

		# Update new nodes sub-infoTree to reflect its json object structure
		#otherNode_.setValue()					

		return thisParrentNode
		
	# replace thisNodes sub-infoTree with copy of otherNodes sub-infoTree "replace nodeChain"
	def replaceSubinfoTreeObjCopy(self, otherNode_):
		thisNode = self
		thisParrentNode = thisNode
		
		# Create Copy of otherNode
		otherNode = otherNode_.copyNodeObj()

		# update this parrentNodes subNode structure "sub-infoTree"		
		# Get thisNodes nodeIx
		ix = thisNode.nodeIx_
				
		# Replace sub-infoTree
		thisParrentNode.subNodes_ = otherNode.subNodes_
		thisParrentNode.lastSubNodeIx_ = otherNode.lastSubNodeIx_

		# Fix thisNodes sub-infoTree association/linking to parrentNode
		for node in thisParrentNode.subNodes_:
			# fix subNodes association/link to parrentNode
			node.parrentNode_ = thisNode

		# Fix subNode & its sub-infoTree nodeIds
		thisParrentNode.updateSubinfoTreeNodeIds()

		# Auto discover item type and update this parrentNodes json object structure "sub-infoTree"
		# Is this parrentNode a dict object?
		if thisParrentNode.isOrderedDict():
			#Y => Replace with new dict item, replace not supported for dicts so we must recreate the sub-infoTree of all nodes after the ref node			
			thisParrentNode.item_ = otherNode.item_

		# Is this parrentNode a list Object?
		if thisParrentNode.isList():
			#Y => Replace thisItem with otherItem
			thisParrentNode.item_ = otherNode.item_

		# Update new nodes sub-infoTree to reflect its json object structure
		#otherNode_.setValue()							

		return thisParrentNode.subNodes_[ix]

	# replace sub-infoTree of node specified by Id with otherNode sub-infoTree, Search from thisNode to end of its sub-infoTree
	def replaceSubinfoTreeObjById(self, nodeId_, otherNode_, uniqueLevel_=-1, startNode_ = ""):
		thisNode = self 
		startNode = startNode_
		
		# Find node specified by id
		thisParrentNode = ""
		while(thisNode != ""):
			# is this the node we are looking for?
			if(thisNode.nodeId_.lower() == nodeId_.lower()):
				# Node located
				thisParrentNode = thisNode.parrentNode_
				break

			# Get next node
			thisNode = thisNode.getNextNode(startNode)
		
		# Was the node found?
		if(thisParrentNode == ""):
			# NO
			self.error_ = "replaceSubinfoTreeObjById: Unable to find node with Id " + nodeId_			 
			return self

		# Has uniquenessLevel been specified?
		if uniqueLevel_ < 0:
			#N => Use/Enerit thisNodes
			uniqueLevel_ = thisNode.uniqueLevel_		

		# Is node->value unique?
		# Is it infoTree Uniqueness?
		if(uniqueLevel_ == 1):
			# Does this node allready exist?
			thisRootNode = thisNode.getRootNode()
			existingNode = thisRootNode.findNodeByValue(otherNode_.item_)
			if(existingNode != ""):
				# Node exit just update frequency "match count"
				existingNode.freq_ += 1
				return self
		# Is it peerNode Uniqueness?
		if(uniqueLevel_ == 2):
			# Does this node allready exist as a peerNode?
			existingNode = thisNode.findPeerNodeByValue(otherNode_.item_)
			if(existingNode != ""):
				# Node exist just update frequency "match count"
				existingNode.freq_ += 1
				return self
		# Is it subNode Uniqueness?
		if(uniqueLevel_ == 3):
			# Does this node allready exist as a subNode?
			existingNode = thisNode.findSubNodeByValue(otherNode_.item_)
			if(existingNode != ""):
				# Node exist just update freq "match count"
				existingNode.freq_ += 1
				return self
		# Is it sub-infoTree Uniqueness
		if(uniqueLevel_ == 4):
			# Does this node allready exist as a subNode?
			existingNode = thisNode.findNodeByValue(otherNode_.item_)
			if(existingNode != ""):
				# Node exist just update freq "match count"
				existingNode.freq_ += 1
				return self		   
						
		# Assume the node was found
		# update this parrentNodes subNode structure "sub-infoTree"	
		# Get thisNode nodeIx
		ix = thisNode.nodeIx_

		# Replace sub-infoTree
		# Fix parrentNode association/Link to thisNode
		otherNode_.parrentNode_ = thisParrentNode
		# Ensure the otherNode has the specified uniqueness level
		otherNode_.uniqueLevel_ = uniqueLevel_		  
		
		# Replace sub-infoTree
		thisParrentNode.subNodes_[ix].subNodes_ = otherNode_.subNodes_
		thisParrentNode.subNodes_[ix].lastSubNodeIx_ = otherNode_.lastSubNodeIx_

		# Fix thisNodes sub-infoTree association/linking to parrentNode
		for node in thisParrentNode.subNodes_[ix].subNodes_:
			# fix subNodes association/link to parrentNode
			node.parrentNode_ = thisNode

		# Fix nodeIds for the swapped node and its sub-infoTree
		thisParrentNode.subNodes_[ix].updateSubinfoTreeNodeIds()

		# Auto discover item type and update this parrentNodes json object structure "sub-infoTree"
		# Is this parrentNode a dict object?
		if thisParrentNode.isOrderedDict():
			#Y => Replace with new dict item, replace not supported for dicts so we must recreate the sub-infoTree of all nodes after the ref node			
			thisParrentNode.replaceDictItemByKey(thisNode.name_, thisNode.name_, otherNode_.item_)

		# Is this parrentNode a list Object?
		if thisParrentNode.isList():
			#Y => Replace thisItem with otherItem
			thisParrentNode.item_.replace(thisNode.nodeIx_, otherNode_.item_)

		# Update new nodes sub-infoTree to reflect its json object structure
		#otherNode_.setValue()					

		return thisParrentNode.subNodes_[ix]

	# replace sub-infoTree of node specified by name with otherNode sub-infoTree, relative search from thisNode to end of its sub-infoTree
	def replaceSubinfoTreeObjByName(self, name_, otherNode_, uniqueLevel_=-1, startNode_ = ""):
		thisNode = self 
		startNode = startNode_
		
		# Find node specified by name
		thisParrentNode = ""
		while(thisNode != ""):
			# is this the node we are looking for?
			if(thisNode.name_.lower() == name_.lower()):
				# Node located
				thisParrentNode = thisNode.parrentNode_
				break

			# Get next node
			thisNode = thisNode.getNextNode(startNode)
		
		# Was the node found?
		if(thisParrentNode == ""):
			# NO
			self.error_ = "replaceSubinfoTreeObjByName: Unable to find node with name " + name_			   
			return self

		# Has uniquenessLevel been specified?
		if uniqueLevel_ < 0:
			#N => Use/Enerit thisNodes
			uniqueLevel_ = thisNode.uniqueLevel_		

		# Is node->value unique?
		# Is it infoTree Uniqueness?
		if(uniqueLevel_ == 1):
			# Does this node allready exist?
			thisRootNode = thisNode.getRootNode()
			existingNode = thisRootNode.findNodeByValue(otherNode_.item_)
			if(existingNode != ""):
				# Node exit just update frequency "match count"
				existingNode.freq_ += 1
				return self
		# Is it peerNode Uniqueness?
		if(uniqueLevel_ == 2):
			# Does this node allready exist as a peerNode?
			existingNode = thisNode.findPeerNodeByValue(otherNode_.item_)
			if(existingNode != ""):
				# Node exist just update frequency "match count"
				existingNode.freq_ += 1
				return self
		# Is it subNode Uniqueness?
		if(uniqueLevel_ == 3):
			# Does this node allready exist as a subNode?
			existingNode = thisNode.findSubNodeByValue(otherNode_.item_)
			if(existingNode != ""):
				# Node exist just update freq "match count"
				existingNode.freq_ += 1
				return self
		# Is it sub-infoTree Uniqueness
		if(uniqueLevel_ == 4):
			# Does this node allready exist as a subNode?
			existingNode = thisNode.findNodeByValue(otherNode_.item_)
			if(existingNode != ""):
				# Node exist just update freq "match count"
				existingNode.freq_ += 1
				return self		   
						
		# Assume the node was found
		# update this parrentNodes subNode structure "sub-infoTree"	
		# Get thisNode nodeIx
		ix = thisNode.nodeIx_

		# Replace sub-infoTree
		# Fix parrentNode association/Link to thisNode
		otherNode_.parrentNode_ = thisParrentNode
		# Ensure the otherNode has the specified uniqueness level
		otherNode_.uniqueLevel_ = uniqueLevel_		  

		# Replace the sub-infoTree
		thisParrentNode.subNodes_[ix].subNodes_ = otherNode_.subNodes_
		thisParrentNode.subNodes_[ix].lastSubNodeIx_ = otherNode_.lastSubNodeIx_

		# Fix thisNodes sub-infoTree association/linking to parrentNode
		for node in thisParrentNode.subNodes_[ix].subNodes_:
			# fix subNodes association/link to parrentNode
			node.parrentNode_ = thisNode

		# Fix nodeIds for the swapped node and its sub-infoTree
		thisParrentNode.subNodes_[ix].updateSubinfoTreeNodeIds()

		# Auto discover item type and update this parrentNodes json object structure "sub-infoTree"
		# Is this parrentNode a dict object?
		if thisParrentNode.isOrderedDict():
			#Y => Replace with new dict item, replace not supported for dicts so we must recreate the sub-infoTree of all nodes after the ref node			
			thisParrentNode.replaceDictItemByKey(thisNode.name_, thisNode.name_, otherNode_.item_)

		# Is this parrentNode a list Object?
		if thisParrentNode.isList():
			#Y => Replace thisItem with otherItem
			thisParrentNode.item_.replace(thisNode.nodeIx_, otherNode_.item_)

		# Update new nodes sub-infoTree to reflect its json object structure
		#otherNode_.setValue()							

		return thisParrentNode.subNodes_[ix]			

	# replace sub-infoTree of node specified by value with otherNode sub-infoTree, relative search from thisNode to end of its sub-infoTree
	def replaceSubinfoTreeObjByValue(self, value_, otherNode_, uniqueLevel_=-1, startNode_ = ""):
		thisNode = self 
		startNode = startNode_
		
		# Find the reference node
		thisParrentNode=""
		while(thisNode != ""):
			# Is this the node we are looking for?
			# Is thisNode and value a ordered dict object
			if thisNode.isOrderedDict() and thisNode.isOrderedDict(value_):
				#Y => Is this the value we are looking for
				if thisNode.item_ == value_:
					#Y
					thisParrentNode = thisNode.parrentNode_
					break

			# Is thisNode and value a list object
			if thisNode.isList() and thisNode.isList(value_):
				#Y => Is this the value we are looking for
				if thisNode.item_ == value_:
					#Y
					thisParrentNode = thisNode.parrentNode_
					break					

			# Is thisNode and value a string
			if thisNode.isString() and thisNode.isString(value_):
				#Y => Is this the value we are looking for
				if(thisNode.item_.lower() == value_.lower()):
					#Y
					thisParrentNode = thisNode.parrentNode_
					break

			# Is thisNode and value a number
			if thisNode.isNumber() and thisNode.isNumber(value_):
				#Y => Is this the value we are looking for
				if thisNode.item_ == value_:
					#Y
					thisParrentNode = thisNode.parrentNode_
					break

			# Get next node
			thisNode = thisNode.getNextNode(startNode)
		
		# Was the node found?
		if(thisParrentNode == ""):
			# NO
			self.error_ = "replaceSubinfoTreeObjByName: Unable to find node with value " + self.getString(value_)			   
			return self

		# Has uniquenessLevel been specified?
		if uniqueLevel_ < 0:
			#N => Use/Enerit thisNodes
			uniqueLevel_ = thisNode.uniqueLevel_		

		# Is node->value unique?
		# Is it infoTree Uniqueness?
		if(uniqueLevel_ == 1):
			# Does this node allready exist?
			thisRootNode = thisNode.getRootNode()
			existingNode = thisRootNode.findNodeByValue(otherNode_.item_)
			if(existingNode != ""):
				# Node exit just update frequency "match count"
				existingNode.freq_ += 1
				return self
		# Is it peerNode Uniqueness?
		if(uniqueLevel_ == 2):
			# Does this node allready exist as a peerNode?
			existingNode = thisNode.findPeerNodeByValue(otherNode_.item_)
			if(existingNode != ""):
				# Node exist just update frequency "match count"
				existingNode.freq_ += 1
				return self
		# Is it subNode Uniqueness?
		if(uniqueLevel_ == 3):
			# Does this node allready exist as a subNode?
			existingNode = thisNode.findSubNodeByValue(otherNode_.item_)
			if(existingNode != ""):
				# Node exist just update freq "match count"
				existingNode.freq_ += 1
				return self
		# Is it sub-infoTree Uniqueness
		if(uniqueLevel_ == 4):
			# Does this node allready exist as a subNode?
			existingNode = thisNode.findNodeByValue(otherNode_.item_)
			if(existingNode != ""):
				# Node exist just update freq "match count"
				existingNode.freq_ += 1
				return self		   
						
		# Assume the node was found
		# update this parrentNodes subNode structure "sub-infoTree"	
		# Get thisNode nodeIx
		ix = thisNode.nodeIx_

		# Replace sub-infoTree
		# Fix parrentNode association/Link to thisNode
		otherNode_.parrentNode_ = thisParrentNode
		# Ensure the otherNode has the specified uniqueness level
		otherNode_.uniqueLevel_ = uniqueLevel_		  

		# Replace the sub-infoTree
		thisParrentNode.subNodes_[ix].subNodes_ = otherNode_.subNodes_
		thisParrentNode.subNodes_[ix].lastSubNodeIx_ = otherNode_.lastSubNodeIx_

		# Fix thisNodes sub-infoTree association/linking to parrentNode
		for node in thisParrentNode.subNodes_[ix].subNodes_:
			# fix subNodes association/link to parrentNode
			node.parrentNode_ = thisNode

		# Fix nodeIds for the swapped node and its sub-infoTree
		thisParrentNode.subNodes_[ix].updateSubinfoTreeNodeIds()

		# Auto discover item type and update this parrentNodes json object structure "sub-infoTree"
		# Is this parrentNode a dict object?
		if thisParrentNode.isOrderedDict():
			#Y => Replace with new dict item, replace not supported for dicts so we must recreate the sub-infoTree of all nodes after the ref node			
			thisParrentNode.replaceDictItemByKey(thisNode.name_, thisNode.name_, otherNode_.item_)

		# Is this parrentNode a list Object?
		if thisParrentNode.isList():
			#Y => Replace thisItem with otherItem
			thisParrentNode.item_.replace(thisNode.nodeIx_, otherNode_.item_)

		# Update new nodes sub-infoTree to reflect its json object structure
		#otherNode_.setValue()							

		return thisParrentNode.subNodes_[ix]			

	# replace thisNodes subNode specified by Ix with the otherNode sub-infoTree, Search in thisNodes subNodes
	def replaceSubNodeObj(self, nodeIx_, otherNode_, uniqueLevel_=-1):
		thisNode = self
		thisParrentNode = thisNode

		# Find node specified by ix
		# Is this nodeIx_ valid?
		if nodeIx_ < 0 or nodeIx_ > thisParrentNode.lastSubNodeIx_:
			#N => Signal attempt to insert peern node at invalid ix
			self.error_ = "replaceSubNodeObjByIx: last subNode Ix of parrenNode " + thisParrentNode.name_ + " is "+ thisParrentNode.lastSubNodeIx_ + ", hence nodeIx " + str(nodeIx_) + " is not a valid ix"
			return self			

		# Auto discover item type and update thisNode uniquenessLevel
		# Is this parrentNode a dict object?
		if thisParrentNode.isOrderedDict():
			#Y => Set uniqunessLevel to peerNode uniqueness since a dict cannot contain duplicate keys
			uniqueLevel_ = 2		

		# Has uniquenessLevel been specified?
		if uniqueLevel_ < 0:
			#N => Use/Enerit thisNodes
			uniqueLevel_ = self.uniqueLevel_		
		
		# Is node->value unique?
		# Is it infoTree Uniqueness?
		if(uniqueLevel_ == 1):
			# Does this node allready exist?
			thisRootNode = thisNode.getRootNode()
			existingNode = thisRootNode.findNodeByValue(otherNode_.item_)
			if(existingNode != ""):
				# Node exit just update frequency "match count"
				existingNode.freq_ += 1
				return self
		# Is it peerNode Uniqueness?
		if(uniqueLevel_ == 2):
			# Does this node allready exist as a peerNode?
			existingNode = thisNode.findPeerNodeByValue(otherNode_.item_)
			if(existingNode != ""):
				# Node exist just update frequency "match count"
				existingNode.freq_ += 1
				return self
		# Is it subNode Uniqueness?
		if(uniqueLevel_ == 3):
			# Does this node allready exist as a subNode?
			existingNode = thisNode.findSubNodeByValue(otherNode_.item_)
			if(existingNode != ""):
				# Node exist just update freq "match count"
				existingNode.freq_ += 1
				return self
		# Is it sub-infoTree Uniqueness
		if(uniqueLevel_ == 4):
			# Does this node allready exist as a subNode?
			existingNode = thisNode.findNodeByValue(otherNode_.item_)
			if(existingNode != ""):
				# Node exist just update freq "match count"
				existingNode.freq_ += 1
				return self

		# get subNode specified by ix
		thisNode = thisParrentNode.subNodes_[nodeIx_]

		# fix/Ensure the otherSubNode_ is associated/linked to thisNodes Parrent before the replace
		otherNode_.parrentNode_ = thisParrentNode
		# Ensure the otherSubNode has the specified uniqueness level
		otherNode_.uniqueLevel_ = uniqueLevel_

		# Replacse thisSubNode with otherSubNode
		thisParrentNode.subNodes_[nodeIx_] = otherNode_

		# Fix thisSubNodes sub-infoTree association/linking to parrentNode
		for node in thisParrentNode.subNodes_[nodeIx_].subNodes_:
			# fix subNodes association/link to parrentNode
			node.parrentNode_ = thisNode
				
		# Fix thisSubNode & its sub-infoTree nodeIds
		thisParrentNode.subNodes_[nodeIx_].updateSubinfoTreeNodeIds()

		# Auto discover item type and update this parrentNodes json object structure "sub-infoTree"
		# Is this parrentNode a dict object?
		if thisParrentNode.isOrderedDict():
			#Y => Has this key allready been added?
			if not otherNode_.name_ in thisParrentNode.item_.keys():
				#N => Replace with new dict item, replace not supported for dicts so we must recreate the sub-infoTree of all nodes after the ref node
				thisParrentNode.replaceDictItemByKey(thisNode.name_, otherNode_.name_, otherNode_.item_)

		# Is this parrentNode a list Object?
		if thisParrentNode.isList():
			#Y => Replace thisItem with otherItem
			thisParrentNode.item_.replace(thisNode.nodeIx_, otherNode_.item_)

		# Update new nodes sub-infoTree to reflect its json object structure
		#otherSubNode_.setValue()					

		return thisParrentNode.subNodes_[nodeIx_]

	# replace thisNodes subNode specified by nodeId with the otherSubNode, Search in thisNode subNodes
	def replaceSubNodeObjById(self, nodeId_, otherNode_, uniqueLevel_=-1):
		thisNode = self
		thisParrentNode = thisNode

		# Find subNode with specified nodeId
		thisParrentNode = ""
		ix = 0
		for node in thisNode.parrentNode_.subNodes_:
			# is This the node we are looking for?
			if(node.nodeId_.lower() == nodeId_.lower()):
				thisParrentNode = node.parrentNode_
				thisNode = node
				break

		# was the node found?
		if(thisParrentNode == ""):
			# NO
			self.error_ = "replaceSubNodeObjById: Unable to find node with Id " + nodeId_			 
			return self

		# Auto discover item type and update thisNode uniquenessLevel
		# Is this parrentNode a dict object?
		if thisParrentNode.isOrderedDict():
			#Y => Set uniqunessLevel to peerNode uniqueness since a dict cannot contain duplicate keys
			uniqueLevel_ = 2

		# Has uniquenessLevel been specified?
		if uniqueLevel_ < 0:
			#N => Use/Enerit thisNodes
			uniqueLevel_ = self.uniqueLevel_		
		
		# Is node->value unique?
		# Is it infoTree Uniqueness?
		if(uniqueLevel_ == 1):
			# Does this node allready exist?
			thisRootNode = thisNode.getRootNode()
			existingNode = thisRootNode.findNodeByValue(otherSubNode_.item_)
			if(existingNode != ""):
				# Node exit just update frequency "match count"
				existingNode.freq_ += 1
				return self
		# Is it peerNode Uniqueness?
		if(uniqueLevel_ == 2):
			# Does this node allready exist as a peerNode?
			existingNode = thisNode.findPeerNodeByValue(otherSubNode_.item_)
			if(existingNode != ""):
				# Node exist just update frequency "match count"
				existingNode.freq_ += 1
				return self
		# Is it subNode Uniqueness?
		if(uniqueLevel_ == 3):
			# Does this node allready exist as a subNode?
			existingNode = thisNode.findSubNodeByValue(otherSubNode_.item_)
			if(existingNode != ""):
				# Node exist just update freq "match count"
				existingNode.freq_ += 1
				return self
		# Is it sub-infoTree Uniqueness
		if(uniqueLevel_ == 4):
			# Does this node allready exist as a subNode?
			existingNode = thisNode.findNodeByValue(otherSubNode_.item_)
			if(existingNode != ""):
				# Node exist just update freq "match count"
				existingNode.freq_ += 1
				return self

		# Get subNode specifed by Ix
		ix = thisNode.nodeIx_

		# fix/Ensure the otherSubNode_ is associated/linked to thisNodes Parrent before the replace
		otherNode_.parrentNode_ = thisParrentNode
		# Ensure the otherSubNode has the specified uniqueness level
		otherNode_.uniqueLevel_ = uniqueLevel_		 

		# Replacse thisSubNode with otherSubNode
		thisNode.subNodes_[ix] = otherNode_

		# Fix thisSubNodes sub-infoTree association/linking to parrentNode
		for node in thisParrentNode.subNodes_[ix].subNodes_:
			# fix subNodes association/link to parrentNode
			node.parrentNode_ = thisNode
				
		# Fix thisSubNode & its sub-infoTree nodeIds
		thisNode.subNodes_[ix].updateSubinfoTreeNodeIds()

		# Auto discover item type and update this parrentNodes json object structure "sub-infoTree"
		# Is this parrentNode a dict object?
		if thisParrentNode.isOrderedDict():
			#Y => Replace with new dict item, replace not supported for dicts so we must recreate the sub-infoTree of all nodes after the ref node
			thisParrentNode.replaceDictItemByKey(thisNode.name_, otherNode_.name_, otherNode_.item_)

		# Is this parrentNode a list Object?
		if thisParrentNode.isList():
			#Y => Replace thisItem with otherItem
			thisParrentNode.item_.replace(thisNode.nodeIx_, otherNode_.item_)
			
		# Update new nodes sub-infoTree to reflect its json object structure
		#otherSubNode_.setValue()					

		return thisNode.subNodes_[ix]

	# replace thisNodes subNode specified by name with the otherSubNode, Search in thisNode subNodes
	def replaceSubNodeObjByName(self, name_, otherNode_, uniqueLevel_=-1):
		thisNode = self
		thisParrentNode = thisNode

		# Find subNode with specified nodeId
		thisParrentNode = ""
		ix = 0
		for node in thisNode.parrentNode_.subNodes_:
			# is This the node we are looking for?
			if(node.name_.lower() == name_.lower()):
				thisParrentNode = node.parrentNode_
				thisNode = node
				break

		# was the node found?
		if(thisParrentNode == ""):
			# NO
			self.error_ = "replaceSubNodeObjByName: Unable to find node with name " + name_			   
			return self

		# Auto discover item type and update thisNode uniquenessLevel
		# Is this parrentNode a dict object?
		if thisParrentNode.isOrderedDict():
			#Y => Set uniqunessLevel to peerNode uniqueness since a dict cannot contain duplicate keys
			uniqueLevel_ = 2

		# Has uniquenessLevel been specified?
		if uniqueLevel_ < 0:
			#N => Use/Enerit thisNodes
			uniqueLevel_ = self.uniqueLevel_		
		
		# Is node->value unique?
		# Is it infoTree Uniqueness?
		if(uniqueLevel_ == 1):
			# Does this node allready exist?
			thisRootNode = thisNode.getRootNode()
			existingNode = thisRootNode.findNodeByValue(otherNode_.item_)
			if(existingNode != ""):
				# Node exit just update frequency "match count"
				existingNode.freq_ += 1
				return self
		# Is it peerNode Uniqueness?
		if(uniqueLevel_ == 2):
			# Does this node allready exist as a peerNode?
			existingNode = thisNode.findPeerNodeByValue(otherNode_.item_)
			if(existingNode != ""):
				# Node exist just update frequency "match count"
				existingNode.freq_ += 1
				return self
		# Is it subNode Uniqueness?
		if(uniqueLevel_ == 3):
			# Does this node allready exist as a subNode?
			existingNode = thisNode.findSubNodeByValue(otherNode_.item_)
			if(existingNode != ""):
				# Node exist just update freq "match count"
				existingNode.freq_ += 1
				return self
		# Is it sub-infoTree Uniqueness
		if(uniqueLevel_ == 4):
			# Does this node allready exist as a subNode?
			existingNode = thisNode.findNodeByValue(otherNode_.item_)
			if(existingNode != ""):
				# Node exist just update freq "match count"
				existingNode.freq_ += 1
				return self
		
		# Get subNode specified by Ix
		ix = thisNode.nodeIx_
		thisNode = thisParrentNode.subNodes_[ix]

		# fix/Ensure the otherSubNode_ is associated/linked to thisNodes Parrent before the replace
		otherNode_.parrentNode_ = thisParrentNode
		# Ensure the otherSubNode has the specified uniqueness level
		otherNode_.uniqueLevel_ = uniqueLevel_		 

		# Replacse thisSubNode with otherSubNode
		thisParrentNode.subNodes_[ix] = otherNode_		  

		# Fix thisSubNodes sub-infoTree association/linking to parrentNode
		for node in thisParrentNode.subNodes_[ix].subNodes_:
			# fix subNodes association/link to parrentNode
			node.parrentNode_ = thisNode
				
		# Fix thisSubNode & its sub-infoTree nodeIds
		thisParrentNode.subNodes_[ix].updateSubinfoTreeNodeIds()

		# Auto discover item type and update this parrentNodes json object structure "sub-infoTree"
		# Is this parrentNode a dict object?
		if thisParrentNode.isOrderedDict():
			#Y => Replace with new dict item, replace not supported for dicts so we must recreate the sub-infoTree of all nodes after the ref node
			thisParrentNode.replaceDictItemByKey(thisNode.name_, otherNode_.name_, otherNode_.item_)

		# Is this parrentNode a list Object?
		if thisParrentNode.isList():
			#Y => Replace thisItem with otherItem
			thisParrentNode.item_.replace(thisNode.nodeIx_, otherNode_.item_)

		# Update new nodes sub-infoTree to reflect its json object structure
		#otherSubNode_.setValue()					

		return thisParrentNode.subNodes_[ix]

	# replace thisNodes subNode specified by nodeIx with the otherSubNode, Search in thisNodes subNodes
	def replaceSubNodeObjByIx(self, nodeIx_, otherNode_, uniqueLevel_=-1):
		thisNode = self
		thisParrentNode = thisNode

		# Find node specified by ix
		# Is this nodeIx_ valid?
		if nodeIx_ < 0 or nodeIx_ > thisParrentNode.lastSubNodeIx_:
			#N => Signal attempt to insert peern node at invalid ix
			self.error_ = "replaceSubNodeObjByIx: last subNode Ix of parrenNode " + thisParrentNode.name_ + " is "+ thisParrentNode.lastSubNodeIx_ + ", hence nodeIx " + str(nodeIx_) + " is not a valid ix"
			return self			

		# Auto discover item type and update thisNode uniquenessLevel
		# Is this parrentNode a dict object?
		if thisParrentNode.isOrderedDict():
			#Y => Set uniqunessLevel to peerNode uniqueness since a dict cannot contain duplicate keys
			uniqueLevel_ = 2		

		# Has uniquenessLevel been specified?
		if uniqueLevel_ < 0:
			#N => Use/Enerit thisNodes
			uniqueLevel_ = self.uniqueLevel_		
		
		# Is node->value unique?
		# Is it infoTree Uniqueness?
		if(uniqueLevel_ == 1):
			# Does this node allready exist?
			thisRootNode = thisNode.getRootNode()
			existingNode = thisRootNode.findNodeByValue(otherSubNode_.item_)
			if(existingNode != ""):
				# Node exit just update frequency "match count"
				existingNode.freq_ += 1
				return self
		# Is it peerNode Uniqueness?
		if(uniqueLevel_ == 2):
			# Does this node allready exist as a peerNode?
			existingNode = thisNode.findPeerNodeByValue(otherSubNode_.item_)
			if(existingNode != ""):
				# Node exist just update frequency "match count"
				existingNode.freq_ += 1
				return self
		# Is it subNode Uniqueness?
		if(uniqueLevel_ == 3):
			# Does this node allready exist as a subNode?
			existingNode = thisNode.findSubNodeByValue(otherSubNode_.item_)
			if(existingNode != ""):
				# Node exist just update freq "match count"
				existingNode.freq_ += 1
				return self
		# Is it sub-infoTree Uniqueness
		if(uniqueLevel_ == 4):
			# Does this node allready exist as a subNode?
			existingNode = thisNode.findNodeByValue(otherSubNode_.item_)
			if(existingNode != ""):
				# Node exist just update freq "match count"
				existingNode.freq_ += 1
				return self

		# get subNode specified by ix
		thisNode = thisParrentNode.subNodes_[nodeIx_]

		# fix/Ensure the otherSubNode_ is associated/linked to thisNodes Parrent before the replace
		otherNode_.parrentNode_ = thisParrentNode
		# Ensure the otherSubNode has the specified uniqueness level
		otherNode_.uniqueLevel_ = uniqueLevel_

		# Replacse thisSubNode with otherSubNode
		thisParrentNode.subNodes_[nodeIx_] = otherNode_

		# Fix thisSubNodes sub-infoTree association/linking to parrentNode
		for node in thisParrentNode.subNodes_[nodeIx_].subNodes_:
			# fix subNodes association/link to parrentNode
			node.parrentNode_ = thisNode
				
		# Fix thisSubNode & its sub-infoTree nodeIds
		thisParrentNode.subNodes_[nodeIx_].updateSubinfoTreeNodeIds()

		# Auto discover item type and update this parrentNodes json object structure "sub-infoTree"
		# Is this parrentNode a dict object?
		if thisParrentNode.isOrderedDict():
			#Y => Has this key allready been added?
			if not otherNode_.name_ in thisParrentNode.item_.keys():
				#N => Replace with new dict item, replace not supported for dicts so we must recreate the sub-infoTree of all nodes after the ref node
				thisParrentNode.replaceDictItemByKey(thisNode.name_, otherNode_.name_, otherNode_.item_)

		# Is this parrentNode a list Object?
		if thisParrentNode.isList():
			#Y => Replace thisItem with otherItem
			thisParrentNode.item_.replace(thisNode.nodeIx_, otherNode_.item_)

		# Update new nodes sub-infoTree to reflect its json object structure
		#otherSubNode_.setValue()					

		return thisParrentNode.subNodes_[nodeIx_]				  

	# replace thisNodes subNode specified by value with the otherSubNode, Search in thisNode subNodes
	def replaceSubNodeObjByValue(self, value_, otherNode_, uniqueLevel_=-1):
		thisNode = self
		thisParrentNode = thisNode

		# Find subNode with specified nodeId
		thisParrentNode = ""
		ix = 0
		for node in thisNode.parrentNode_.subNodes_:
			# Is this the node we are looking for?
			# Is thisNode and value a ordered dict object
			if node.isOrderedDict() and node.isOrderedDict(value_):
				#Y => Is this the value we are looking for
				if node.item_ == value_:
					#Y
					thisParrentNode = thisNode
					thisNode = node
					break

			# Is thisNode and value a list object
			if thisNode.isList() and thisNode.isList(value_):
				#Y => Is this the value we are looking for
				if thisNode.item_ == value_:
					#Y
					thisParrentNode = thisNode
					thisNode = node
					break					

			# Is thisNode and value a string
			if thisNode.isString() and thisNode.isString(value_):
				#Y => Is this the value we are looking for
				if(thisNode.item_.lower() == value_.lower()):
					#Y
					thisParrentNode = thisNode
					thisNode = node
					break

			# Is thisNode and value a number
			if thisNode.isNumber() and thisNode.isNumber(value_):
				#Y => Is this the value we are looking for
				if thisNode.item_ == value_:
					#Y
					thisParrentNode = thisNode
					thisNode = node
					break

		# was the node found?
		if(thisParrentNode == ""):
			# NO
			self.error_ = "replaceSubNodeObjByValue: Unable to find node with value " + self.getString(value_)			   
			return self

		# Auto discover item type and update thisNode uniquenessLevel
		# Is this parrentNode a dict object?
		if thisParrentNode.isOrderedDict():
			#Y => Set uniqunessLevel to peerNode uniqueness since a dict cannot contain duplicate keys
			uniqueLevel_ = 2

		# Has uniquenessLevel been specified?
		if uniqueLevel_ < 0:
			#N => Use/Enerit thisNodes
			uniqueLevel_ = self.uniqueLevel_		
		
		# Is node->value unique?
		# Is it infoTree Uniqueness?
		if(uniqueLevel_ == 1):
			# Does this node allready exist?
			thisRootNode = thisNode.getRootNode()
			existingNode = thisRootNode.findNodeByValue(otherSubNode_.item_)
			if(existingNode != ""):
				# Node exit just update frequency "match count"
				existingNode.freq_ += 1
				return self
		# Is it peerNode Uniqueness?
		if(uniqueLevel_ == 2):
			# Does this node allready exist as a peerNode?
			existingNode = thisNode.findPeerNodeByValue(otherSubNode_.item_)
			if(existingNode != ""):
				# Node exist just update frequency "match count"
				existingNode.freq_ += 1
				return self
		# Is it subNode Uniqueness?
		if(uniqueLevel_ == 3):
			# Does this node allready exist as a subNode?
			existingNode = thisNode.findSubNodeByValue(otherSubNode_.item_)
			if(existingNode != ""):
				# Node exist just update freq "match count"
				existingNode.freq_ += 1
				return self
		# Is it sub-infoTree Uniqueness
		if(uniqueLevel_ == 4):
			# Does this node allready exist as a subNode?
			existingNode = thisNode.findNodeByValue(otherSubNode_.item_)
			if(existingNode != ""):
				# Node exist just update freq "match count"
				existingNode.freq_ += 1
				return self
		
		# Get subNode specified by Ix
		ix = thisNode.nodeIx_

		# fix/Ensure the otherSubNode_ is associated/linked to thisNodes Parrent before the replace
		otherNode_.parrentNode_ = thisParrentNode
		# Ensure the otherSubNode has the specified uniqueness level
		otherNode_.uniqueLevel_ = uniqueLevel_		 

		# Replacse thisSubNode with otherSubNode
		thisParrentNode.subNodes_[ix] = otherNode_		  

		# Fix thisSubNodes sub-infoTree association/linking to parrentNode
		for node in thisParrentNode.subNodes_[ix].subNodes_:
			# fix subNodes association/link to parrentNode
			node.parrentNode_ = thisNode
				
		# Fix thisSubNode & its sub-infoTree nodeIds
		thisParrentNode.subNodes_[ix].updateSubinfoTreeNodeIds()

		# Auto discover item type and update this parrentNodes json object structure "sub-infoTree"
		# Is this parrentNode a dict object?
		if thisParrentNode.isOrderedDict():
			#Y => Replace with new dict item, replace not supported for dicts so we must recreate the sub-infoTree of all nodes after the ref node
			thisParrentNode.replaceDictItemByKey(thisNode.name_, otherNode_.name_, otherNode_.item_)

		# Is this parrentNode a list Object?
		if thisParrentNode.isList():
			#Y => Replace thisItem with otherItem
			thisParrentNode.item_.replace(thisNode.nodeIx_, otherNode_.item_)

		# Update new nodes sub-infoTree to reflect its json object structure
		#otherSubNode_.setValue()					

		return thisParrentNode.subNodes_[ix]

	# Replace thisNodes subNode specified by nodeIx with copy of otherSubNode
	def replaceSubNodeObjCopy(self, nodeIx_, otherNode_, uniqueLevel_=-1):
		thisNode = self
		thisParrentNode = thisNode

		# Find node specified by ix
		# Is this nodeIx_ valid?
		if nodeIx_ < 0 or nodeIx_ > thisParrentNode.lastSubNodeIx_:
			#N => Signal attempt to insert peern node at invalid ix
			self.error_ = "replaceSubNodeObjByIx: last subNode Ix of parrenNode " + thisParrentNode.name_ + " is "+ thisParrentNode.lastSubNodeIx_ + ", hence nodeIx " + str(nodeIx_) + " is not a valid ix"
			return self			

		# Auto discover item type and update thisNode uniquenessLevel
		# Is this parrentNode a dict object?
		if thisParrentNode.isOrderedDict():
			#Y => Set uniqunessLevel to peerNode uniqueness since a dict cannot contain duplicate keys
			uniqueLevel_ = 2		

		# Has uniquenessLevel been specified?
		if uniqueLevel_ < 0:
			#N => Use/Enerit thisNodes
			uniqueLevel_ = self.uniqueLevel_		

		# Is node->value unique?
		# Is it infoTree Uniqueness?
		if(uniqueLevel_ == 1):
			# Does this node allready exist?
			thisRootNode = thisNode.getRootNode()
			existingNode = thisRootNode.findNodeByValue(otherSubNode_.item_)
			if(existingNode != ""):
				# Node exit just update frequency "match count"
				existingNode.freq_ += 1
				return self
		# Is it peerNode Uniqueness?
		if(uniqueLevel_ == 2):
			# Does this node allready exist as a peerNode?
			existingNode = thisNode.findPeerNodeByValue(otherSubNode_.item_)
			if(existingNode != ""):
				# Node exist just update frequency "match count"
				existingNode.freq_ += 1
				return self
		# Is it subNode Uniqueness?
		if(uniqueLevel_ == 3):
			# Does this node allready exist as a subNode?
			existingNode = thisNode.findSubNodeByValue(otherSubNode_.item_)
			if(existingNode != ""):
				# Node exist just update freq "match count"
				existingNode.freq_ += 1
				return self
		# Is it sub-infoTree Uniqueness
		if(uniqueLevel_ == 4):
			# Does this node allready exist as a subNode?
			existingNode = thisNode.findNodeByValue(otherSubNode_.item_)
			if(existingNode != ""):
				# Node exist just update freq "match count"
				existingNode.freq_ += 1
				return self		   
		
		# Create copy of otherSubNode
		otherNode = otherNode_.copyNodeObj()
		# Get subNode specified by ix
		thisNode = thisParrentNode.subNodes_[nodeIx_]

		# fix/Ensure the otherSubNode_ is associated/linked to thisNodes Parrent before the replace
		otherNode.parrentNode_ = thisParrentNode
		# Ensure the otherSubNode has the specified uniqueness level
		otherNode.uniqueLevel_ = uniqueLevel_		 

		# Replacse thisSubNode with otherSubNode
		thisParrentNode.subNodes_[nodeIx_] = otherNode

		# Fix thisSubNodes sub-infoTree association/linking to parrentNode
		for node in thisParrentNode.subNodes_[nodeIx_].subNodes_:
			# fix subNodes association/link to parrentNode
			node.parrentNode_ = thisNode
				
		# Fix thisSubNode & its sub-infoTree nodeIds
		thisParrentNode.subNodes_[nodeIx_].updateSubinfoTreeNodeIds()

		# Auto discover item type and update this parrentNodes json object structure "sub-infoTree"
		# Is this parrentNode a dict object?
		if thisParrentNode.isOrderedDict():
			#Y => Replace with new dict item, replace not supported for dicts so we must recreate the sub-infoTree of all nodes after the ref node
			thisParrentNode.replaceDictItemByKey(thisNode.name_, otherNode.name_, otherNode.item_)

		# Is this parrentNode a list Object?
		if thisParrentNode.isList():
			#Y => Replace thisItem with otherItem
			thisParrentNode.item_.replace(thisNode.nodeIx_, otherNode.item_)

		# Update new nodes sub-infoTree to reflect its json object structure
		#otherSubNode_.setValue()					

		return thisParrentNode.subNodes_[nodeIx_]
#-----------------------------------
#--------------------- REPLACE Helper/Wrapper Methods -----------------
# TODO: IMPLEMENT THEM!!
#----------- Replace Helper/Wrapper Methods -----------------------------
#----------- Replace Node Helper/Wrapper methods (Search from thisNode to end of sub-infoTree)-----------------
# Build to search entire sub-infoTree of thisNode
	# replace thisNode with the otherNode
	# STATUS:
	def replaceNode(self, name_="", item_="", uniqueLevel_=-1):
		thisNode = self

		# Create new node
		newNode = jsonNode(name_, item_, thisNode.parrentNode_, thisNode.nodeLevelSeparator_)

		# Was the new node created?
		if newNode.error_ != "":
			#N => Signal failed to add new subNode
			self.error_ = "replaceNode: Failed to Create jsonNode: " + newNode.error_
			return self

		# Insert the new node as after thisNode 
		thisNode = thisNode.replaceNodeObj(newNode, uniqueLevel_)

		# Update new nodes sub-infoTree to reflect its json object structure
		thisNode.setValue()		

		return thisNode
	
	# replace node specified by Id with otherNode, Search from thisNode to end of its sub-infoTree
	# use rootNode if you are unsure where the node is located
	def replaceNodeById(self, nodeId_, name_="", item_="", uniqueLevel_=-1, startNode_ = ""):
		thisNode = self

		# Create new node
		newNode = jsonNode(name_, item_, thisNode.parrentNode_, thisNode.nodeLevelSeparator_)

		# Was the new node created?
		if newNode.error_ != "":
			#N => Signal failed to add new subNode
			self.error_ = "replaceNodeById: Failed to Create jsonNode: " + newNode.error_
			return self

		# Insert the new node after node specified by id
		thisNode = thisNode.replaceNodeObjById(nodeId_, newNode, uniqueLevel_, startNode_)

		# Update new nodes sub-infoTree to reflect its json object structure
		thisNode.setValue()		

		return thisNode

	# replace node specified by name with otherNode, relative search from thisNode to end of its sub-infoTree
	# use rootNode if you are unsure where the node is located
	def replaceNodeByName(self, nodeName_, name_="", item_="", uniqueLevel_=-1, startNode_ = ""):
		thisNode = self

		# Create new node
		newNode = jsonNode(name_, item_, thisNode.parrentNode_, thisNode.nodeLevelSeparator_)
		
		# Was the new node created?
		if newNode.error_ != "":
			#N => Signal failed to add new subNode
			self.error_ = "replaceNodeByName: Failed to Create jsonNode: " + newNode.error_
			return self		

		# Insert the new node after node specified by name
		thisNode = thisNode.replaceNodeObjByName(nodeName_, newNode, uniqueLevel_, startNode_)

		# Update new nodes sub-infoTree to reflect its json object structure
		thisNode.setValue()		

		return thisNode

	# replace node specified by value with otherNode, relative search from thisNode to end of its sub-infoTree
	# use rootNode if you are unsure where the node is located
	def replaceNodeByValue(self, value_, name_="", item_="", uniqueLevel_=-1, startNode_ = ""):
		thisNode = self

		# Create new node
		newNode = jsonNode(name_, item_, thisNode.parrentNode_, thisNode.nodeLevelSeparator_)
		
		# Was the new node created?
		if newNode.error_ != "":
			#N => Signal failed to add new subNode
			self.error_ = "replaceNodeByValue: Failed to Create jsonNode: " + newNode.error_
			return self		

		# Insert the new node after node specified by value
		thisNode = thisNode.replaceNodeObjByValue(value_, newNode, uniqueLevel_, startNode_)

		# Update new nodes sub-infoTree to reflect its json object structure
		thisNode.setValue()		

		return thisNode

# -------------- Insert peerNode Helper/Wrapper methods (Search in thisNodes peerNodes) ----------------
# Build to search only peerNodes, parrentNode->subNodes/nodeChain

	# Replace peerNodeObj on same parrentNode/nodeChain as thisNode & relative to "after" thisNode
	def replacePeerNode(self, name_="", item_="", uniqueLevel_=-1):
		thisNode = self

		# Create new node
		newNode = jsonNode(name_, item_, thisNode.parrentNode_, thisNode.nodeLevelSeparator_)

		# Was the node created?
		if newNode.error_ != "":
			#N => Signal failed to add new subNode
			self.error_ = "insertPeerNode: Failed to Create jsonNode: " + newNode.error_
			return self		

		# Insert the new node rel to thisNode
		thisNode = thisNode.replacePeerNodeObj(newNode, uniqueLevel_)

		# Update new nodes sub-infoTree to reflect its json object structure
		thisNode.setValue()		

		return thisNode

	# replace thisNodes peerNode specified by nodeId with the otherNode, Search in thisNode peerNodes
	# use rootNode if you are unsure where the node is located
	def replacePeerNodeById(self, nodeId_, name_="", item_="", uniqueLevel_=-1):
		thisNode = self

		# Create new node
		newNode = jsonNode(name_, item_, thisNode.parrentNode_, thisNode.nodeLevelSeparator_)

		# Was the node created?
		if newNode.error_ != "":
			#N => Signal failed to add new subNode
			self.error_ = "replacePeerNodeById: Failed to Create jsonNode: " + newNode.error_
			return self		

		# Insert the new peerNode rel to thisNode
		thisNode = thisNode.replacePeerNodeObjById(nodeId_, newNode, uniqueLevel_)

		# Update new nodes sub-infoTree to reflect its json object structure
		thisNode.setValue()		

		return thisNode

	# Replace peerNode (by value) relative to "After" Node Specified by name, Search in thisNodes peerNodes
	# use rootNode if you are unsure where the node is located
	def replacePeerNodeByName(self, nodeName_, name_="", item_="", uniqueLevel_=-1):
		thisNode = self

		# Create new node
		newNode = jsonNode(name_, item_, thisNode.parrentNode_, thisNode.nodeLevelSeparator_)

		# Was the node created?
		if newNode.error_ != "":
			#N => Signal failed to add new subNode
			self.error_ = "replacePeerNodeByName: Failed to Create jsonNode: " + newNode.error_
			return self		

		# Insert the new node rel to node specified by name
		thisNode = thisNode.replacePeerNodeObjByName(nodeName_, newNode, uniqueLevel_)

		# Update new nodes sub-infoTree to reflect its json object structure
		thisNode.setValue()		

		return thisNode

	# replace thisNodes peerNode specified by nodeIx with the otherNode, Search in thisNodes peerNodes
	# use rootNode if you are unsure where the node is located
	def replacePeerNodeByIx(self, nodeIx_, name_="", item_="", uniqueLevel_=-1):
		thisNode = self

		# Create new node
		newNode = jsonNode(name_, item_, thisNode.parrentNode_, thisNode.nodeLevelSeparator_)

		# Was the node created?
		if newNode.error_ != "":
			#N => Signal failed to add new subNode
			self.error_ = "replacePeerNodeByIx: Failed to Create jsonNode: " + newNode.error_
			return self		

		# Insert the new peerNode rel to thisNode
		thisNode = thisNode.replacePeerNodeObjByIx(nodeIx_, newNode, uniqueLevel_)

		# Update new nodes sub-infoTree to reflect its json object structure
		thisNode.setValue()		

		return thisNode		   

	# replace thisNodes peerNode specified by value with the otherNode, Search in thisNode peerNodes
	# use rootNode if you are unsure where the node is located
	def replacePeerNodeByValue(self, value_, name_="", item_="", uniqueLevel_=-1):
		thisNode = self

		# Create new node
		newNode = jsonNode(name_, item_, thisNode.parrentNode_, thisNode.nodeLevelSeparator_)

		# Was the node created?
		if newNode.error_ != "":
			#N => Signal failed to add new subNode
			self.error_ = "replacePeerNodeByValue: Failed to Create jsonNode: " + newNode.error_
			return self		

		# Insert the new node rel. after node specified by value
		thisNode = thisNode.replacePeerNodeObjByValue(value_, newNode, uniqueLevel_)

		# Update new nodes sub-infoTree to reflect its json object structure
		thisNode.setValue()		

		return thisNode

#-------------- Insert subNode Helper methods (Search in thisNodes subNodes) ---------------------
# Build to search only thisNodes->subNodes/nodeChain	 
	# replace thisNodes subNode specified by Ix with the otherNode sub-infoTree, Search in thisNodes subNodes
	def replaceSubNode(self, nodeIx_, name_="", item_="", uniqueLevel_=-1):
		thisNode = self
		
		# Create new node
		newNode = jsonNode(name_, item_, thisNode, thisNode.nodeLevelSeparator_)

		# Was the node created?
		if newNode.error_ != "":
			#N => Signal failed to add new subNode
			self.error_ = "replaceSubNode: Failed to Create jsonNode: " + newNode.error_
			return self		

		# Insert the new node rel. after node specified by ix
		thisNode = thisNode.replaceSubNodeObj(nodeIx_, newNode, uniqueLevel_)

		# Update new nodes sub-infoTree to reflect its json object structure
		thisNode.setValue()		

		return thisNode

	# replace thisNodes sub-infoTree with the otherNodes sub-infoTree "replace nodeChain"
	def replaceSubinfoTree(self, name_="", item_=""):
		thisNode = self
		
		# Create new node
		newNode = jsonNode(name_, item_, thisNode, thisNode.nodeLevelSeparator_)
		newNode.setValue()

		# Was the node created?
		if newNode.error_ != "":
			#N => Signal failed to add new subNode
			self.error_ = "replaceSubinfoTree: Failed to Create jsonNode: " + newNode.error_
			return self		

		# Insert the new node rel. after node specified by ix
		thisNode = thisNode.replaceSubinfoTreeObj(newNode)

		# Update new nodes sub-infoTree to reflect its json object structure
		thisNode.setValue()		

		return thisNode		
	
	# replace thisNodes subNode specified by nodeId with the otherSubNode, Search in thisNode subNodes
	# use rootNode if you are unsure where the node is located
	def replaceSubNodeById(self, nodeId_, name_="", item_="", uniqueLevel_=-1):
		thisNode = self
		
		# Create new subNode "Dont worry about parrentNode it is fixed by the core add subnode method"
		newNode = jsonNode(name_, item_, thisNode, thisNode.nodeLevelSeparator_)

		# Was the node created?
		if newNode.error_ != "":
			#N => Signal failed to add new subNode
			self.error_ = "replaceSubNodeById: Failed to Create jsonNode: " + newNode.error_
			return self		

		# Insert the new Node rel. after node specified by id
		thisNode = thisNode.replaceSubNodeObjById(nodeId_, newNode, uniqueLevel_)

		# Update new nodes sub-infoTree to reflect its json object structure
		thisNode.setValue()		

		return thisNode

	# replace sub-infoTree of node specified by Id with otherNode sub-infoTree, Search from thisNode to end of its sub-infoTree
	# use rootNode if you are unsure where the node is located
	def replaceSubinfoTreeById(self, nodeId_, name_="", item_="", uniqueLevel_=-1, startNode_ = ""):
		thisNode = self
		
		# Create new subNode "Dont worry about parrentNode it is fixed by the core add subnode method"
		newNode = jsonNode(name_, item_, thisNode, thisNode.nodeLevelSeparator_)
		newNode.setValue()

		# Was the node created?
		if newNode.error_ != "":
			#N => Signal failed to add new subNode
			self.error_ = "replaceSubinfoTreeById: Failed to Create jsonNode: " + newNode.error_
			return self		

		# Insert the new Node rel. after node specified by id
		thisNode = thisNode.replaceSubinfoTreeObjById(nodeId_, newNode, uniqueLevel_, startNode_)

		# Update new nodes sub-infoTree to reflect its json object structure
		thisNode.setValue()		

		return thisNode		

	# replace thisNodes subNode specified by name with the otherSubNode, Search in thisNode subNodes
	# use rootNode if you are unsure where the node is located
	def replaceSubNodeByName(self, nodeName_, name_="", item_="", uniqueLevel_=-1):
		thisNode = self

		# Create new subNode
		newNode = jsonNode(name_, item_, thisNode, thisNode.nodeLevelSeparator_)

		# Was the node created?
		if newNode.error_ != "":
			#N => Signal failed to add new subNode
			self.error_ = "replaceSubNodeByName: Failed to Create jsonNode: " + newNode.error_
			return self		

		# Insert the new Node rel. after node specified by name
		thisNode = thisNode.replaceSubNodeObjByName(nodeName_, newNode, uniqueLevel_)

		# Update new nodes sub-infoTree to reflect its json object structure
		thisNode.setValue()		

		return thisNode

	# replace sub-infoTree of node specified by name with otherNode sub-infoTree, relative search from thisNode to end of its sub-infoTree
	# use rootNode if you are unsure where the node is located
	def replaceSubinfoTreeByName(self, nodeName_, name_="", item_="", uniqueLevel_=-1, startNode_ = ""):
		thisNode = self
		
		# Create new subNode "Dont worry about parrentNode it is fixed by the core add subnode method"
		newNode = jsonNode(name_, item_, thisNode, thisNode.nodeLevelSeparator_)
		newNode.setValue()

		# Was the node created?
		if newNode.error_ != "":
			#N => Signal failed to add new subNode
			self.error_ = "replaceSubinfoTreeByName: Failed to Create jsonNode: " + newNode.error_
			return self		

		# Insert the new Node rel. after node specified by id
		thisNode = thisNode.replaceSubinfoTreeObjByName(nodeName_, newNode, uniqueLevel_, startNode_)

		# Update new nodes sub-infoTree to reflect its json object structure
		thisNode.setValue()		

		return thisNode		

	# replace thisNodes subNode specified by nodeIx with the otherSubNode, Search in thisNodes subNodes
	# use rootNode if you are unsure where the node is located
	def replaceSubNodeByIx(self, nodeIx_, name_="", item_="", uniqueLevel_=-1):
		thisNode = self
		
		# Create new subNode "Dont worry about parrentNode it is fixed by the core add subnode method"
		newNode = jsonNode(name_, item_, thisNode, thisNode.nodeLevelSeparator_)

		# Was the node created?
		if newNode.error_ != "":
			#N => Signal failed to add new subNode
			self.error_ = "replaceSubNodeByIx: Failed to Create jsonNode: " + newNode.error_
			return self		

		# Replace the new Node rel. after node specfied by ix
		thisNode = thisNode.replaceSubNodeObjByIx(nodeIx_, newNode, uniqueLevel_)

		# Update new nodes sub-infoTree to reflect its json object structure
		thisNode.setValue()		

		return thisNode		   

	# replace thisNodes subNode specified by value with the otherSubNode, Search in thisNode subNodes
	# use rootNode if you are unsure where the node is located
	def replaceSubNodeByValue(self, value_, name_="", item_="", uniqueLevel_=-1):
		thisNode = self

		# Create new subNode
		newNode = jsonNode(name_, item_, thisNode, thisNode.nodeLevelSeparator_)

		# Was the node created?
		if newNode.error_ != "":
			#N => Signal failed to add new subNode
			self.error_ = "replaceSubNodeByValue: Failed to Create jsonNode: " + newNode.error_
			return self		

		# Replace the new Node rel. after node specfied by value
		thisNode = thisNode.replaceSubNodeObjByValue(value_, newNode, uniqueLevel_)

		# Update new nodes sub-infoTree to reflect its json object structure
		thisNode.setValue()		

		return thisNode	
		
	# replace sub-infoTree of node specified by value with otherNode sub-infoTree, relative search from thisNode to end of its sub-infoTree
	# use rootNode if you are unsure where the node is located
	def replaceSubinfoTreeByValue(self, value_, name_="", item_="", uniqueLevel_=-1, startNode_ = ""):
		thisNode = self
		
		# Create new subNode "Dont worry about parrentNode it is fixed by the core add subnode method"
		newNode = jsonNode(name_, item_, thisNode, thisNode.nodeLevelSeparator_)
		newNode.setValue()

		# Was the node created?
		if newNode.error_ != "":
			#N => Signal failed to add new subNode
			self.error_ = "replaceSubinfoTreeByValue: Failed to Create jsonNode: " + newNode.error_
			return self		

		# Insert the new Node rel. after node specified by id
		thisNode = thisNode.replaceSubinfoTreeObjByValue(value_, newNode, uniqueLevel_, startNode_)

		# Update new nodes sub-infoTree to reflect its json object structure
		thisNode.setValue()		

		return thisNode			
#-------------------------------------------------


#-------- link/relation to method -------
	# Method to attach/link thisNode to a specfied parrentNode as new last childNode
	# STATUS: NOT IMPLEMENTED AND POT. UNRQUIRED
	def linkNode(self, parrentNode_):
		thisNode = self

		# Does thisNode allready have a parrentNode?
		#**if thisNode.parrentNode_ != "":
			#Y => move the node to new parrentNode

		# Link this childNode to specified parrentNode
		thisNode.parrentNode_ = parrentNode_

		# Link thisItem to to specified parrentItem as new last childItem

		# Is new parrentNode a orderedDict
		#if parrentNode_.isOrdereddDict():
			#Y =>

# -------- Move node Helper/Warpper Methods (Search from thisNode to end of sub-infoTree) -----
# Methods used to move nodes around between parrentNodes "Global move"
	# move thisNode to other parrentNode relative search from thisNode
	# Search thisNode sub-infoTree unless startNode is specified	
	def moveNode(self, otherParrentNode_, uniqueLevel_=-1):
		thisNode = self
		
		# Create copy of thisNode
		movedNode = thisNode.copyNodeObj()

		# Add node to new parrent
		otherParrentNode_.addSubNodeObj(movedNode)

		# Remove the node from old parrent
		thisNode.removeNodeObj()

		# Update new nodes sub-infoTree to reflect its json object structure
		movedNode.setValue()		

		return movedNode

	# move Node specified by Id to other parrentNode relative search from thisNode 
	# Search thisNode sub-infoTree unless startNode is specified
	def moveNodeById(self, nodeId_, otherParrentNode_, uniqueLevel_=-1, startNode_ = ""):
		thisNode = self
		
		# Find specified node node
		thisNode = thisNode.getNodeById(nodeId_,uniqueLevel_, startNode_)

		# Was a valid node found?
		if thisNode == "":
			#N =>signal failed to move
			self.error_ = "moveNodeById: Cannot find node with id " + nodeId_
			return self

		# Create copy of thisNode
		movedNode = thisNode.copyNodeObj()

		# Add node to new parrent
		otherParrentNode_.addSubNodeObj(movedNode)

		# Remove the node from old parrent
		thisNode.removeNodeObj()

		# Update new nodes sub-infoTree to reflect its json object structure
		movedNode.setValue()		

		return movedNode

	# move Node specified by Name to other parrentNode relative search from thisNode
	# Search thisNode sub-infoTree unless startNode is specified	
	def moveNodeByName(self, name_, otherParrentNode_, uniqueLevel_=-1, startNode_ = ""):
		thisNode = self
		
		# Find specified node node
		thisNode = thisNode.getNodeByName(name_, uniqueLevel_, startNode_)

		# Was a valid node found?
		if thisNode == "":
			#N =>signal failed to move
			self.error_ = "moveNodeByName: Cannot find node with name " + name_
			return self
			
		# Create copy of thisNode
		movedNode = thisNode.copyNodeObj()

		# Add node to new parrent
		otherParrentNode_.addSubNodeObj(movedNode)

		# Remove the node from old parrent
		thisNode.removeNodeObj()

		# Update new nodes sub-infoTree to reflect its json object structure
		movedNode.setValue()		

		return movedNode

	# move Node specified by Value to other parrentNode relative search from thisNode
	# Search thisNode sub-infoTree unless startNode is specified	
	def moveNodeByValue(self, value_, otherParrentNode_, uniqueLevel_=-1, startNode_ = ""):
		thisNode = self
		
		# Find specified node node
		thisNode = thisNode.getNodeByValue(value_, uniqueLevel_, startNode_)

		# Was a valid node found?
		if thisNode == "":
			#N =>signal failed to move
			self.error_ = "moveNodeByValue: Cannot find node with value " + self.getString(value_)
			return self
			
		# Create copy of thisNode
		movedNode = thisNode.copyNodeObj()

		# Add node to new parrent
		otherParrentNode_.addSubNodeObj(movedNode)

		# Remove the node from old parrent
		thisNode.removeNodeObj()

		# Update new nodes sub-infoTree to reflect its json object structure
		movedNode.setValue()		

		return movedNode		

#------------------- MOVE peerNode  Helper/Wrapper METHODS (Search in thisNodes peerNodes) ---------

	# Move peerNodeObj (by value) Specified by Id, Search in thisNodes peerNodes
	# use rootNode if you are unsure where the node is located
	def movePeerNodeById(self, nodeId_, otherParrentNode_, uniqueLevel_=-1):
		thisNode = self
		startNode = thisNode

		# Find specified peerNode
		thisNode = thisNode.getPeerNodeById(nodeId_)

		# Was a valid node found?
		if thisNode == "":
			#N =>signal failed to move
			self.error_ = "movePeerNodeById: Cannot find node with id " + nodeId_
			return self

		# Create copy of thisNode
		movedNode = thisNode.copyNodeObj()

		# Add node to new parrent
		otherParrentNode_.addSubNodeObj(movedNode)

		# Remove the node from old parrent
		thisNode.removeNodeObj()

		# Update new nodes sub-infoTree to reflect its json object structure
		movedNode.setValue()

		return movedNode	   

	# Move new peerNodeObj (by value) Specified by name, Search in thisNodes peerNodes
	# use rootNode if you are unsure where the node is located
	def movePeerNodeByName(self, name_, otherParrentNode_, uniqueLevel_=-1):
		thisNode = self
		startNode = thisNode

		# Find specified peerNode
		thisNode = thisNode.getPeerNodeByName(name_)

		# Was a valid node found?
		if thisNode == "":
			#N =>signal failed to move
			self.error_ = "movePeerNodeByName: Cannot find node with name " + name_
			return self

		# Create copy of thisNode
		movedNode = thisNode.copyNodeObj()

		# Add node to new parrent
		otherParrentNode_.addSubNodeObj(movedNode)

		# Remove the node from old parrent
		thisNode.removeNodeObj()

		# Update new nodes sub-infoTree to reflect its json object structure
		movedNode.setValue()

		return movedNode	

	# Move new peerNodeObj (by value) Specified by value, Search in thisNodes peerNodes
	# use rootNode if you are unsure where the node is located
	def movePeerNodeByValue(self, value_, otherParrentNode_, uniqueLevel_=-1):
		thisNode = self
		startNode = thisNode

		# Find specified peerNode
		thisNode = thisNode.getPeerNodeByValue(value_)

		# Was a valid node found?
		if thisNode == "":
			#N =>signal failed to move
			self.error_ = "movePeerNodeByValue: Cannot find node with value " + self.getString(value_)
			return self

		# Create copy of thisNode
		movedNode = thisNode.copyNodeObj()

		# Add node to new parrent
		otherParrentNode_.addSubNodeObj(movedNode)

		# Remove the node from old parrent
		thisNode.removeNodeObj()

		# Update new nodes sub-infoTree to reflect its json object structure
		movedNode.setValue()

		return movedNode	

	# Move peerNodeObj (by value) specified by ix, Search in thisNodes peerNodes
	# use rootNode if you are unsure where the node is located
	def movePeerNodeByIx(self, nodeIx_, otherParrentNode_):
		thisNode = self

		# Find specified node
		thisNode = thisNode.getPeerNodeByIx(nodeIx_)

		# Was a valid node found?
		if thisNode == "":
			#N =>signal failed to move
			self.error_ = "movePeerNodeByIx: Cannot find node with ix " + str(nodeIx_)
			return self
			
		# Create copy of thisNode
		movedNode = thisNode.copyNodeObj()

		# Add node to new parrent
		otherParrentNode_.addSubNodeObj(movedNode)

		# Remove the node from old parrent
		thisNode.removeNodeObj()

		# Update new nodes sub-infoTree to reflect its json object structure
		movedNode.setValue()		

		return movedNode

#------------------- MOVE subNode Helper/Wrapper METHODS (Search in thisNodes subNodes) ---------
	# Move subNodeObj (by value) Specified by Id, Search in thisNodes subNodes
	# use rootNode if you are unsure where the node is located
	def moveSubNodeById(self, nodeId_, otherParrentNode_, uniqueLevel_=-1):
		thisNode = self
		startNode = thisNode

		# Find specified peerNode
		thisNode = thisNode.getSubNodeById(nodeId_)

		# Was a valid node found?
		if thisNode == "":
			#N =>signal failed to move
			self.error_ = "moveSubNodeById: Cannot find node with id " + nodeId_
			return self

		# Create copy of thisNode
		movedNode = thisNode.copyNodeObj()

		# Add node to new parrent
		otherParrentNode_.addSubNodeObj(movedNode)

		# Remove the node from old parrent
		thisNode.removeNodeObj()

		# Update new nodes sub-infoTree to reflect its json object structure
		movedNode.setValue()

		return movedNode	   

	# Move subNodeObj (by value) Specified by name, Search in thisNodes subNodes
	# use rootNode if you are unsure where the node is located
	def moveSubNodeByName(self, name_, otherParrentNode_, uniqueLevel_=-1):
		thisNode = self
		startNode = thisNode

		# Find specified peerNode
		thisNode = thisNode.getSubNodeByName(name_)

		# Was a valid node found?
		if thisNode == "":
			#N =>signal failed to move
			self.error_ = "moveSubNodeByName: Cannot find node with name " + name_
			return self

		# Create copy of thisNode
		movedNode = thisNode.copyNodeObj()

		# Add node to new parrent
		otherParrentNode_.addSubNodeObj(movedNode)

		# Remove the node from old parrent
		thisNode.removeNodeObj()

		# Update new nodes sub-infoTree to reflect its json object structure
		movedNode.setValue()

		return movedNode	

	# Move subNodeObj (by value) Specified by value, Search in thisNodes subNodes
	# use rootNode if you are unsure where the node is located
	def moveSubNodeByValue(self, value_, otherParrentNode_, uniqueLevel_=-1):
		thisNode = self
		startNode = thisNode

		# Find specified peerNode
		thisNode = thisNode.getSubNodeByValue(value_)

		# Was a valid node found?
		if thisNode == "":
			#N =>signal failed to move
			self.error_ = "moveSubNodeByValue: Cannot find node with value " + self.getString(value_)
			return self

		# Create copy of thisNode
		movedNode = thisNode.copyNodeObj()

		# Add node to new parrent
		otherParrentNode_.addSubNodeObj(movedNode)

		# Remove the node from old parrent
		thisNode.removeNodeObj()

		# Update new nodes sub-infoTree to reflect its json object structure
		movedNode.setValue()

		return movedNode	

	# Move subNodeObj (by value) specified by ix, Search in thisNodes subNodes
	# use rootNode if you are unsure where the node is located
	def moveSubNodeByIx(self, nodeIx_, otherParrentNode_):
		thisNode = self

		# Find specified node
		thisNode = thisNode.getSubNodeByIx(nodeIx_)

		# Was a valid node found?
		if thisNode == "":
			#N =>signal failed to move
			self.error_ = "moveSubNodeByIx: Cannot find node with ix " + str(nodeIx_)
			return self
			
		# Create copy of thisNode
		movedNode = thisNode.copyNodeObj()

		# Add node to new parrent
		otherParrentNode_.addSubNodeObj(movedNode)

		# Remove the node from old parrent
		thisNode.removeNodeObj()

		# Update new nodes sub-infoTree to reflect its json object structure
		movedNode.setValue()		

		return movedNode

# -------- Copy node Helper/Warpper Methods (Search from thisNode to end of sub-infoTree) -----
# Methods used to copy nodes "incl. sub-infoTree" around between parrentNodes "Global copy"
	# copy thisNode to other parrentNode relative search from thisNode
	# Search thisNode sub-infoTree unless startNode is specified	
	def copyNode(self, otherParrentNode_ = "", uniqueLevel_=-1):
		thisNode = self
		
		# Has parrentNode been specified?
		if otherParrentNode_ == "":
			#N => Assume copy of node should be retuned
			copiedNode = thisNode.copyNodeObj()
			return copiedNode

		# Create copy of thisNode
		copiedNode = thisNode.copyNodeObj()

		# Assigne unique name to the new node to ensure there is no duplicae names "keys"
		ix = 0
		someNode = ""
		while(1):
			# Try next name
			newName = copiedNode.name_ + str(ix)			
			#does specified node allready Exist as subNode of new parrentNode
			someNode = otherParrentNode_.getSubNodeByName(newName)
			if someNode == "":
				#N => New valid node key found
				break

			# Update ix
			ix += 1

		# Was a valid newName found?
		if someNode == "":
			#Y => Update nodeName 
			copiedNode.name_ = newName
		else:
			#N => Signal failed to copy node
			self.error_ = "copyNode: Failed to find a unique name for copied node"
			return self		

		# Add node to new parrent
		otherParrentNode_.addSubNodeObj(copiedNode)

		# Update new nodes sub-infoTree to reflect its json object structure
		copiedNode.setValue()		

		return copiedNode

	# copy Node "incl. sub-infoTree" specified by Id to other parrentNode relative search from thisNode 
	# Search thisNode sub-infoTree unless startNode is specified
	def copyNodeById(self, nodeId_, otherParrentNode_ = "", uniqueLevel_=-1, startNode_ = ""):
		thisNode = self
		
		# Find specified node node
		thisNode = thisNode.getNodeById(nodeId_,uniqueLevel_, startNode_)

		# Was a valid node found?
		if thisNode == "":
			#N =>signal failed to move
			self.error_ = "copyNodeById: Cannot find node with id " + nodeId_
			return self

		# Has parrentNode been specified?
		if otherParrentNode_ == "":
			#N => Assume copy of node should be retuned
			copiedNode = thisNode.copyNodeObj()
			return copiedNode

		# Create copy of thisNode
		copiedNode = thisNode.copyNodeObj()

		# Assigne unique name to the new node to ensure there is no duplicae names "keys"
		ix = 0
		someNode = ""
		while(1):
			# Try next name
			newName = copiedNode.name_ + str(ix)			
			#does specified node allready Exist as subNode of new parrentNode
			someNode = otherParrentNode_.getSubNodeByName(newName)
			if someNode == "":
				#N => New valid node key found
				break

			# Update ix
			ix += 1

		# Was a valid newName found?
		if someNode == "":
			#Y => Update nodeName 
			copiedNode.name_ = newName
		else:
			#N => Signal failed to copy node
			self.error_ = "copyNode: Failed to find a unique name for copied node"
			return self		

		# Add node to new parrent
		otherParrentNode_.addSubNodeObj(copiedNode)

		# Update new nodes sub-infoTree to reflect its json object structure
		copiedNode.setValue()		

		return copiedNode

	# copy Node "incl. sub-infoTree" specified by Name to other parrentNode relative search from thisNode
	# Search thisNode sub-infoTree unless startNode is specified	
	def copyNodeByName(self, name_, otherParrentNode_ = "", uniqueLevel_=-1, startNode_ = ""):
		thisNode = self
		
		# Find specified node node
		thisNode = thisNode.getNodeByName(name_, uniqueLevel_, startNode_)

		# Was a valid node found?
		if thisNode == "":
			#N =>signal failed to move
			self.error_ = "copyNodeByName: Cannot find node with name " + name_
			return self

		# Has parrentNode been specified?
		if otherParrentNode_ == "":
			#N => Assume copy of node should be retuned
			copiedNode = thisNode.copyNodeObj()
			return copiedNode			
			
		# Create copy of thisNode
		copiedNode = thisNode.copyNodeObj()

		# Assigne unique name to the new node to ensure there is no duplicae names "keys"
		ix = 0
		someNode = ""
		while(1):
			# Try next name
			newName = copiedNode.name_ + str(ix)			
			#does specified node allready Exist as subNode of new parrentNode
			someNode = otherParrentNode_.getSubNodeByName(newName)
			if someNode == "":
				#N => New valid node key found
				break

			# Update ix
			ix += 1

		# Was a valid newName found?
		if someNode == "":
			#Y => Update nodeName 
			copiedNode.name_ = newName
		else:
			#N => Signal failed to copy node
			self.error_ = "copyNode: Failed to find a unique name for copied node"
			return self		

		# Add node to new parrent
		otherParrentNode_.addSubNodeObj(copiedNode)

		# Update new nodes sub-infoTree to reflect its json object structure
		copiedNode.setValue()		

		return copiedNode

	# copy Node "incl. sub-infoTree" specified by Value to other parrentNode relative search from thisNode
	# Search thisNode sub-infoTree unless startNode is specified	
	def copyNodeByValue(self, value_, otherParrentNode_ = "", uniqueLevel_=-1, startNode_ = ""):
		thisNode = self
		
		# Find specified node node
		thisNode = thisNode.getNodeByValue(value_, uniqueLevel_, startNode_)

		# Was a valid node found?
		if thisNode == "":
			#N =>signal failed to move
			self.error_ = "copyNodeByValue: Cannot find node with value " + self.getString(value_)
			return self

		# Has parrentNode been specified?
		if otherParrentNode_ == "":
			#N => Assume copy of node should be retuned
			copiedNode = thisNode.copyNodeObj()
			return copiedNode			
			
		# Create copy of thisNode
		copiedNode = thisNode.copyNodeObj()

		# Assigne unique name to the new node to ensure there is no duplicae names "keys"
		ix = 0
		someNode = ""
		while(1):
			# Try next name
			newName = copiedNode.name_ + str(ix)			
			#does specified node allready Exist as subNode of new parrentNode
			someNode = otherParrentNode_.getSubNodeByName(newName)
			if someNode == "":
				#N => New valid node key found
				break

			# Update ix
			ix += 1

		# Was a valid newName found?
		if someNode == "":
			#Y => Update nodeName 
			copiedNode.name_ = newName
		else:
			#N => Signal failed to copy node
			self.error_ = "copyNode: Failed to find a unique name for copied node"
			return self		

		# Add node to new parrent
		otherParrentNode_.addSubNodeObj(copiedNode)

		# Update new nodes sub-infoTree to reflect its json object structure
		copiedNode.setValue()		

		return copiedNode

#------------------- COPY peerNode  Helper/Wrapper METHODS (Search in thisNodes peerNodes)---------

	# Copy peerNodeObj (by value) Specified by Id, Search in thisNodes peerNodes
	# use rootNode if you are unsure where the node is located
	def copyPeerNodeById(self, nodeId_, otherParrentNode_ = "", uniqueLevel_=-1):
		thisNode = self
		startNode = thisNode

		# Find specified peerNode
		thisNode = thisNode.getPeerNodeById(nodeId_)

		# Was a valid node found?
		if thisNode == "":
			#N =>signal failed to move
			self.error_ = "copyPeerNodeById: Cannot find node with id " + nodeId_
			return self

		# Has parrentNode been specified?
		if otherParrentNode_ == "":
			#N => Assume copy of node should be retuned
			copiedNode = thisNode.copyNodeObj()
			return copiedNode			

		# Create copy of thisNode
		copiedNode = thisNode.copyNodeObj()

		# Assigne unique name to the new node to ensure there is no duplicae names "keys"
		ix = 0
		someNode = ""
		while(1):
			# Try next name
			newName = copiedNode.name_ + str(ix)			
			#does specified node allready Exist as subNode of new parrentNode
			someNode = otherParrentNode_.getSubNodeByName(newName)
			if someNode == "":
				#N => New valid node key found
				break

			# Update ix
			ix += 1

		# Was a valid newName found?
		if someNode == "":
			#Y => Update nodeName 
			copiedNode.name_ = newName
		else:
			#N => Signal failed to copy node
			self.error_ = "copyNode: Failed to find a unique name for copied node"
			return self		

		# Add node to new parrent
		otherParrentNode_.addSubNodeObj(copiedNode)

		# Update new nodes sub-infoTree to reflect its json object structure
		copiedNode.setValue()		

		return copiedNode	   

	# Copy peerNodeObj (by value) Specified by name, Search in thisNodes peerNodes
	# use rootNode if you are unsure where the node is located
	def copyPeerNodeByName(self, name_, otherParrentNode_ = "", uniqueLevel_=-1):
		thisNode = self
		startNode = thisNode

		# Find specified peerNode
		thisNode = thisNode.getPeerNodeByName(name_)

		# Was a valid node found?
		if thisNode == "":
			#N =>signal failed to move
			self.error_ = "copyPeerNodeByName: Cannot find node with name " + name_
			return self

		# Has parrentNode been specified?
		if otherParrentNode_ == "":
			#N => Assume copy of node should be retuned
			copiedNode = thisNode.copyNodeObj()
			return copiedNode			

		# Create copy of thisNode
		copiedNode = thisNode.copyNodeObj()

		# Assigne unique name to the new node to ensure there is no duplicae names "keys"
		ix = 0
		someNode = ""
		while(1):
			# Try next name
			newName = copiedNode.name_ + str(ix)			
			#does specified node allready Exist as subNode of new parrentNode
			someNode = otherParrentNode_.getSubNodeByName(newName)
			if someNode == "":
				#N => New valid node key found
				break

			# Update ix
			ix += 1

		# Was a valid newName found?
		if someNode == "":
			#Y => Update nodeName 
			copiedNode.name_ = newName
		else:
			#N => Signal failed to copy node
			self.error_ = "copyNode: Failed to find a unique name for copied node"
			return self		

		# Add node to new parrent
		otherParrentNode_.addSubNodeObj(copiedNode)

		# Update new nodes sub-infoTree to reflect its json object structure
		copiedNode.setValue()		

		return copiedNode	

	# Copy peerNodeObj (by value) Specified by value, Search in thisNodes peerNodes
	# use rootNode if you are unsure where the node is located
	def copyPeerNodeByValue(self, value_, otherParrentNode_ = "", uniqueLevel_=-1):
		thisNode = self
		startNode = thisNode

		# Find specified peerNode
		thisNode = thisNode.getPeerNodeByValue(value_)

		# Was a valid node found?
		if thisNode == "":
			#N =>signal failed to move
			self.error_ = "copyPeerNodeByValue: Cannot find node with value " + self.getString(value_)
			return self

		# Has parrentNode been specified?
		if otherParrentNode_ == "":
			#N => Assume copy of node should be retuned
			copiedNode = thisNode.copyNodeObj()
			return copiedNode			

		# Create copy of thisNode
		copiedNode = thisNode.copyNodeObj()

		# Assigne unique name to the new node to ensure there is no duplicae names "keys"
		ix = 0
		someNode = ""
		while(1):
			# Try next name
			newName = copiedNode.name_ + str(ix)			
			#does specified node allready Exist as subNode of new parrentNode
			someNode = otherParrentNode_.getSubNodeByName(newName)
			if someNode == "":
				#N => New valid node key found
				break

			# Update ix
			ix += 1

		# Was a valid newName found?
		if someNode == "":
			#Y => Update nodeName 
			copiedNode.name_ = newName
		else:
			#N => Signal failed to copy node
			self.error_ = "copyNode: Failed to find a unique name for copied node"
			return self		

		# Add node to new parrent
		otherParrentNode_.addSubNodeObj(copiedNode)

		# Update new nodes sub-infoTree to reflect its json object structure
		copiedNode.setValue()		

		return copiedNode	

	# Copy peerNodeObj (by value) specified by ix, Search in thisNodes peerNodes
	# use rootNode if you are unsure where the node is located
	def copyPeerNodeByIx(self, nodeIx_, otherParrentNode_ = ""):
		thisNode = self

		# Find specified node
		thisNode = thisNode.getPeerNodeByIx(nodeIx_)

		# Was a valid node found?
		if thisNode == "":
			#N =>signal failed to move
			self.error_ = "copyPeerNodeByIx: Cannot find node with ix " + str(nodeIx_)
			return self

		# Has parrentNode been specified?
		if otherParrentNode_ == "":
			#N => Assume copy of node should be retuned
			copiedNode = thisNode.copyNodeObj()
			return copiedNode			
			
		# Create copy of thisNode
		copiedNode = thisNode.copyNodeObj()

		# Assigne unique name to the new node to ensure there is no duplicae names "keys"
		ix = 0
		someNode = ""
		while(1):
			# Try next name
			newName = copiedNode.name_ + str(ix)			
			#does specified node allready Exist as subNode of new parrentNode
			someNode = otherParrentNode_.getSubNodeByName(newName)
			if someNode == "":
				#N => New valid node key found
				break

			# Update ix
			ix += 1

		# Was a valid newName found?
		if someNode == "":
			#Y => Update nodeName 
			copiedNode.name_ = newName
		else:
			#N => Signal failed to copy node
			self.error_ = "copyNode: Failed to find a unique name for copied node"
			return self		

		# Add node to new parrent
		otherParrentNode_.addSubNodeObj(copiedNode)

		# Update new nodes sub-infoTree to reflect its json object structure
		copiedNode.setValue()		

		return copiedNode

#------------------- COPY subNode Helper/Wrapper METHODS (Search in thisNodes subNodes) ---------
	# Copy subNodeObj (by value) Specified by Id, Search in thisNodes subNodes
	# use rootNode if you are unsure where the node is located
	def copySubNodeById(self, nodeId_, otherParrentNode_ = "", uniqueLevel_=-1):
		thisNode = self
		startNode = thisNode

		# Find specified peerNode
		thisNode = thisNode.getSubNodeById(nodeId_)

		# Was a valid node found?
		if thisNode == "":
			#N =>signal failed to move
			self.error_ = "copySubNodeById: Cannot find node with id " + nodeId_
			return self

		# Has parrentNode been specified?
		if otherParrentNode_ == "":
			#N => Assume copy of node should be retuned
			copiedNode = thisNode.copyNodeObj()
			return copiedNode			

		# Create copy of thisNode
		copiedNode = thisNode.copyNodeObj()

		# Assigne unique name to the new node to ensure there is no duplicae names "keys"
		ix = 0
		someNode = ""
		while(1):
			# Try next name
			newName = copiedNode.name_ + str(ix)			
			#does specified node allready Exist as subNode of new parrentNode
			someNode = otherParrentNode_.getSubNodeByName(newName)
			if someNode == "":
				#N => New valid node key found
				break

			# Update ix
			ix += 1

		# Was a valid newName found?
		if someNode == "":
			#Y => Update nodeName 
			copiedNode.name_ = newName
		else:
			#N => Signal failed to copy node
			self.error_ = "copyNode: Failed to find a unique name for copied node"
			return self		

		# Add node to new parrent
		otherParrentNode_.addSubNodeObj(copiedNode)

		# Update new nodes sub-infoTree to reflect its json object structure
		copiedNode.setValue()		

		return copiedNode	   

	# Copy subNodeObj (by value) Specified by name, Search in thisNodes subNodes
	# use rootNode if you are unsure where the node is located
	def copySubNodeByName(self, name_, otherParrentNode_ = "", uniqueLevel_=-1):
		thisNode = self
		startNode = thisNode

		# Find specified peerNode
		thisNode = thisNode.getSubNodeByName(name_)

		# Was a valid node found?
		if thisNode == "":
			#N =>signal failed to move
			self.error_ = "copySubNodeByName: Cannot find node with name " + name_
			return self

		# Has parrentNode been specified?
		if otherParrentNode_ == "":
			#N => Assume copy of node should be retuned
			copiedNode = thisNode.copyNodeObj()
			return copiedNode			

		# Create copy of thisNode
		copiedNode = thisNode.copyNodeObj()

		# Assigne unique name to the new node to ensure there is no duplicae names "keys"
		ix = 0
		someNode = ""
		while(1):
			# Try next name
			newName = copiedNode.name_ + str(ix)			
			#does specified node allready Exist as subNode of new parrentNode
			someNode = otherParrentNode_.getSubNodeByName(newName)
			if someNode == "":
				#N => New valid node key found
				break

			# Update ix
			ix += 1

		# Was a valid newName found?
		if someNode == "":
			#Y => Update nodeName 
			copiedNode.name_ = newName
		else:
			#N => Signal failed to copy node
			self.error_ = "copyNode: Failed to find a unique name for copied node"
			return self		

		# Add node to new parrent
		otherParrentNode_.addSubNodeObj(copiedNode)

		# Update new nodes sub-infoTree to reflect its json object structure
		copiedNode.setValue()		

		return copiedNode	

	# Copy subNodeObj (by value) Specified by value, Search in thisNodes subNodes
	# use rootNode if you are unsure where the node is located
	def copySubNodeByValue(self, value_, otherParrentNode_ = "", uniqueLevel_=-1):
		thisNode = self
		startNode = thisNode

		# Find specified peerNode
		thisNode = thisNode.getSubNodeByValue(value_)

		# Was a valid node found?
		if thisNode == "":
			#N =>signal failed to move
			self.error_ = "copySubNodeByValue: Cannot find node with value " + self.getString(value_)
			return self

		# Has parrentNode been specified?
		if otherParrentNode_ == "":
			#N => Assume copy of node should be retuned
			copiedNode = thisNode.copyNodeObj()
			return copiedNode			

		# Create copy of thisNode
		copiedNode = thisNode.copyNodeObj()

		# Assigne unique name to the new node to ensure there is no duplicae names "keys"
		ix = 0
		someNode = ""
		while(1):
			# Try next name
			newName = copiedNode.name_ + str(ix)			
			#does specified node allready Exist as subNode of new parrentNode
			someNode = otherParrentNode_.getSubNodeByName(newName)
			if someNode == "":
				#N => New valid node key found
				break

			# Update ix
			ix += 1

		# Was a valid newName found?
		if someNode == "":
			#Y => Update nodeName 
			copiedNode.name_ = newName
		else:
			#N => Signal failed to copy node
			self.error_ = "copyNode: Failed to find a unique name for copied node"
			return self		

		# Add node to new parrent
		otherParrentNode_.addSubNodeObj(copiedNode)

		# Update new nodes sub-infoTree to reflect its json object structure
		copiedNode.setValue()		

		return copiedNode	

	# Copy subNodeObj (by value) specified by ix, Search in thisNodes subNodes
	# use rootNode if you are unsure where the node is located
	def copySubNodeByIx(self, nodeIx_, otherParrentNode_ = ""):
		thisNode = self

		# Find specified node
		thisNode = thisNode.getSubNodeByIx(nodeIx_)

		# Was a valid node found?
		if thisNode == "":
			#N =>signal failed to move
			self.error_ = "copySubNodeByIx: Cannot find node with ix " + str(nodeIx_)
			return self

		# Has parrentNode been specified?
		if otherParrentNode_ == "":
			#N => Assume copy of node should be retuned
			copiedNode = thisNode.copyNodeObj()
			return copiedNode			
			
		# Create copy of thisNode
		copiedNode = thisNode.copyNodeObj()

		# Assigne unique name to the new node to ensure there is no duplicae names "keys"
		ix = 0
		someNode = ""
		while(1):
			# Try next name
			newName = copiedNode.name_ + str(ix)			
			#does specified node allready Exist as subNode of new parrentNode
			someNode = otherParrentNode_.getSubNodeByName(newName)
			if someNode == "":
				#N => New valid node key found
				break

			# Update ix
			ix += 1

		# Was a valid newName found?
		if someNode == "":
			#Y => Update nodeName 
			copiedNode.name_ = newName
		else:
			#N => Signal failed to copy node
			self.error_ = "copyNode: Failed to find a unique name for copied node"
			return self		

		# Add node to new parrent
		otherParrentNode_.addSubNodeObj(copiedNode)

		# Update new nodes sub-infoTree to reflect its json object structure
		copiedNode.setValue()		

		return copiedNode

# ---------------- Reloacate Node methods ------------
# Reloacte is used to only move nodes around on same brach "local move", hence change the order of the peer or subNodes
# -------- Relocate node Helper/Warpper Methods (Search From thisNode to end of sub-infoTree)-----
	# Relocate thisNode to other nodeIx relative search from thisNode
	# Search thisNode sub-infoTree unless startNode is specified	
	def relocateNode(self, nodeIx_ = "", uniqueLevel_=-1):
		thisNode = self
		thisParrentNode = thisNode.parrentNode_

		# Is thisNode rootNode?
		if thisParrentNode == "":
			#Y => Signal fail
			self.error_ = "relocateNodeObj: rootNodes does not have peerNodes"
			return self
		
		# Has nodeIx been specified?
		if nodeIx_ == "":
			#N => Assume thisNodes nodeIx
			nodeIx_ = thisNode.nodeIx_
		else:
			#Y => Is this ix valid?
			if nodeIx_ < 0 or nodeIx_ > thisParrentNode.lastSubNodeIx_:
				#N => Signal failed to move
				self.error_ = "relocateNodeObj: Cannont find node with ix " + str(nodeIx_)
				return self

		# Create copy of thisNode
		movedNode = thisNode.copyNodeObj()

		# Remove old node
		thisNode.removeNodeObj()

		# Reinsert node
		thisParrentNode.insertSubNodeObjByIx(nodeIx_, movedNode)

		# Update new nodes sub-infoTree to reflect its json object structure
		movedNode.setValue()		

		return movedNode

	# Relocate Node specified by Id to other nodeIx relative search from thisNode to end of sub-infoTree
	# Search thisNode sub-infoTree unless startNode is specified
	def relocateNodeById(self, nodeId_, nodeIx_="", uniqueLevel_=-1, startNode_ = ""):
		thisNode = self
				
		# Find specified node by id
		thisNode = thisNode.getNodeById(nodeId_, uniqueLevel_, startNode_)

		# Was a valid node found?
		if thisNode == "":
			#N =>signal failed to move
			self.error_ = "reloacetNodeObjById: Cannot find node with id " + nodeId_
			return self

		# Keep track of parrentNode
		thisParrentNode = thisNode.parrentNode_			

		# Is thisNode rootNode?
		if thisParrentNode == "":
			#Y => Signal fail
			self.error_ = "relocateNodeObjById: rootNodes does not have peerNodes"
			return self		

		# Has nodeIx been specified?
		if nodeIx_ == "":
			#N => Assume thisNodes nodeIx
			nodeIx_ = thisNode.nodeIx_
		else:
			#Y => Is this ix valid?
			if nodeIx_ < 0 or nodeIx_ > thisParrentNode.lastSubNodeIx_:
				#N => Signal failed to move
				self.error_ = "relocateNodeObjById: Cannont find node with ix " + str(nodeIx_)
				return self									

		# Create copy of thisNode
		movedNode = thisNode.copyNodeObj()

		# Remove old node
		thisNode.removeNodeObj()

		# Reinsert node
		thisParrentNode.insertSubNodeObjByIx(nodeIx_, movedNode)

		# Update new nodes sub-infoTree to reflect its json object structure
		movedNode.setValue()		

		return movedNode

	# Relocate Node specified by Name to other nodeIx relative search from thisNode to end of sub-infoTree
	# Search thisNode sub-infoTree unless startNode is specified	
	def relocateNodeByName(self, name_, nodeIx_ = "", uniqueLevel_=-1, startNode_ = ""):
		thisNode = self
				
		# Find specified node by id
		thisNode = thisNode.getNodeByName(name_, uniqueLevel_, startNode_)

		# Was a valid node found?
		if thisNode == "":
			#N =>signal failed to move
			self.error_ = "reloacetNodeObjByName: Cannot find node with name " + name_
			return self

		# Keep track of parrentNode
		thisParrentNode = thisNode.parrentNode_			

		# Is thisNode rootNode?
		if thisParrentNode == "":
			#Y => Signal fail
			self.error_ = "relocateNodeObjByName: rootNodes does not have peerNodes"
			return self		

		# Has nodeIx been specified?
		if nodeIx_ == "":
			#N => Assume thisNodes nodeIx
			nodeIx_ = thisNode.nodeIx_
		else:
			#Y => Is this ix valid?
			if nodeIx_ < 0 or nodeIx_ > thisParrentNode.lastSubNodeIx_:
				#N => Signal failed to move
				self.error_ = "relocateNodeObjByName: Cannont find node with ix " + str(nodeIx_)
				return self						

		# Create copy of thisNode
		movedNode = thisNode.copyNodeObj()

		# Remove old node
		thisNode.removeNodeObj()

		# Reinsert node
		thisParrentNode.insertSubNodeObjByIx(nodeIx_, movedNode)

		# Update new nodes sub-infoTree to reflect its json object structure
		movedNode.setValue()		

		return movedNode

	# Relocate Node specified by Value to other nodeIx relative search from thisNode to end of sub-infoTree
	# Search thisNode sub-infoTree unless startNode is specified	
	def relocateNodeByValue(self, value_, nodeIx_ = "", uniqueLevel_=-1, startNode_ = ""):
		thisNode = self
				
		# Find specified node by id
		thisNode = thisNode.getNodeByValue(value_, uniqueLevel_, startNode_)

		# Was a valid node found?
		if thisNode == "":
			#N =>signal failed to move
			self.error_ = "reloacetNodeObjByValue: Cannot find node with value " + self.getString(value_)
			return self

		# Keep track of parrentNode
		thisParrentNode = thisNode.parrentNode_			

		# Is thisNode rootNode?
		if thisParrentNode == "":
			#Y => Signal fail
			self.error_ = "relocateNodeObjByValue: rootNodes does not have peerNodes"
			return self		

		# Has nodeIx been specified?
		if nodeIx_ == "":
			#N => Assume thisNodes nodeIx
			nodeIx_ = thisNode.nodeIx_
		else:
			#Y => Is this ix valid?
			if nodeIx_ < 0 or nodeIx_ > thisParrentNode.lastSubNodeIx_:
				#N => Signal failed to move
				self.error_ = "relocateNodeObjByValue: Cannont find node with ix " + str(nodeIx_)
				return self						

		# Create copy of thisNode
		movedNode = thisNode.copyNodeObj()

		# Remove old node
		thisNode.removeNodeObj()

		# Reinsert node
		thisParrentNode.insertSubNodeObjByIx(nodeIx_, movedNode)

		# Update new nodes sub-infoTree to reflect its json object structure
		movedNode.setValue()		

		return movedNode

#------------------- RELOCATE peerNode  Helper/Wrapper METHODS (Search in thisNodes peerNodes) ---------

	# Relocate peerNodeObj (by value) Specified by Id to specified nodeIx, Search in thisNodes peerNodes
	# use rootNode if you are unsure where the node is located
	def relocatePeerNodeById(self, nodeId_, nodeIx_ = "", uniqueLevel_=-1):
		thisNode = self
				
		# Find specified node by id
		thisNode = thisNode.getPeerNodeById(nodeId_, uniqueLevel_)

		# Was a valid node found?
		if thisNode == "":
			#N =>signal failed to move
			self.error_ = "reloacetPeerNodeObjById: Cannot find node with id " + nodeId_
			return self

		# Keep track of parrentNode
		thisParrentNode = thisNode.parrentNode_			

		# Is thisNode rootNode?
		if thisParrentNode == "":
			#Y => Signal fail
			self.error_ = "relocatePeerNodeObjById: rootNodes does not have peerNodes"
			return self		

		# Has nodeIx been specified?
		if nodeIx_ == "":
			#N => Assume thisNodes nodeIx
			nodeIx_ = thisNode.nodeIx_
		else:
			#Y => Is this ix valid?
			if nodeIx_ < 0 or nodeIx_ > thisParrentNode.lastSubNodeIx_:
				#N => Signal failed to move
				self.error_ = "relocatePeerNodeObjById: Cannont find node with ix " + str(nodeIx_)
				return self						

		# Create copy of thisNode
		movedNode = thisNode.copyNodeObj()

		# Remove old node
		thisNode.removeNodeObj()

		# Reinsert node
		thisParrentNode.insertSubNodeObjByIx(nodeIx_, movedNode)

		# Update new nodes sub-infoTree to reflect its json object structure
		movedNode.setValue()		

		return movedNode	   

	# Relocate new peerNodeObj (by value) Specified by name, Search in thisNodes peerNodes
	# use rootNode if you are unsure where the node is located
	def relocatePeerNodeByName(self, name_, nodeIx_ = "", uniqueLevel_=-1):
		thisNode = self
				
		# Find specified node by id
		thisNode = thisNode.getPeerNodeByName(name_, uniqueLevel_)

		# Was a valid node found?
		if thisNode == "":
			#N =>signal failed to move
			self.error_ = "reloacetPeerNodeObjByName: Cannot find node with id " + name_
			return self

		# Keep track of parrentNode
		thisParrentNode = thisNode.parrentNode_			

		# Is thisNode rootNode?
		if thisParrentNode == "":
			#Y => Signal fail
			self.error_ = "relocatePeerNodeObjByName: rootNodes does not have peerNodes"
			return self		

		# Has nodeIx been specified?
		if nodeIx_ == "":
			#N => Assume thisNodes nodeIx
			nodeIx_ = thisNode.nodeIx_
		else:
			#Y => Is this ix valid?
			if nodeIx_ < 0 or nodeIx_ > thisParrentNode.lastSubNodeIx_:
				#N => Signal failed to move
				self.error_ = "relocatePeerNodeObjByName: Cannont find node with ix " + str(nodeIx_)
				return self						

		# Create copy of thisNode
		movedNode = thisNode.copyNodeObj()

		# Remove old node
		thisNode.removeNodeObj()

		# Reinsert node
		thisParrentNode.insertSubNodeObjByIx(nodeIx_, movedNode)

		# Update new nodes sub-infoTree to reflect its json object structure
		movedNode.setValue()		

		return movedNode	

	# Relocate new peerNodeObj (by value) Specified by value, Search in thisNodes peerNodes
	# use rootNode if you are unsure where the node is located
	def relocatePeerNodeByValue(self, value_, nodeIx_ = "", uniqueLevel_=-1):
		thisNode = self
				
		# Find specified node by id
		thisNode = thisNode.getPeerNodeByValue(value_, uniqueLevel_)

		# Was a valid node found?
		if thisNode == "":
			#N =>signal failed to move
			self.error_ = "reloacetPeerNodeObjByValue: Cannot find node with value " + self.getString(value_)
			return self

		# Keep track of parrentNode
		thisParrentNode = thisNode.parrentNode_			

		# Is thisNode rootNode?
		if thisParrentNode == "":
			#Y => Signal fail
			self.error_ = "relocatePeerNodeObjByValue: rootNodes does not have peerNodes"
			return self		

		# Has nodeIx been specified?
		if nodeIx_ == "":
			#N => Assume thisNodes nodeIx
			nodeIx_ = thisNode.nodeIx_
		else:
			#Y => Is this ix valid?
			if nodeIx_ < 0 or nodeIx_ > thisParrentNode.lastSubNodeIx_:
				#N => Signal failed to move
				self.error_ = "relocatePeerNodeObjByValue: Cannont find node with ix " + str(nodeIx_)
				return self						

		# Create copy of thisNode
		movedNode = thisNode.copyNodeObj()

		# Remove old node
		thisNode.removeNodeObj()

		# Reinsert node
		thisParrentNode.insertSubNodeObjByIx(nodeIx_, movedNode)

		# Update new nodes sub-infoTree to reflect its json object structure
		movedNode.setValue()		

		return movedNode	

	# Relocate peerNodeObj (by value) specified by ix to specified ix, Search in thisNodes peerNodes
	# use rootNode if you are unsure where the node is located
	def relocatePeerNodeByIx(self, oldNodeIx_, nodeIx_ = ""):
		thisNode = self
				
		# Find specified node by ix
		thisNode = thisNode.getPeerNodeByIx(oldNodeIx_)

		# Was a valid node found?
		if thisNode == "":
			#N =>signal failed to move
			self.error_ = "reloacetPeerNodeObjByIx: Cannot find node with id " + oldNodeIx_
			return self

		# Keep track of parrentNode
		thisParrentNode = thisNode.parrentNode_			

		# Is thisNode rootNode?
		if thisParrentNode == "":
			#Y => Signal fail
			self.error_ = "relocatePeerNodeObjByIx: rootNodes does not have peerNodes"
			return self		

		# Has nodeIx been specified?
		if nodeIx_ == "":
			#N => Assume thisNodes nodeIx
			nodeIx_ = thisNode.nodeIx_
		else:
			#Y => Is this ix valid?
			if nodeIx_ < 0 or nodeIx_ > thisParrentNode.lastSubNodeIx_:
				#N => Signal failed to move
				self.error_ = "relocatePeerNodeObjByIx: Cannont find node with ix " + str(nodeIx_)
				return self						

		# Create copy of thisNode
		movedNode = thisNode.copyNodeObj()

		# Remove old node
		thisNode.removeNodeObj()

		# Reinsert node
		thisParrentNode.insertSubNodeObjByIx(nodeIx_, movedNode)

		# Update new nodes sub-infoTree to reflect its json object structure
		movedNode.setValue()		

		return movedNode

#------------------- RELOCATE subNode Helper/Wrapper METHODS (Search in thisNodes subNodes)---------
	# Relocate subNodeObj (by value) Specified by Id to specified ix, Search in thisNodes subNodes
	# use rootNode if you are unsure where the node is located
	def relocateSubNodeById(self, nodeId_, nodeIx_ = "", uniqueLevel_=-1):
		thisNode = self

		# Keep track of parrentNode
		thisParrentNode = thisNode

		# Find specified node by id
		thisNode = thisNode.getSubNodeById(nodeId_, uniqueLevel_)
		
		# Was a valid node found?
		if thisNode == "":
			#N =>signal failed to move
			self.error_ = "reloacetSubNodeObjById: Cannot find node with id " + nodeId_
			return self


		# Is thisNode a leafNode?
		if thisParrentNode.lastSubNodeIx_ == -1:
			#Y => Signal failed to move
			self.error_ = "relocateSubNodeObjById: leafNodes does not have subNodes"
			return self			

		# Has nodeIx been specified?
		if nodeIx_ == "":
			#N => Assume thisNodes nodeIx
			nodeIx_ = thisNode.nodeIx_
		else:
			#Y => Is this ix valid?
			if nodeIx_ < 0 or nodeIx_ > thisParrentNode.lastSubNodeIx_:
				#N => Signal failed to move
				self.error_ = "relocateSubNodeObjById: Cannont find node with ix " + str(nodeIx_)
				return self						

		# Create copy of thisNode
		movedNode = thisNode.copyNodeObj()

		# Remove old node
		thisNode.removeNodeObj()
		
		# Reinsert node
		thisParrentNode.insertSubNodeObjByIx(nodeIx_, movedNode)

		# Update new nodes sub-infoTree to reflect its json object structure
		movedNode.setValue()		

		return movedNode		   

	# Relocate subNodeObj (by value) Specified by name, Search in thisNodes subNodes
	# use rootNode if you are unsure where the node is located
	def relocateSubNodeByName(self, name_, nodeIx_ = "", uniqueLevel_=-1):
		thisNode = self

		# Keep track of parrentNode
		thisParrentNode = thisNode

		# Find specified node by id
		thisNode = thisNode.getSubNodeByName(name_, uniqueLevel_)
		
		# Was a valid node found?
		if thisNode == "":
			#N =>signal failed to move
			self.error_ = "reloacetSubNodeObjByName: Cannot find node with id " + name_
			return self


		# Is thisNode a leafNode?
		if thisParrentNode.lastSubNodeIx_ == -1:
			#Y => Signal failed to move
			self.error_ = "relocateSubNodeObjByName: leafNodes does not have subNodes"
			return self			

		# Has nodeIx been specified?
		if nodeIx_ == "":
			#N => Assume thisNodes nodeIx
			nodeIx_ = thisNode.nodeIx_
		else:
			#Y => Is this ix valid?
			if nodeIx_ < 0 or nodeIx_ > thisParrentNode.lastSubNodeIx_:
				#N => Signal failed to move
				self.error_ = "relocateSubNodeObjByName: Cannont find node with ix " + str(nodeIx_)
				return self						

		# Create copy of thisNode
		movedNode = thisNode.copyNodeObj()

		# Remove old node
		thisNode.removeNodeObj()
		
		# Reinsert node
		thisParrentNode.insertSubNodeObjByIx(nodeIx_, movedNode)

		# Update new nodes sub-infoTree to reflect its json object structure
		movedNode.setValue()		

		return movedNode	

	# Relocate subNodeObj (by value) Specified by value, Search in thisNodes subNodes
	# use rootNode if you are unsure where the node is located
	def relocateSubNodeByValue(self, value_, nodeIx_ = "", uniqueLevel_=-1):
		thisNode = self

		# Keep track of parrentNode
		thisParrentNode = thisNode

		# Find specified node by id
		thisNode = thisNode.getSubNodeByValue(value_, uniqueLevel_)
		
		# Was a valid node found?
		if thisNode == "":
			#N =>signal failed to move
			self.error_ = "reloacetSubNodeObjByValue: Cannot find node with value " + self.getString(value_)
			return self


		# Is thisNode a leafNode?
		if thisParrentNode.lastSubNodeIx_ == -1:
			#Y => Signal failed to move
			self.error_ = "relocateSubNodeObjByValue: leafNodes does not have subNodes"
			return self			

		# Has nodeIx been specified?
		if nodeIx_ == "":
			#N => Assume thisNodes nodeIx
			nodeIx_ = thisNode.nodeIx_
		else:
			#Y => Is this ix valid?
			if nodeIx_ < 0 or nodeIx_ > thisParrentNode.lastSubNodeIx_:
				#N => Signal failed to move
				self.error_ = "relocateSubNodeObjByValue: Cannont find node with ix " + str(nodeIx_)
				return self						

		# Create copy of thisNode
		movedNode = thisNode.copyNodeObj()

		# Remove old node
		thisNode.removeNodeObj()
		
		# Reinsert node
		thisParrentNode.insertSubNodeObjByIx(nodeIx_, movedNode)

		# Update new nodes sub-infoTree to reflect its json object structure
		movedNode.setValue()		

		return movedNode	

	# Relocate subNodeObj (by value) specified by ix, Search in thisNodes subNodes
	# use rootNode if you are unsure where the node is located
	def relocateSubNodeByIx(self, oldNodeIx_, nodeIx_ = ""):
		thisNode = self

		# Keep track of parrentNode
		thisParrentNode = thisNode

		# Find specified node by id
		thisNode = thisNode.getSubNodeByIx(oldNodeIx_)
		
		# Was a valid node found?
		if thisNode == "":
			#N =>signal failed to move
			self.error_ = "reloacetSubNodeObjByIx: Cannot find node with ix " + oldNodeIx_
			return self

		# Is thisNode a leafNode?
		if thisParrentNode.lastSubNodeIx_ == -1:
			#Y => Signal failed to move
			self.error_ = "relocateSubNodeObjByIx: leafNodes does not have subNodes"
			return self			

		# Has nodeIx been specified?
		if nodeIx_ == "":
			#N => Assume thisNodes nodeIx
			nodeIx_ = thisNode.nodeIx_
		else:
			#Y => Is this ix valid?
			if nodeIx_ < 0 or nodeIx_ > thisParrentNode.lastSubNodeIx_:
				#N => Signal failed to move
				self.error_ = "relocateSubNodeObjByIx: Cannont find node with ix " + str(nodeIx_)
				return self						

		# Create copy of thisNode
		movedNode = thisNode.copyNodeObj()

		# Remove old node
		thisNode.removeNodeObj()
		
		# Reinsert node
		thisParrentNode.insertSubNodeObjByIx(nodeIx_, movedNode)

		# Update new nodes sub-infoTree to reflect its json object structure
		movedNode.setValue()		

		return movedNode

# ---------------- DUPLICATE Node methods ------------
# Duplicate is used to only copy nodes around on same brach "local copy", hence change the order of the peer or subNodes
# -------- Duplicate node Helper/Warpper Methods (Search from thisNode to end of sub-infoTree)-----
	# Duplicate thisNode to other nodeIx relative search from thisNode
	# Search thisNode sub-infoTree unless startNode is specified	
	def duplicateNode(self, nodeIx_ = "", uniqueLevel_=-1):
		thisNode = self
		thisParrentNode = thisNode.parrentNode_

		# Is thisNode rootNode?
		if thisParrentNode == "":
			#Y => Signal fail
			self.error_ = "duplicateNodeObj: rootNodes does not have peerNodes"
			return self
		
		# Has nodeIx been specified?
		if nodeIx_ == "":
			#N => Assume thisNodes nodeIx
			nodeIx_ = thisNode.nodeIx_
		else:
			#Y => Is this ix valid?
			if nodeIx_ < 0 or nodeIx_ > thisParrentNode.lastSubNodeIx_:
				#N => Signal failed to move
				self.error_ = "duplicateNodeObj: Cannont find node with ix " + str(nodeIx_)
				return self

		# Create copy of thisNode
		copiedNode = thisNode.copyNodeObj()

		# Assigne unique name to the new node to ensure there is no duplicae names "keys"
		ix = 0
		someNode = ""
		while(1):
			# Try next name
			newName = copiedNode.name_ + str(ix)			
			#does specified node allready Exist
			someNode = thisParrentNode.getSubNodeByName(newName)
			if someNode == "":
				#N => New valid node key found
				break

			# Update ix
			ix += 1

		# Was a valid newName found?
		if someNode == "":
			#Y => Update nodeName 
			copiedNode.name_ = newName
		else:
			#N => Signal failed to copy node
			self.error_ = "duplicateNodeObj: Failed to find a unique name for copied node"
			return self

		# Reinsert node
		thisParrentNode.insertSubNodeObjByIx(nodeIx_, copiedNode)

		# Update new nodes sub-infoTree to reflect its json object structure
		copiedNode.setValue()		

		return copiedNode

	# Duplicate Node specified by Id to other nodeIx relative search from thisNode to end of sub-infoTree
	# Search thisNode sub-infoTree unless startNode is specified
	def duplicateNodeById(self, nodeId_, nodeIx_="", uniqueLevel_=-1, startNode_ = ""):
		thisNode = self
				
		# Find specified node by id
		thisNode = thisNode.getNodeById(nodeId_, uniqueLevel_, startNode_)

		# Was a valid node found?
		if thisNode == "":
			#N =>signal failed to move
			self.error_ = "duplicateNodeObjById: Cannot find node with id " + nodeId_
			return self

		# Keep track of parrentNode
		thisParrentNode = thisNode.parrentNode_			

		# Is thisNode rootNode?
		if thisParrentNode == "":
			#Y => Signal fail
			self.error_ = "duplicateNodeObjById: rootNodes does not have peerNodes"
			return self		

		# Has nodeIx been specified?
		if nodeIx_ == "":
			#N => Assume thisNodes nodeIx
			nodeIx_ = thisNode.nodeIx_
		else:
			#Y => Is this ix valid?
			if nodeIx_ < 0 or nodeIx_ > thisParrentNode.lastSubNodeIx_:
				#N => Signal failed to move
				self.error_ = "duplicateNodeObjById: Cannont find node with ix " + str(nodeIx_)
				return self									

		# Create copy of thisNode
		copiedNode = thisNode.copyNodeObj()

		# Assigne unique name to the new node to ensure there is no duplicae names "keys"
		ix = 0
		someNode = ""
		while(1):
			# Try next name
			newName = copiedNode.name_ + str(ix)			
			#does specified node allready Exist
			someNode = thisParrentNode.getSubNodeByName(newName)
			if someNode == "":
				#N => New valid node key found
				break

			# Update ix
			ix += 1

		# Was a valid newName found?
		if someNode == "":
			#Y => Update nodeName 
			copiedNode.name_ = newName
		else:
			#N => Signal failed to copy node
			self.error_ = "duplicateNodeObj: Failed to find a unique name for copied node"
			return self

		# Reinsert node
		thisParrentNode.insertSubNodeObjByIx(nodeIx_, copiedNode)

		# Update new nodes sub-infoTree to reflect its json object structure
		copiedNode.setValue()		

		return copiedNode

	# Duplicate Node specified by Name to other nodeIx relative search from thisNode to end of sub-infoTree
	# Search thisNode sub-infoTree unless startNode is specified	
	def duplicateNodeByName(self, name_, nodeIx_ = "", uniqueLevel_=-1, startNode_ = ""):
		thisNode = self
				
		# Find specified node by id
		thisNode = thisNode.getNodeByName(name_, uniqueLevel_, startNode_)

		# Was a valid node found?
		if thisNode == "":
			#N =>signal failed to move
			self.error_ = "duplicateNodeObjByName: Cannot find node with name " + name_
			return self

		# Keep track of parrentNode
		thisParrentNode = thisNode.parrentNode_			

		# Is thisNode rootNode?
		if thisParrentNode == "":
			#Y => Signal fail
			self.error_ = "duplicateNodeObjByName: rootNodes does not have peerNodes"
			return self		

		# Has nodeIx been specified?
		if nodeIx_ == "":
			#N => Assume thisNodes nodeIx
			nodeIx_ = thisNode.nodeIx_
		else:
			#Y => Is this ix valid?
			if nodeIx_ < 0 or nodeIx_ > thisParrentNode.lastSubNodeIx_:
				#N => Signal failed to move
				self.error_ = "duplicateNodeObjByName: Cannont find node with ix " + str(nodeIx_)
				return self						

		# Create copy of thisNode
		copiedNode = thisNode.copyNodeObj()

		# Assigne unique name to the new node to ensure there is no duplicae names "keys"
		ix = 0
		someNode = ""
		while(1):
			# Try next name
			newName = copiedNode.name_ + str(ix)			
			#does specified node allready Exist
			someNode = thisParrentNode.getSubNodeByName(newName)
			if someNode == "":
				#N => New valid node key found
				break

			# Update ix
			ix += 1

		# Was a valid newName found?
		if someNode == "":
			#Y => Update nodeName 
			copiedNode.name_ = newName
		else:
			#N => Signal failed to copy node
			self.error_ = "duplicateNodeObj: Failed to find a unique name for copied node"
			return self		

		# Reinsert node
		thisParrentNode.insertSubNodeObjByIx(nodeIx_, copiedNode)

		# Update new nodes sub-infoTree to reflect its json object structure
		copiedNode.setValue()		

		return copiedNode

	# Duplicate Node specified by Value to other nodeIx relative search from thisNode to end of sub-infoTree
	# Search thisNode sub-infoTree unless startNode is specified	
	def duplicateNodeByValue(self, value_, nodeIx_ = "", uniqueLevel_=-1, startNode_ = ""):
		thisNode = self
				
		# Find specified node by id
		thisNode = thisNode.getNodeByValue(value_, uniqueLevel_, startNode_)

		# Was a valid node found?
		if thisNode == "":
			#N =>signal failed to move
			self.error_ = "duplicateNodeObjByValue: Cannot find node with value " + self.getString(value_)
			return self

		# Keep track of parrentNode
		thisParrentNode = thisNode.parrentNode_			

		# Is thisNode rootNode?
		if thisParrentNode == "":
			#Y => Signal fail
			self.error_ = "duplicateNodeObjByValue: rootNodes does not have peerNodes"
			return self		

		# Has nodeIx been specified?
		if nodeIx_ == "":
			#N => Assume thisNodes nodeIx
			nodeIx_ = thisNode.nodeIx_
		else:
			#Y => Is this ix valid?
			if nodeIx_ < 0 or nodeIx_ > thisParrentNode.lastSubNodeIx_:
				#N => Signal failed to move
				self.error_ = "duplicateNodeObjByValue: Cannont find node with ix " + str(nodeIx_)
				return self						

		# Create copy of thisNode
		copiedNode = thisNode.copyNodeObj()

		# Assigne unique name to the new node to ensure there is no duplicae names "keys"
		ix = 0
		someNode = ""
		while(1):
			# Try next name
			newName = copiedNode.name_ + str(ix)			
			#does specified node allready Exist
			someNode = thisParrentNode.getSubNodeByName(newName)
			if someNode == "":
				#N => New valid node key found
				break

			# Update ix
			ix += 1

		# Was a valid newName found?
		if someNode == "":
			#Y => Update nodeName 
			copiedNode.name_ = newName
		else:
			#N => Signal failed to copy node
			self.error_ = "duplicateNodeByValue: Failed to find a unique name for copied node"
			return self		

		# Reinsert node
		thisParrentNode.insertSubNodeObjByIx(nodeIx_, copiedNode)

		# Update new nodes sub-infoTree to reflect its json object structure
		copiedNode.setValue()		

		return copiedNode

#------------------- DUPLICATE peerNode  Helper/Wrapper METHODS (Search in thisNodes peerNodes)---------

	# Duplicate peerNodeObj (by value) Specified by Id to specified nodeIx, Search in thisNodes peerNodes
	# use rootNode if you are unsure where the node is located
	def duplicatePeerNodeById(self, nodeId_, nodeIx_ = "", uniqueLevel_=-1):
		thisNode = self
				
		# Find specified node by id
		thisNode = thisNode.getPeerNodeById(nodeId_, uniqueLevel_)

		# Was a valid node found?
		if thisNode == "":
			#N =>signal failed to move
			self.error_ = "duplicatePeerNodeObjById: Cannot find node with id " + nodeId_
			return self

		# Keep track of parrentNode
		thisParrentNode = thisNode.parrentNode_			

		# Is thisNode rootNode?
		if thisParrentNode == "":
			#Y => Signal fail
			self.error_ = "duplicatePeerNodeObjById: rootNodes does not have peerNodes"
			return self		

		# Has nodeIx been specified?
		if nodeIx_ == "":
			#N => Assume thisNodes nodeIx
			nodeIx_ = thisNode.nodeIx_
		else:
			#Y => Is this ix valid?
			if nodeIx_ < 0 or nodeIx_ > thisParrentNode.lastSubNodeIx_:
				#N => Signal failed to move
				self.error_ = "duplicatePeerNodeObjById: Cannont find node with ix " + str(nodeIx_)
				return self						

		# Create copy of thisNode
		copiedNode = thisNode.copyNodeObj()

		# Assigne unique name to the new node to ensure there is no duplicae names "keys"
		ix = 0
		someNode = ""
		while(1):
			# Try next name
			newName = copiedNode.name_ + str(ix)			
			#does specified node allready Exist
			someNode = thisParrentNode.getSubNodeByName(newName)
			if someNode == "":
				#N => New valid node key found
				break

			# Update ix
			ix += 1

		# Was a valid newName found?
		if someNode == "":
			#Y => Update nodeName 
			copiedNode.name_ = newName
		else:
			#N => Signal failed to copy node
			self.error_ = "duplicateNodeObj: Failed to find a unique name for copied node"
			return self

		# Reinsert node
		thisParrentNode.insertSubNodeObjByIx(nodeIx_, copiedNode)

		# Update new nodes sub-infoTree to reflect its json object structure
		copiedNode.setValue()		

		return copiedNode	   

	# Duplicate new peerNodeObj (by value) Specified by name, Search in thisNodes peerNodes
	# use rootNode if you are unsure where the node is located
	def duplicatePeerNodeByName(self, name_, nodeIx_ = "", uniqueLevel_=-1):
		thisNode = self
				
		# Find specified node by id
		thisNode = thisNode.getPeerNodeByName(name_, uniqueLevel_)

		# Was a valid node found?
		if thisNode == "":
			#N =>signal failed to move
			self.error_ = "duplicatePeerNodeObjByName: Cannot find node with id " + name_
			return self

		# Keep track of parrentNode
		thisParrentNode = thisNode.parrentNode_			

		# Is thisNode rootNode?
		if thisParrentNode == "":
			#Y => Signal fail
			self.error_ = "duplicatePeerNodeObjByName: rootNodes does not have peerNodes"
			return self		

		# Has nodeIx been specified?
		if nodeIx_ == "":
			#N => Assume thisNodes nodeIx
			nodeIx_ = thisNode.nodeIx_
		else:
			#Y => Is this ix valid?
			if nodeIx_ < 0 or nodeIx_ > thisParrentNode.lastSubNodeIx_:
				#N => Signal failed to move
				self.error_ = "duplicatePeerNodeObjByName: Cannont find node with ix " + str(nodeIx_)
				return self						

		# Create copy of thisNode
		copiedNode = thisNode.copyNodeObj()

		# Assigne unique name to the new node to ensure there is no duplicae names "keys"
		ix = 0
		someNode = ""
		while(1):
			# Try next name
			newName = copiedNode.name_ + str(ix)			
			#does specified node allready Exist
			someNode = thisParrentNode.getSubNodeByName(newName)
			if someNode == "":
				#N => New valid node key found
				break

			# Update ix
			ix += 1

		# Was a valid newName found?
		if someNode == "":
			#Y => Update nodeName 
			copiedNode.name_ = newName
		else:
			#N => Signal failed to copy node
			self.error_ = "duplicateNodeObj: Failed to find a unique name for copied node"
			return self		

		# Reinsert node
		thisParrentNode.insertSubNodeObjByIx(nodeIx_, copiedNode)

		# Update new nodes sub-infoTree to reflect its json object structure
		copiedNode.setValue()		

		return copiedNode	

	# Duplicate new peerNodeObj (by value) Specified by value, Search in thisNodes peerNodes
	# use rootNode if you are unsure where the node is located
	def duplicatePeerNodeByValue(self, value_, nodeIx_ = "", uniqueLevel_=-1):
		thisNode = self
				
		# Find specified node by id
		thisNode = thisNode.getPeerNodeByValue(value_, uniqueLevel_)

		# Was a valid node found?
		if thisNode == "":
			#N =>signal failed to move
			self.error_ = "duplicatePeerNodeObjByValue: Cannot find node with value " + self.getString(value_)
			return self

		# Keep track of parrentNode
		thisParrentNode = thisNode.parrentNode_			

		# Is thisNode rootNode?
		if thisParrentNode == "":
			#Y => Signal fail
			self.error_ = "duplicatePeerNodeObjByName: rootNodes does not have peerNodes"
			return self		

		# Has nodeIx been specified?
		if nodeIx_ == "":
			#N => Assume thisNodes nodeIx
			nodeIx_ = thisNode.nodeIx_
		else:
			#Y => Is this ix valid?
			if nodeIx_ < 0 or nodeIx_ > thisParrentNode.lastSubNodeIx_:
				#N => Signal failed to move
				self.error_ = "duplicatePeerNodeObjByName: Cannont find node with ix " + str(nodeIx_)
				return self						

		# Create copy of thisNode
		copiedNode = thisNode.copyNodeObj()

		# Assigne unique name to the new node to ensure there is no duplicae names "keys"
		ix = 0
		someNode = ""
		while(1):
			# Try next name
			newName = copiedNode.name_ + str(ix)			
			#does specified node allready Exist
			someNode = thisParrentNode.getSubNodeByName(newName)
			if someNode == "":
				#N => New valid node key found
				break

			# Update ix
			ix += 1

		# Was a valid newName found?
		if someNode == "":
			#Y => Update nodeName 
			copiedNode.name_ = newName
		else:
			#N => Signal failed to copy node
			self.error_ = "duplicateNodeObj: Failed to find a unique name for copied node"
			return self		

		# Reinsert node
		thisParrentNode.insertSubNodeObjByIx(nodeIx_, copiedNode)

		# Update new nodes sub-infoTree to reflect its json object structure
		copiedNode.setValue()		

		return copiedNode	

	# Duplicate peerNodeObj (by value) specified by ix to specified ix, Search in thisNodes peerNodes
	# use rootNode if you are unsure where the node is located
	def duplicatePeerNodeByIx(self, oldNodeIx_, nodeIx_ = ""):
		thisNode = self
				
		# Find specified node by ix
		thisNode = thisNode.getPeerNodeByIx(oldNodeIx_)

		# Was a valid node found?
		if thisNode == "":
			#N =>signal failed to move
			self.error_ = "duplicatePeerNodeObjByIx: Cannot find node with id " + oldNodeIx_
			return self

		# Keep track of parrentNode
		thisParrentNode = thisNode.parrentNode_			

		# Is thisNode rootNode?
		if thisParrentNode == "":
			#Y => Signal fail
			self.error_ = "duplicatePeerNodeObjByIx: rootNodes does not have peerNodes"
			return self		

		# Has nodeIx been specified?
		if nodeIx_ == "":
			#N => Assume thisNodes nodeIx
			nodeIx_ = thisNode.nodeIx_
		else:
			#Y => Is this ix valid?
			if nodeIx_ < 0 or nodeIx_ > thisParrentNode.lastSubNodeIx_:
				#N => Signal failed to move
				self.error_ = "duplicatePeerNodeObjByIx: Cannont find node with ix " + str(nodeIx_)
				return self						

		# Create copy of thisNode
		copiedNode = thisNode.copyNodeObj()

		# Assigne unique name to the new node to ensure there is no duplicae names "keys"
		ix = 0
		someNode = ""
		while(1):
			# Try next name
			newName = copiedNode.name_ + str(ix)			
			#does specified node allready Exist
			someNode = thisParrentNode.getSubNodeByName(newName)
			if someNode == "":
				#N => New valid node key found
				break

			# Update ix
			ix += 1

		# Was a valid newName found?
		if someNode == "":
			#Y => Update nodeName 
			copiedNode.name_ = newName
		else:
			#N => Signal failed to copy node
			self.error_ = "duplicateNodeObj: Failed to find a unique name for copied node"
			return self

		# Reinsert node
		thisParrentNode.insertSubNodeObjByIx(nodeIx_, copiedNode)

		# Update new nodes sub-infoTree to reflect its json object structure
		copiedNode.setValue()		

		return copiedNode

#------------------- DUPLICATE subNode Helper/Wrapper METHODS (Search in thisNodes subNodes)---------
	# Duplicate subNodeObj (by value) Specified by Id to specified ix, Search in thisNodes subNodes
	# use rootNode if you are unsure where the node is located
	def duplicateSubNodeById(self, nodeId_, nodeIx_ = "", uniqueLevel_=-1):
		thisNode = self

		# Keep track of parrentNode
		thisParrentNode = thisNode

		# Find specified node by id
		thisNode = thisNode.getSubNodeById(nodeId_, uniqueLevel_)
		
		# Was a valid node found?
		if thisNode == "":
			#N =>signal failed to move
			self.error_ = "duplicateSubNodeObjById: Cannot find node with id " + nodeId_
			return self

		# Is thisNode a leafNode?
		if thisParrentNode.lastSubNodeIx_ == -1:
			#Y => Signal failed to move
			self.error_ = "duplicateSubNodeObjById: leafNodes does not have subNodes"
			return self			

		# Has nodeIx been specified?
		if nodeIx_ == "":
			#N => Assume thisNodes nodeIx
			nodeIx_ = thisNode.nodeIx_
		else:
			#Y => Is this ix valid?
			if nodeIx_ < 0 or nodeIx_ > thisParrentNode.lastSubNodeIx_:
				#N => Signal failed to move
				self.error_ = "duplicateSubNodeObjById: Cannont find node with ix " + str(nodeIx_)
				return self						

		# Create copy of thisNode
		copiedNode = thisNode.copyNodeObj()

		# Assigne unique name to the new node to ensure there is no duplicae names "keys"
		ix = 0
		someNode = ""
		while(1):
			# Try next name
			newName = copiedNode.name_ + str(ix)			
			#does specified node allready Exist
			someNode = thisParrentNode.getSubNodeByName(newName)
			if someNode == "":
				#N => New valid node key found
				break

			# Update ix
			ix += 1

		# Was a valid newName found?
		if someNode == "":
			#Y => Update nodeName 
			copiedNode.name_ = newName
		else:
			#N => Signal failed to copy node
			self.error_ = "duplicateNodeObj: Failed to find a unique name for copied node"
			return self
		
		# Reinsert node
		thisParrentNode.insertSubNodeObjByIx(nodeIx_, copiedNode)

		# Update new nodes sub-infoTree to reflect its json object structure
		copiedNode.setValue()		

		return copiedNode		   

	# Duplicate subNodeObj (by value) Specified by name, Search in thisNodes subNodes
	# use rootNode if you are unsure where the node is located
	def duplicateSubNodeByName(self, name_, nodeIx_ = "", uniqueLevel_=-1):
		thisNode = self

		# Keep track of parrentNode
		thisParrentNode = thisNode

		# Find specified node by id
		thisNode = thisNode.getSubNodeByName(name_, uniqueLevel_)
		
		# Was a valid node found?
		if thisNode == "":
			#N =>signal failed to move
			self.error_ = "duplicateSubNodeObjByName: Cannot find node with id " + name_
			return self


		# Is thisNode a leafNode?
		if thisParrentNode.lastSubNodeIx_ == -1:
			#Y => Signal failed to move
			self.error_ = "duplicateSubNodeObjByName: leafNodes does not have subNodes"
			return self			

		# Has nodeIx been specified?
		if nodeIx_ == "":
			#N => Assume thisNodes nodeIx
			nodeIx_ = thisNode.nodeIx_
		else:
			#Y => Is this ix valid?
			if nodeIx_ < 0 or nodeIx_ > thisParrentNode.lastSubNodeIx_:
				#N => Signal failed to move
				self.error_ = "duplicateSubNodeObjByName: Cannont find node with ix " + str(nodeIx_)
				return self						

		# Create copy of thisNode
		copiedNode = thisNode.copyNodeObj()

		# Assigne unique name to the new node to ensure there is no duplicae names "keys"
		ix = 0
		someNode = ""
		while(1):
			# Try next name
			newName = copiedNode.name_ + str(ix)			
			#does specified node allready Exist
			someNode = thisParrentNode.getSubNodeByName(newName)
			if someNode == "":
				#N => New valid node key found
				break

			# Update ix
			ix += 1

		# Was a valid newName found?
		if someNode == "":
			#Y => Update nodeName 
			copiedNode.name_ = newName
		else:
			#N => Signal failed to copy node
			self.error_ = "duplicateNodeObj: Failed to find a unique name for copied node"
			return self
		
		# Reinsert node
		thisParrentNode.insertSubNodeObjByIx(nodeIx_, copiedNode)

		# Update new nodes sub-infoTree to reflect its json object structure
		copiedNode.setValue()		

		return copiedNode	

	# Duplicate subNodeObj (by value) Specified by value, Search in thisNodes subNodes
	# use rootNode if you are unsure where the node is located
	def duplicateSubNodeByValue(self, value_, nodeIx_ = "", uniqueLevel_=-1):
		thisNode = self

		# Keep track of parrentNode
		thisParrentNode = thisNode

		# Find specified node by id
		thisNode = thisNode.getSubNodeByValue(value_, uniqueLevel_)
		
		# Was a valid node found?
		if thisNode == "":
			#N =>signal failed to move
			self.error_ = "duplicateSubNodeObjByValue: Cannot find node with value " + self.getString(value_)
			return self


		# Is thisNode a leafNode?
		if thisParrentNode.lastSubNodeIx_ == -1:
			#Y => Signal failed to move
			self.error_ = "duplicateSubNodeObjByValue: leafNodes does not have subNodes"
			return self			

		# Has nodeIx been specified?
		if nodeIx_ == "":
			#N => Assume thisNodes nodeIx
			nodeIx_ = thisNode.nodeIx_
		else:
			#Y => Is this ix valid?
			if nodeIx_ < 0 or nodeIx_ > thisParrentNode.lastSubNodeIx_:
				#N => Signal failed to move
				self.error_ = "duplicateSubNodeObjByValue: Cannont find node with ix " + str(nodeIx_)
				return self						

		# Create copy of thisNode
		copiedNode = thisNode.copyNodeObj()

		# Assigne unique name to the new node to ensure there is no duplicae names "keys"
		ix = 0
		someNode = ""
		while(1):
			# Try next name
			newName = copiedNode.name_ + str(ix)			
			#does specified node allready Exist
			someNode = thisParrentNode.getSubNodeByName(newName)
			if someNode == "":
				#N => New valid node key found
				break

			# Update ix
			ix += 1

		# Was a valid newName found?
		if someNode == "":
			#Y => Update nodeName 
			copiedNode.name_ = newName
		else:
			#N => Signal failed to copy node
			self.error_ = "duplicateNodeObjByValue: Failed to find a unique name for copied node"
			return self
		
		# Reinsert node
		thisParrentNode.insertSubNodeObjByIx(nodeIx_, copiedNode)

		# Update new nodes sub-infoTree to reflect its json object structure
		copiedNode.setValue()		

		return copiedNode	

	# Relocate subNodeObj (by value) specified by ix, Search in thisNodes subNodes
	# use rootNode if you are unsure where the node is located
	def duplicateSubNodeByIx(self, oldNodeIx_, nodeIx_ = ""):
		thisNode = self

		# Keep track of parrentNode
		thisParrentNode = thisNode

		# Find specified node by id
		thisNode = thisNode.getSubNodeByIx(oldNodeIx_)
		
		# Was a valid node found?
		if thisNode == "":
			#N =>signal failed to move
			self.error_ = "duplicateSubNodeObjByIx: Cannot find node with ix " + oldNodeIx_
			return self

		# Is thisNode a leafNode?
		if thisParrentNode.lastSubNodeIx_ == -1:
			#Y => Signal failed to move
			self.error_ = "duplicateSubNodeObjByIx: leafNodes does not have subNodes"
			return self			

		# Has nodeIx been specified?
		if nodeIx_ == "":
			#N => Assume thisNodes nodeIx
			nodeIx_ = thisNode.nodeIx_
		else:
			#Y => Is this ix valid?
			if nodeIx_ < 0 or nodeIx_ > thisParrentNode.lastSubNodeIx_:
				#N => Signal failed to move
				self.error_ = "duplicateSubNodeObjByIx: Cannont find node with ix " + str(nodeIx_)
				return self						

		# Create copy of thisNode
		copiedNode = thisNode.copyNodeObj()

		# Assigne unique name to the new node to ensure there is no duplicae names "keys"
		ix = 0
		someNode = ""
		while(1):
			# Try next name
			newName = copiedNode.name_ + str(ix)			
			#does specified node allready Exist
			someNode = thisParrentNode.getSubNodeByName(newName)
			if someNode == "":
				#N => New valid node key found
				break

			# Update ix
			ix += 1

		# Was a valid newName found?
		if someNode == "":
			#Y => Update nodeName 
			copiedNode.name_ = newName
		else:
			#N => Signal failed to copy node
			self.error_ = "duplicateNodeObj: Failed to find a unique name for copied node"
			return self
		
		# Reinsert node
		thisParrentNode.insertSubNodeObjByIx(nodeIx_, copiedNode)

		# Update new nodes sub-infoTree to reflect its json object structure
		copiedNode.setValue()		

		return copiedNode

#------------------- Gloabl Search methods (Search from thisNode to end of sub-infoTree)-----------------------------------
	# Find node with specifed nodeId (id), relative search from thisNode to end of its sub-infoTree
	# use rootNode if you are unsure about where the node is located
	def findNodeById(self, nodeId_, caseSensitive=0, startNode_ = ""):
		thisNode = self
		startNode = startNode_

		# Has startNode been specified?
		if startNode_ == "":
			#N => Assume thisNodes parrentNode
			startNode = thisNode.parrentNode_
		
		# Search for the Node with the specified NodeId in this Nodes sub-Tree
		while(thisNode != ""):
		
			# is this caseSesnsitive search?
			if(caseSensitive == 0):					 
				# Is This the node we are looking for?
				if(thisNode.nodeId_.lower() == nodeId_.lower()):
					# Node found retun it
					return thisNode
			else: # Assume case sensitive search
				# Is This the node we are looking for?
				if(thisNode.nodeId_ == nodeId_):
					# Node found retun it
					return thisNode				   
			
			# Get Next Node
			thisNode = thisNode.getNextNode(startNode)
		
		# Assume the node was not found
		self.error_ = "findNodeById: Unable to find the node with Id " + nodeId_
		return ""

	# Find node with specifed item (key:value), relative search from thisNode to end of its sub-infoTree
	# use rootNode if you are unsure about where the node is located
	# STATUS: TESTED->OK
	def findNodeByItem(self, name_, value_, caseSensitive=0, startNode_ = ""):
		thisNode = self
		startNode = startNode_

		# Has startNode been specified?
		if startNode_ == "":
			#N => Assume thisNodes parrentNode
			startNode = thisNode.parrentNode_		
		
		# Search for the Node with the specified key:value in this Nodes sub-Tree
		while(thisNode != ""):
			# Is this the Item we are looking for?
			
			# reset trackingNode
			thisTrackingNode = trackingNode(name_, value_)

			# Get items
			thisItem = thisTrackingNode.value_
			someItem = thisNode.item_

			# Is thisNode a simpleLeafNode?
			if thisNode.isSimpleLeafNode():
				#Y =>
				# Get string representation of items
				thisItem = thisTrackingNode.getString()
				someItem = thisNode.getString()

				# Is thisItem a simple leafNode?, hence does object type match
				if thisTrackingNode.isSimpleLeafNode():
					#Y => Does thisNode contain the item we are looking for?
					# is this caseSesnsitive search?
					if(caseSensitive == 0):					 
						#N => Is This the node we are looking for?
						if (thisNode.name_.lower() == name_.lower()):
							if (thisItem.lower() == someItem.lower()):
								#Y => Node found retun it
								return thisNode
					else: # Assume case sensitive search
						#Y => Is This the node we are looking for?
						if(thisNode.name_ == name_):
							if(thisItem == someItem):
								#Y => Node found retun it
								return thisNode

			# Is thisNode a OrderedDict Object?
			if thisNode.isOrderedDict():
				#Y => Is thisItem a OrderedDict Object?, hence does object type match
				if thisTrackingNode.isOrderedDict():
					# Is ths casseSensitive search?
					if(caseSensitive == 0):
						#N => Does thisNode contain the item we are looking for?
						if(thisNode.name_.lower() == name_.lower()):
							if(thisItem == someItem):
								#Y => Node found return it
								return thisNode
					else:
						#Y => Assume case sensitive search
						# Does thisNode contain the item we are looking for?
						if(thisNode.name_ == name_):
							if(thisItem == someItem):
								#Y => Node found return it
								return thisNode

			# Is thisNode a list Object?
			if thisNode.isList():
				#Y => Is thisItem a list Object, hence does object type match?
				if thisTrackingNode.isList():
					# Is ths casseSensitive search?
					if(caseSensitive == 0):
						#N => Does thisNode contain the item we are looking for?
						if(thisNode.name_.lower() == name_.lower()):
							if(thisItem == someItem):
								#Y => Node found return it
								return thisNode
					else:
						#Y => Assume case sensitive search
						# Does thisNode contain the item we are looking for?
						if(thisNode.name_ == name_):
							if(thisItem == someItem):
								#Y => Node found return it
								return thisNode											
					
			# Get Next Node
			thisNode = thisNode.getNextNode(startNode)
		
		# Assume the node was not found
		self.error_ = "findNodeByItem: Unable to find the node with Key:value " + self.getString(value_)
		return ""		

	# Same as findNodeById, but uses the get/set method naming convention
	# Searches relative from thisNode and to end of its sub-infoTree
	# use rootNode if you are unsure about where the node is
	def getNodeById(self, nodeId_, caseSensitive=0, startNode_ = ""):
		thisNode = self
		startNode = startNode_

		# Has startNode been specified?
		if startNode_ == "":
			#N => Assume thisNodes parrentNode
			startNode = thisNode.parrentNode_		

		# Search for the Node with the specified NodeId in this Nodes sub-Tree
		while(thisNode != ""):
		
			# is this caseSesnsitive search?
			if(caseSensitive == 0):					 
				# Is This the node we are looking for?
				if(thisNode.nodeId_.lower() == nodeId_.lower()):
					# Node found retun it
					return thisNode
			else: # Assume case sensitive search
				# Is This the node we are looking for?
				if(thisNode.nodeId_ == nodeId_):
					# Node found retun it
					return thisNode				   
			
			# Get Next Node
			thisNode = thisNode.getNextNode(startNode)
		
		# Assume the node was not found
		self.error_ = "getNodeById: Unable to find the node with Id " + nodeId_		   
		return ""		 

	# Find node with specifed item (key:value), relative search from thisNode to end of its sub-infoTree
	# use rootNode if you are unsure about where the node is located
	# STATUS: TESTED->OK
	def getNodeByItem(self, name_, value_, caseSensitive=0, startNode_ = ""):
		thisNode = self
		startNode = startNode_

		# Has startNode been specified?
		if startNode_ == "":
			#N => Assume thisNodes parrentNode
			startNode = thisNode.parrentNode_		
		
		# Search for the Node with the specified key:value in this Nodes sub-Tree
		while(thisNode != ""):
			# Is this the Item we are looking for?
			
			# reset trackingNode
			thisTrackingNode = trackingNode(name_, value_)

			# Get items
			thisItem = thisTrackingNode.value_
			someItem = thisNode.item_

			# Is thisNode a simpleLeafNode?
			if thisNode.isSimpleLeafNode():
				#Y =>
				# Get string representation of items
				thisItem = thisTrackingNode.getString()
				someItem = thisNode.getString()

				# Is thisItem a simple leafNode?, hence does object type match
				if thisTrackingNode.isSimpleLeafNode():
					#Y => Does thisNode contain the item we are looking for?
					# is this caseSesnsitive search?
					if(caseSensitive == 0):					 
						#N => Is This the node we are looking for?
						if (thisNode.name_.lower() == name_.lower()):
							if (thisItem.lower() == someItem.lower()):
								#Y => Node found retun it
								return thisNode
					else: # Assume case sensitive search
						#Y => Is This the node we are looking for?
						if(thisNode.name_ == name_):
							if(thisItem == someItem):
								#Y => Node found retun it
								return thisNode

			# Is thisNode a OrderedDict Object?
			if thisNode.isOrderedDict():
				#Y => Is thisItem a OrderedDict Object?, hence does object type match
				if thisTrackingNode.isOrderedDict():
					# Is ths casseSensitive search?
					if(caseSensitive == 0):
						#N => Does thisNode contain the item we are looking for?
						if(thisNode.name_.lower() == name_.lower()):
							if(thisItem == someItem):
								#Y => Node found return it
								return thisNode
					else:
						#Y => Assume case sensitive search
						# Does thisNode contain the item we are looking for?
						if(thisNode.name_ == name_):
							if(thisItem == someItem):
								#Y => Node found return it
								return thisNode

			# Is thisNode a list Object?
			if thisNode.isList():
				#Y => Is thisItem a list Object, hence does object type match?
				if thisTrackingNode.isList():
					# Is ths casseSensitive search?
					if(caseSensitive == 0):
						#N => Does thisNode contain the item we are looking for?
						if(thisNode.name_.lower() == name_.lower()):
							if(thisItem == someItem):
								#Y => Node found return it
								return thisNode
					else:
						#Y => Assume case sensitive search
						# Does thisNode contain the item we are looking for?
						if(thisNode.name_ == name_):
							if(thisItem == someItem):
								#Y => Node found return it
								return thisNode											
					
			# Get Next Node
			thisNode = thisNode.getNextNode(startNode)
		
		# Assume the node was not found
		self.error_ = "getNodeByItem: Unable to find the node with Key:value " + self.getString(value_)
		return ""

	# Find first node with specifed name, relative search from thisNode to end of its sub-infoTree
	# Use rootNode if your are unsure where the node is located
	def findNodeByName(self, name_, caseSensitive=0, startNode_ = ""):
		thisNode = self
		startNode = startNode_

		# Has startNode been specified?
		if startNode_ == "":
			#N => Assume thisNodes parrentNode
			startNode = thisNode.parrentNode_		
			
		# Search for the Node with the specified NodeId in this Nodes sub-Tree
		while(thisNode != ""):
		
			# is this caseSesnsitive search?
			if(caseSensitive == 0):					 
				# Is This the node we are looking for?
				if(thisNode.name_.lower() == name_.lower()):
					# Node found retun it
					return thisNode
			else: # Assume case sensitive search
				# Is This the node we are looking for?
				if(thisNode.name_ == name_):
					# Node found retun it
					return thisNode				   
			
			# Get Next Node
			thisNode = thisNode.getNextNode(startNode)
		
		# Assume the node was not found
		self.error_ = "findNodeByName: Unable to find the node with name " + name_		  
		return ""

	# Find first node with specifed name, relative search from thisNode to end of its sub-infoTree
	# Use rootNode if your are unsure where the node is located
	# STATUS: TESTED->OK
	def getNodeByName(self, name_, caseSensitive=0, startNode_ = ""):
		thisNode = self
		startNode = startNode_

		# Has startNode been specified?
		if startNode_ == "":
			#N => Assume thisNodes parrentNode
			startNode = thisNode.parrentNode_		
		
		# Search for the Node with the specified NodeId in this Nodes sub-Tree
		while(thisNode != ""):
		
			# is this caseSesnsitive search?
			if(caseSensitive == 0):					 
				# Is This the node we are looking for?
				if(thisNode.name_.lower() == name_.lower()):
					# Node found retun it
					return thisNode
			else: # Assume case sensitive search
				# Is This the node we are looking for?
				if(thisNode.name_ == name_):
					# Node found retun it
					return thisNode				   
			
			# Get Next Node
			thisNode = thisNode.getNextNode(startNode)
		
		# Assume the node was not found
		self.error_ = "getNodeByName: Unable to find the node with name " + name_		 
		return ""		 

	# Finds first node with specified value "item_"
	# Searches relative from thisNode to end of its sub-infoTree
	# Use rootNode if you are unsure where the value is located
	# Can be used to detect wether a given value has allready be added to node tree when handling uniqe data.
	# TODO: Add case sensitive check to value compare
	def findNodeByValue(self, value_, caseSensitive=0, startNode_ = ""):
		thisNode = self
		startNode = startNode_

		# Has startNode been specified?
		if startNode == "":
			#N => Assume thisNodes parrentNode "sub-infoTree"
			startNode = thisNode.parrentNode_		
				
		# Search for the Node with the specified Value in this Nodes sub-Tree
		while(thisNode != ""):
			# Is this the node we are looking for?
			# Is thisNode and value a ordered dict object
			if thisNode.isOrderedDict() and thisNode.isOrderedDict(value_):
				#Y => Is this the value we are looking for
				if thisNode.item_ == value_:
					#Y
					return thisNode

			# Is thisNode and value a list object
			if thisNode.isList() and thisNode.isList(value_):
				#Y => Is this the value we are looking for
				if thisNode.item_ == value_:
					#Y
					return thisNode

			# Is thisNode and value a string
			if thisNode.isString() and thisNode.isString(value_):
				#Y => Is this the value we are looking for
				if(thisNode.item_.lower() == value_.lower()):
					#Y
					return thisNode

			# Is thisNode and value a number
			if thisNode.isNumber() and thisNode.isNumber(value_):
				#Y => Is this the value we are looking for
				if thisNode.item_ == value_:
					#Y
					return thisNode

			# Get next node
			thisNode = thisNode.getNextNode(startNode)
		
		# Assume the node was not found, values dataType is unknowns so we will let the expcition handler "getString" handle it
		self.error_ = "findNodeByValue: Unable to find a node->value " + self.getString(item_) + " in " + startNode.name_ + " sub-infoTree"		   
		return ""

	# Finds first node with specified value "item_"
	# Searches relative from thisNode to end of its sub-infoTree
	# Use rootNode if you are unsure where the value is located
	# Can be used to detect wether a given value has allready be added to node tree when handling uniqe data.
	# STATUS: TESTED->OK
	# TODO: Add case sensitive check to value compare 	   
	def getNodeByValue(self, value_, caseSensitive=0, startNode_ = ""):
		thisNode = self
		startNode = startNode_

		# Has startNode been specified?
		if startNode == "":
			#N => Assume thisNodes parrentNode
			startNode = thisNode.parrentNode_		
				
		# Search for the Node with the specified Value in this Nodes sub-Tree
		while(thisNode != ""):
			# Is this the node we are looking for?
			# Is thisNode and value a ordered dict object
			if thisNode.isOrderedDict() and thisNode.isOrderedDict(value_):
				#Y => Is this the value we are looking for
				if thisNode.item_ == value_:
					#Y
					return thisNode

			# Is thisNode and value a list object
			if thisNode.isList() and thisNode.isList(value_):
				#Y => Is this the value we are looking for
				if thisNode.item_ == value_:
					#Y
					return thisNode

			# Is thisNode and value a string
			if thisNode.isString() and thisNode.isString(value_):
				#Y => Is this the value we are looking for
				if(thisNode.item_.lower() == value_.lower()):
					#Y
					return thisNode

			# Is thisNode and value a number
			if thisNode.isNumber() and thisNode.isNumber(value_):
				#Y => Is this the value we are looking for
				if thisNode.item_ == value_:
					#Y
					return thisNode

			# Get next node
			thisNode = thisNode.getNextNode(startNode)
		
		# Assume the node was not found
		self.error_ = "getNodeByValue: Unable to find a node->value " + self.getString(item_) + " in " + startNode.name_ + " sub-infoTree"		  
		return ""

#----------------- peerNode Search methods (Search in thisNodes peerNodes)--------------
	# Same as getNodeById, but only searches on peerNodes of thisNode
	# Searches relative from first childNode  to last childNode
	# use rootNode if you are unsure about where the node is
	def getPeerNodeById(self, nodeId_, caseSensitive=0):
		thisNode = self
		thisParrentNode = thisNode.parrentNode_

		# Is thisNode rootNode?
		if thisParrentNode == "":
			#Y => Signal attempt to search peerNodes on a root node
			thisNode.error_ = "getPeerNodeById: rootNodes dont have peerNodes"
			return ""

		# Search for the Node with the specified NodeId in this Nodes sub-Tree
		for node in thisParrentNode.subNodes_:		
			# is this caseSesnsitive search?
			if(caseSensitive == 0):					 
				# Is This the node we are looking for?
				if(node.nodeId_.lower() == nodeId_.lower()):
					# Node found retun it
					return node
			else: # Assume case sensitive search
				# Is This the node we are looking for?
				if(node.nodeId_ == nodeId_):
					# Node found retun it
					return node				   
					
		# Assume the node was not found
		self.error_ = "getPeerNodeById: Unable to find the peerNode with Id " + nodeId_		   
		return ""		

	# Find peerNode with specifed item (key:value), relative search from peerNodes of thisNode
	# use rootNode if you are unsure about where the node is located
	# STATUS: TESTED->OK	
	def getPeerNodeByItem(self, name_, value_, caseSensitive=0):
		thisNode = self
		thisParrentNode = thisNode.parrentNode_

		# Is thisNode a rootNode?
		if thisNode.parrentNode_ == "":
			#Y => Signal failed to get peerNode
			self.error_ = "getPeerNodeByItem: rootNodes does not have peerNodes"
			return ""		
		
		# Search for the Node with the specified key:value in this Nodes sub-Tree
		for node in thisParrentNode.subNodes_:
			# Is this the Item we are looking for?
			
			# reset trackingNode
			thisTrackingNode = trackingNode(name_, value_)

			# Get items
			thisItem = thisTrackingNode.value_
			someItem = node.item_

			# Is thisNode a simpleLeafNode?
			if node.isSimpleLeafNode():
				#Y =>
				# Get string representation of items
				thisItem = thisTrackingNode.getString()
				someItem = node.getString()

				# Is thisItem a simple leafNode?, hence does object type match
				if thisTrackingNode.isSimpleLeafNode():
					#Y => Does thisNode contain the item we are looking for?
					# is this caseSesnsitive search?
					if(caseSensitive == 0):					 
						#N => Is This the node we are looking for?
						if (node.name_.lower() == name_.lower()):
							if (thisItem.lower() == someItem.lower()):
								#Y => Node found retun it
								return node
					else: # Assume case sensitive search
						#Y => Is This the node we are looking for?
						if(node.name_ == name_):
							if(thisItem == someItem):
								#Y => Node found retun it
								return node

			# Is thisNode a OrderedDict Object?
			if node.isOrderedDict():
				#Y => Is thisItem a OrderedDict Object?, hence does object type match
				if thisTrackingNode.isOrderedDict():
					# Is ths casseSensitive search?
					if(caseSensitive == 0):
						#N => Does thisNode contain the item we are looking for?
						if(node.name_.lower() == name_.lower()):
							if(thisItem == someItem):
								#Y => Node found return it
								return node
					else:
						#Y => Assume case sensitive search
						# Does thisNode contain the item we are looking for?
						if(thisNode.name_ == name_):
							if(thisItem == someItem):
								#Y => Node found return it
								return node

			# Is thisNode a list Object?
			if node.isList():
				#Y => Is thisItem a list Object, hence does object type match?
				if thisTrackingNode.isList():
					# Is ths casseSensitive search?
					if(caseSensitive == 0):
						#N => Does thisNode contain the item we are looking for?
						if(node.name_.lower() == name_.lower()):
							if(thisItem == someItem):
								#Y => Node found return it
								return node
					else:
						#Y => Assume case sensitive search
						# Does thisNode contain the item we are looking for?
						if(node.name_ == name_):
							if(thisItem == someItem):
								#Y => Node found return it
								return node											
		
		# Assume the node was not found
		self.error_ = "getPeerNodeByItem: Unable to find the node with Key:value " + self.getString(value_)
		return ""

	# Find thisNodes peerNode by Id
	#TODO: Implement this any value check method in other find by value methods!! (OK)
	def findPeerNodeById(self, nodeId_, caseSensitive=0):
		thisNode = self
		thisParrentNode = thisNode.parrentNode_

		# Is this rootNode?
		if(thisNode.parrentNode_ ==""):
			# YES => rootNode does not have peerNodes
			self.error_ = "findPeerNodeById: rootNodes dont have peerNodes!!"			 
			return ""
		
		for node in thisParrentNode.subNodes_:
			# Is this caseSenstive search?
			if(caseSensitive == 0):
				# Is this the peerNode we are looking for?
				if(node.nodeId_.lower() == nodeId_.lower()):
					return node
			else: # Assume case senstive search
				if(node.nodeId_ == nodeId_):
					return node

		# Assume the peerNode did not exist
		self.error_ = "findPeerNodeById: Unable to find peerNode with Id" + nodeId_		   
		return ""

	# Find peerNode with specifed item (key:value), relative search from peerNodes of thisNode
	# use rootNode if you are unsure about where the node is located
	# STATUS: TESTED->OK	
	def findPeerNodeByItem(self, name_, value_, caseSensitive=0):
		thisNode = self
		thisParrentNode = thisNode.parrentNode_

		# Is thisNode a rootNode?
		if thisNode.parrentNode_ == "":
			#Y => Signal failed to get peerNode
			self.error_ = "findPeerNodeByItem: rootNodes does not have peerNodes"
			return ""		

		# Search for the Node with the specified key:value in this Nodes sub-Tree
		for node in thisParrentNode.subNodes_:
			# Is this the Item we are looking for?
			
			# reset trackingNode
			thisTrackingNode = trackingNode(name_, value_)

			# Get items
			thisItem = thisTrackingNode.value_
			someItem = node.item_

			# Is thisNode a simpleLeafNode?
			if node.isSimpleLeafNode():
				#Y =>
				# Get string representation of items
				thisItem = thisTrackingNode.getString()
				someItem = node.getString()

				# Is thisItem a simple leafNode?, hence does object type match
				if thisTrackingNode.isSimpleLeafNode():
					#Y => Does thisNode contain the item we are looking for?
					# is this caseSesnsitive search?
					if(caseSensitive == 0):					 
						#N => Is This the node we are looking for?
						if (node.name_.lower() == name_.lower()):
							if (thisItem.lower() == someItem.lower()):
								#Y => Node found retun it
								return node
					else: # Assume case sensitive search
						#Y => Is This the node we are looking for?
						if(node.name_ == name_):
							if(thisItem == someItem):
								#Y => Node found retun it
								return node

			# Is thisNode a OrderedDict Object?
			if node.isOrderedDict():
				#Y => Is thisItem a OrderedDict Object?, hence does object type match
				if thisTrackingNode.isOrderedDict():
					# Is ths casseSensitive search?
					if(caseSensitive == 0):
						#N => Does thisNode contain the item we are looking for?
						if(node.name_.lower() == name_.lower()):
							if(thisItem == someItem):
								#Y => Node found return it
								return node
					else:
						#Y => Assume case sensitive search
						# Does thisNode contain the item we are looking for?
						if(thisNode.name_ == name_):
							if(thisItem == someItem):
								#Y => Node found return it
								return node

			# Is thisNode a list Object?
			if node.isList():
				#Y => Is thisItem a list Object, hence does object type match?
				if thisTrackingNode.isList():
					# Is ths casseSensitive search?
					if(caseSensitive == 0):
						#N => Does thisNode contain the item we are looking for?
						if(node.name_.lower() == name_.lower()):
							if(thisItem == someItem):
								#Y => Node found return it
								return node
					else:
						#Y => Assume case sensitive search
						# Does thisNode contain the item we are looking for?
						if(node.name_ == name_):
							if(thisItem == someItem):
								#Y => Node found return it
								return node											
		
		# Assume the node was not found
		self.error_ = "findPeerNodeByItem: Unable to find the node with Key:value " + self.getString(value_)
		return ""

	# Same as getNodeByName, but only searches on peerNodes of thisNode
	# Searches relative from first childNode  to last childNode
	# use rootNode if you are unsure about where the node is
	def getPeerNodeByName(self, name_, caseSensitive=0):
		thisNode = self
		thisParrentNode = thisNode.parrentNode_

		# Is thisNode rootNode?
		if thisParrentNode == "":
			#Y => Signal attempt to search peerNodes on a root node
			thisNode.error_ = "getPeerNodeByName: rootNodes dont have peerNodes"
			return ""

		# Search for the Node with the specified NodeId in this Nodes sub-Tree
		for node in thisParrentNode.subNodes_:		
			# is this caseSesnsitive search?
			if(caseSensitive == 0):					 
				# Is This the node we are looking for?
				if(node.name_.lower() == name_.lower()):
					# Node found retun it
					return node
			else: # Assume case sensitive search
				# Is This the node we are looking for?
				if(node.name_ == name_):
					# Node found retun it
					return node				   
					
		# Assume the node was not found
		self.error_ = "getPeerNodeByName: Unable to find the peerNode with Name " + name_		   
		return ""		

	# Same as getNodeByName, but only searches on peerNodes of thisNode
	# Searches relative from first childNode  to last childNode
	# use rootNode if you are unsure about where the node is
	def findPeerNodeByName(self, name_, caseSensitive=0):
		thisNode = self
		thisParrentNode = thisNode.parrentNode_

		# Is thisNode rootNode?
		if thisParrentNode == "":
			#Y => Signal attempt to search peerNodes on a root node
			thisNode.error_ = "findPeerNodeByName: rootNodes dont have peerNodes"
			return ""

		# Search for the Node with the specified NodeId in this Nodes sub-Tree
		for node in thisParrentNode.subNodes_:		
			# is this caseSesnsitive search?
			if(caseSensitive == 0):					 
				# Is This the node we are looking for?
				if(node.name_.lower() == name_.lower()):
					# Node found retun it
					return node
			else: # Assume case sensitive search
				# Is This the node we are looking for?
				if(node.name_ == name_):
					# Node found retun it
					return node				   
					
		# Assume the node was not found
		self.error_ = "findPeerNodeByName: Unable to find the peerNode with Name " + name_		   
		return ""

# Same as getNodeByIx, but only searches on peerNodes of thisNode
	# Searches relative from first childNode  to last childNode
	# use rootNode if you are unsure about where the node is
	def getPeerNodeByIx(self, nodeIx_):
		thisNode = self
		thisParrentNode = thisNode.parrentNode_

		# Is thisNode rootNode?
		if thisParrentNode == "":
			#Y => Signal attempt to search peerNodes on a root node
			thisNode.error_ = "getPeerNodeByIx: rootNodes dont have peerNodes"
			return ""

		# Is specified childNode ix valid?
		if nodeIx_ < 0 or nodeIx_ > thisParrentNode.lastSubNodeIx_:
			#N => Signal invalid childNode ix
			thisNode.error_ = "getPeerNodeByIx: Specified ix " + str(nodeIx_) + " is not valid, last childNode Ix of parrentNode" + thisParrentNode.name_ + " is " + str(thisParrentNode.lastSubNodeIx_)
			return thisNode
		
		# Assum the ix was valid
		# Return specified peerNode
		return thisParrentNode.subNodes_[nodeIx_]

	# Finds first node with specified value
	# Searches relative in thisNodes subNodes
	# Can be used to detect wether a given value has allready be added to node tree when handling uniqe data.
	# TODO: Implement caseSenstive option (OK)
	def findPeerNodeByValue(self, item_, caseSensitive=0):
		thisNode = self
		thisParrentNode = thisNode.parrentNode_

		# Is this rootNode?
		if(thisNode.parrentNode_ == ""):
			# YES => rootNode dont have peerNodes
			self.error_ = "findPeerNodeByValue: rootNodes dont have peerNodes!!"			  
			return ""

		# Find the subNode
		# Search for the specifed subNode->value
		for node in thisParrentNode.subNodes_:
			# reset trackingNode
			thisTrackingNode = trackingNode("", item_)

			# Get items
			thisItem = thisTrackingNode.value_
			someItem = node.item_

			# Is thisNode a simpleLeafNode?
			if node.isSimpleLeafNode():
				#Y =>
				# Get string representation of items
				thisItem = thisTrackingNode.getValueString()
				someItem = node.getValueString()

				# Is thisItem a simple leafNode?, hence does object type match
				if thisTrackingNode.isSimpleLeafNode():
					#Y => Does thisNode contain the item we are looking for?
					# is this caseSesnsitive search?
					if(caseSensitive == 0):					 
						#N => Is This the node we are looking for?
						if (thisItem.lower() == someItem.lower()):
							#Y => Node found retun it
							return thisNode
					else: # Assume case sensitive search
						#Y => Is This the node we are looking for?
						if(thisItem == someItem):
							#Y => Node found retun it
							return thisNode

			# Is thisNode a OrderedDict Object?
			if node.isOrderedDict():
				#Y => Is thisItem a OrderedDict Object?, hence does object type match
				if thisTrackingNode.isOrderedDict():
					#Y => Does thisNode contain the item we are looking for?
					if(thisItem == someItem):
						#Y => Node found return it
						return thisNode

			# Is thisNode a list Object?
			if node.isList():
				#Y => Is thisItem a list Object, hence does object type match?
				if thisTrackingNode.isList():
					#Y => Does thisNode contain the item we are looking for?
					if(thisItem == someItem):
						#Y => Node found return it
						return thisNode

		# Assume the node was not found
		self.error_ = "findPeerNodeByValue: Unable to find the node with value " + self.getString(item_)		   
		return ""

	# Finds first peerNode with specified value
	# Searches relative in thisNodes peerNodes
	# Can be used to detect wether a given value has allready be added to node tree when handling uniqe data.
	# TODO: Implement caseSenstive option (OK)
	def getPeerNodeByValue(self, item_, caseSensitive=0):
		thisNode = self
		thisParrentNode = thisNode.parrentNode_

		# Is this rootNode?
		if(thisNode.parrentNode_ == ""):
			# YES => rootNode dont have peerNodes
			self.error_ = "getPeerNodeByValue: rootNodes dont have peerNodes!!"			  
			return ""

		# Find the subNode
		# Search for the specifed subNode->value
		for node in thisParrentNode.subNodes_:
			# reset trackingNode
			thisTrackingNode = trackingNode("", item_)

			# Get items
			thisItem = thisTrackingNode.value_
			someItem = node.item_

			# Is thisNode a simpleLeafNode?
			if node.isSimpleLeafNode():
				#Y =>
				# Get string representation of items
				thisItem = thisTrackingNode.getValueString()
				someItem = node.getValueString()

				# Is thisItem a simple leafNode?, hence does object type match
				if thisTrackingNode.isSimpleLeafNode():
					#Y => Does thisNode contain the item we are looking for?
					# is this caseSesnsitive search?
					if(caseSensitive == 0):					 
						#N => Is This the node we are looking for?
						if (thisItem.lower() == someItem.lower()):
							#Y => Node found retun it
							return thisNode
					else: # Assume case sensitive search
						#Y => Is This the node we are looking for?
						if(thisItem == someItem):
							#Y => Node found retun it
							return thisNode

			# Is thisNode a OrderedDict Object?
			if node.isOrderedDict():
				#Y => Is thisItem a OrderedDict Object?, hence does object type match
				if thisTrackingNode.isOrderedDict():
					#Y => Does thisNode contain the item we are looking for?
					if(thisItem == someItem):
						#Y => Node found return it
						return thisNode

			# Is thisNode a list Object?
			if node.isList():
				#Y => Is thisItem a list Object, hence does object type match?
				if thisTrackingNode.isList():
					#Y => Does thisNode contain the item we are looking for?
					if(thisItem == someItem):
						#Y => Node found return it
						return thisNode

		# Assume the node was not found
		self.error_ = "getPeerNodeByValue: Unable to find the node with value " + self.getString(item_)		   
		return ""

#----------------------------
#---------------- subNode Search Methods (Search in thisNodes subNodes)-----------------
	# Same as getPeerNodeById, but only searches on subNodes of thisNode
	# Searches relative from first childNode  to last childNode
	# use rootNode if you are unsure about where the node is
	def getSubNodeById(self, nodeId_, caseSensitive=0):
		thisNode = self
		thisParrentNode = thisNode

		# Is thisNode leafNode?
		if thisNode.lastSubNodeIx_ < 0:
			#Y => Signal attempt to search subNodes on a leaf node
			thisNode.error_ = "getSubNodeById: leafNodes dont have subNodes"
			return ""

		# Search for the Node with the specified NodeId in this Nodes sub-Tree
		for node in thisParrentNode.subNodes_:		
			# is this caseSesnsitive search?
			if(caseSensitive == 0):					 
				# Is This the node we are looking for?
				if(node.nodeId_.lower() == nodeId_.lower()):
					# Node found retun it
					return node
			else: # Assume case sensitive search
				# Is This the node we are looking for?
				if(node.nodeId_ == nodeId_):
					# Node found retun it
					return node				   
					
		# Assume the node was not found
		self.error_ = "getSubNodeById: Unable to find the subNode with Id " + nodeId_		   
		return ""

	# Find subNode with specifed item (key:value), relative search in subNodes of thisNode
	# use rootNode if you are unsure about where the node is located
	# STATUS: TESTED->OK	
	def getSubNodeByItem(self, name_, value_, caseSensitive=0):
		thisNode = self
		thisParrentNode = thisNode
		
		# Is thisNode a leafNode? "Does thisNode have subNodes?"
		if thisNode.lastSubNodeIx_ == -1:
			#Y => Signal failed to get subNode
			self.error_ = "getSubNodeByItem: leafNodes does not have subNodes"
			return ""

		# Search for the Node with the specified key:value in this Nodes sub-Tree
		for node in thisParrentNode.subNodes_:
			# Is this the Item we are looking for?
			
			# reset trackingNode
			thisTrackingNode = trackingNode(name_, value_)

			# Get items
			thisItem = thisTrackingNode.value_
			someItem = node.item_

			# Is thisNode a simpleLeafNode?
			if node.isSimpleLeafNode():
				#Y =>
				# Get string representation of items
				thisItem = thisTrackingNode.getString()
				someItem = node.getString()

				# Is thisItem a simple leafNode?, hence does object type match
				if thisTrackingNode.isSimpleLeafNode():
					#Y => Does thisNode contain the item we are looking for?
					# is this caseSesnsitive search?
					if(caseSensitive == 0):					 
						#N => Is This the node we are looking for?
						if (node.name_.lower() == name_.lower()):
							if (thisItem.lower() == someItem.lower()):
								#Y => Node found retun it
								return node
					else: # Assume case sensitive search
						#Y => Is This the node we are looking for?
						if(node.name_ == name_):
							if(thisItem == someItem):
								#Y => Node found retun it
								return node

			# Is thisNode a OrderedDict Object?
			if node.isOrderedDict():
				#Y => Is thisItem a OrderedDict Object?, hence does object type match
				if thisTrackingNode.isOrderedDict():
					# Is ths casseSensitive search?
					if(caseSensitive == 0):
						#N => Does thisNode contain the item we are looking for?
						if(node.name_.lower() == name_.lower()):
							if(thisItem == someItem):
								#Y => Node found return it
								return node
					else:
						#Y => Assume case sensitive search
						# Does thisNode contain the item we are looking for?
						if(thisNode.name_ == name_):
							if(thisItem == someItem):
								#Y => Node found return it
								return node

			# Is thisNode a list Object?
			if node.isList():
				#Y => Is thisItem a list Object, hence does object type match?
				if thisTrackingNode.isList():
					# Is ths casseSensitive search?
					if(caseSensitive == 0):
						#N => Does thisNode contain the item we are looking for?
						if(node.name_.lower() == name_.lower()):
							if(thisItem == someItem):
								#Y => Node found return it
								return node
					else:
						#Y => Assume case sensitive search
						# Does thisNode contain the item we are looking for?
						if(node.name_ == name_):
							if(thisItem == someItem):
								#Y => Node found return it
								return node											
		
		# Assume the node was not found
		self.error_ = "getSubNodeByItem: Unable to find the node with Key:value " + self.getString(value_)
		return ""

	# Same as getPeerNodeById, but only searches on subNodes of thisNode
	# Searches relative from first childNode  to last childNode
	# use rootNode if you are unsure about where the node is
	def findSubNodeById(self, nodeId_, caseSensitive=0):
		thisNode = self
		thisParrentNode = thisNode

		# Is thisNode leafNode?
		if thisNode.lastSubNodeIx_ < 0:
			#Y => Signal attempt to search subNodes on a leaf node
			thisNode.error_ = "findSubNodeById: leafNodes dont have subNodes"
			return ""

		# Search for the Node with the specified NodeId in this Nodes sub-Tree
		for node in thisParrentNode.subNodes_:		
			# is this caseSesnsitive search?
			if(caseSensitive == 0):					 
				# Is This the node we are looking for?
				if(node.nodeId_.lower() == nodeId_.lower()):
					# Node found retun it
					return node
			else: # Assume case sensitive search
				# Is This the node we are looking for?
				if(node.nodeId_ == nodeId_):
					# Node found retun it
					return node				   
					
		# Assume the node was not found
		self.error_ = "findSubNodeById: Unable to find the subNode with Id " + nodeId_		   
		return ""				 

	# Find subNode with specifed item (key:value), relative search in subNodes of thisNode
	# use rootNode if you are unsure about where the node is located
	def findSubNodeByItem(self, name_, value_, caseSensitive=0):
		thisNode = self
		thisParrentNode = thisNode
		
		# Is thisNode a leafNode? "Does thisNode have subNodes?"
		if thisNode.lastSubNodeIx_ == -1:
			#Y => Signal failed to get subNode
			self.error_ = "findSubNodeByItem: leafNodes does not have subNodes"
			return ""

		# Has node search been restricted to a specific endNode?
		if startNode_ == "":
			#N => Assume thisNode sub-infoTree 
			startNode = thisNode

		# Search for the Node with the specified key:value in this Nodes sub-Tree
		for node in thisParrentNode.subNodes_:
			# Is this the Item we are looking for?
			
			# reset trackingNode
			thisTrackingNode = trackingNode(name_, value_)

			# Get items
			thisItem = thisTrackingNode.value_
			someItem = node.item_

			# Is thisNode a simpleLeafNode?
			if node.isSimpleLeafNode():
				#Y =>
				# Get string representation of items
				thisItem = thisTrackingNode.getString()
				someItem = node.getString()

				# Is thisItem a simple leafNode?, hence does object type match
				if thisTrackingNode.isSimpleLeafNode():
					#Y => Does thisNode contain the item we are looking for?
					# is this caseSesnsitive search?
					if(caseSensitive == 0):					 
						#N => Is This the node we are looking for?
						if (node.name_.lower() == name_.lower()):
							if (thisItem.lower() == someItem.lower()):
								#Y => Node found retun it
								return node
					else: # Assume case sensitive search
						#Y => Is This the node we are looking for?
						if(node.name_ == name_):
							if(thisItem == someItem):
								#Y => Node found retun it
								return node

			# Is thisNode a OrderedDict Object?
			if node.isOrderedDict():
				#Y => Is thisItem a OrderedDict Object?, hence does object type match
				if thisTrackingNode.isOrderedDict():
					# Is ths casseSensitive search?
					if(caseSensitive == 0):
						#N => Does thisNode contain the item we are looking for?
						if(node.name_.lower() == name_.lower()):
							if(thisItem == someItem):
								#Y => Node found return it
								return node
					else:
						#Y => Assume case sensitive search
						# Does thisNode contain the item we are looking for?
						if(thisNode.name_ == name_):
							if(thisItem == someItem):
								#Y => Node found return it
								return node

			# Is thisNode a list Object?
			if node.isList():
				#Y => Is thisItem a list Object, hence does object type match?
				if thisTrackingNode.isList():
					# Is ths casseSensitive search?
					if(caseSensitive == 0):
						#N => Does thisNode contain the item we are looking for?
						if(node.name_.lower() == name_.lower()):
							if(thisItem == someItem):
								#Y => Node found return it
								return node
					else:
						#Y => Assume case sensitive search
						# Does thisNode contain the item we are looking for?
						if(node.name_ == name_):
							if(thisItem == someItem):
								#Y => Node found return it
								return node											
		
		# Assume the node was not found
		self.error_ = "findSubNodeByItem: Unable to find the node with Key:value " + self.getString(value_)
		return ""

	# Same as getPeerNodeById, but only searches on subNodes of thisNode
	# Searches relative from first childNode  to last childNode
	# use rootNode if you are unsure about where the node is
	def getSubNodeByName(self, name_, caseSensitive=0):
		thisNode = self
		thisParrentNode = thisNode

		# Is thisNode leafNode?
		if thisNode.lastSubNodeIx_ < 0:
			#Y => Signal attempt to search subNodes on a leaf node
			thisNode.error_ = "getSubNodeByName: leafNodes dont have subNodes"
			return ""

		# Search for the Node with the specified NodeId in this Nodes sub-Tree
		for node in thisParrentNode.subNodes_:		
			# is this caseSesnsitive search?
			if(caseSensitive == 0):					 
				# Is This the node we are looking for?
				if(node.name_.lower() == name_.lower()):
					# Node found retun it
					return node
			else: # Assume case sensitive search
				# Is This the node we are looking for?
				if(node.name_ == name_):
					# Node found retun it
					return node				   
					
		# Assume the node was not found
		self.error_ = "getSubNodeByName: Unable to find the subNode with Id " + name_		   
		return ""

	# Same as getPeerNodeById, but only searches on subNodes of thisNode
	# Searches relative from first childNode  to last childNode
	# use rootNode if you are unsure about where the node is
	def findSubNodeByName(self, name_, caseSensitive=0):
		thisNode = self
		thisParrentNode = thisNode

		# Is thisNode leafNode?
		if thisNode.lastSubNodeIx_ < 0:
			#Y => Signal attempt to search subNodes on a leaf node
			thisNode.error_ = "findSubNodeByName: leafNodes dont have subNodes"
			return ""

		# Search for the Node with the specified NodeId in this Nodes sub-Tree
		for node in thisParrentNode.subNodes_:		
			# is this caseSesnsitive search?
			if(caseSensitive == 0):					 
				# Is This the node we are looking for?
				if(node.name_.lower() == name_.lower()):
					# Node found retun it
					return node
			else: # Assume case sensitive search
				# Is This the node we are looking for?
				if(node.name_ == name_):
					# Node found retun it
					return node				   
					
		# Assume the node was not found
		self.error_ = "findSubNodeByName: Unable to find the subNode with Id " + name_		   
		return ""				 

	# Same as getPeerNodeById, but only searches on subNodes of thisNode
	# Searches relative from first childNode  to last childNode
	# use rootNode if you are unsure about where the node is
	def getSubNodeByIx(self, nodeIx_):
		thisNode = self
		thisParrentNode = thisNode

		# Is thisNode leafNode?
		if thisNode.lastSubNodeIx_ < 0:
			#Y => Signal attempt to search subNodes on a leaf node
			thisNode.error_ = "getSubNodeByIx: leafNodes dont have subNodes"
			return ""

		# Is specified childNode ix valid?
		if nodeIx_ < 0 or nodeIx_ > thisParrentNode.lastSubNodeIx_:
			#N => Signal invalid childNode ix
			thisNode.error_ = "getSubNodeByIx: Specified ix " + str(nodeIx_) + " is not valid, last childNode Ix of parrentNode" + thisParrentNode.name_ + " is " + str(thisParrentNode.lastSubNodeIx_)
			return thisNode
		
		# Assume the ix was valid
		# Return specified subNode
		return thisParrentNode.subNodes_[nodeIx_]			

	# Finds first subNode with specified value
	# Searches relative in thisNodes subNodes
	# Can be used to detect wether a given value has allready be added to node tree when handling uniqe data.
	# TODO: Implement caseSenstive option (OK)
	def findSubNodeByValue(self, item_, caseSensitive=0):
		thisNode = self
		thisParrentNode = thisNode

		# Is this leafNode?
		if(thisNode.lastSubNodeIx_ == -1):
			# YES => leafNode dont have subNodes
			self.error_ = "findSubNodeByValue: leafNodes dont have subNodes!!"			  
			return ""

		# Find the subNode
		# Search for the specifed subNode->value
		for node in thisParrentNode.subNodes_:
			# reset trackingNode
			thisTrackingNode = trackingNode("", item_)

			# Get items
			thisItem = thisTrackingNode.value_
			someItem = node.item_

			# Is thisNode a simpleLeafNode?
			if node.isSimpleLeafNode():
				#Y =>
				# Get string representation of items
				thisItem = thisTrackingNode.getValueString()
				someItem = node.getValueString()

				# Is thisItem a simple leafNode?, hence does object type match
				if thisTrackingNode.isSimpleLeafNode():
					#Y => Does thisNode contain the item we are looking for?
					# is this caseSesnsitive search?
					if(caseSensitive == 0):					 
						#N => Is This the node we are looking for?
						if (thisItem.lower() == someItem.lower()):
							#Y => Node found retun it
							return thisNode
					else: # Assume case sensitive search
						#Y => Is This the node we are looking for?
						if(thisItem == someItem):
							#Y => Node found retun it
							return thisNode

			# Is thisNode a OrderedDict Object?
			if node.isOrderedDict():
				#Y => Is thisItem a OrderedDict Object?, hence does object type match
				if thisTrackingNode.isOrderedDict():
					#Y => Does thisNode contain the item we are looking for?
					if(thisItem == someItem):
						#Y => Node found return it
						return thisNode

			# Is thisNode a list Object?
			if node.isList():
				#Y => Is thisItem a list Object, hence does object type match?
				if thisTrackingNode.isList():
					#Y => Does thisNode contain the item we are looking for?
					if(thisItem == someItem):
						#Y => Node found return it
						return thisNode

		# Assume the node was not found
		self.error_ = "findSubNodeByValue: Unable to find the node with value " + self.getString(item_)		   
		return ""

	# Finds first peerNode with specified value
	# Searches relative in thisNodes peerNodes
	# Can be used to detect wether a given value has allready be added to node tree when handling uniqe data.
	# TODO: Implement caseSenstive option (OK)
	def getSubNodeByValue(self, item_, caseSensitive=0):
		thisNode = self
		thisParrentNode = thisNode.parrentNode_

		# Is this leafNode?
		if(thisNode.lastSubNodeIx_ == -1):
			# YES => leafNode dont have subNodes
			self.error_ = "getSubNodeByValue: leafNodes dont have subNodes!!"			  
			return ""

		# Find the subNode
		# Search for the specifed subNode->value
		for node in thisParrentNode.subNodes_:
			# reset trackingNode
			thisTrackingNode = trackingNode("", item_)

			# Get items
			thisItem = thisTrackingNode.value_
			someItem = node.item_

			# Is thisNode a simpleLeafNode?
			if node.isSimpleLeafNode():
				#Y =>
				# Get string representation of items
				thisItem = thisTrackingNode.getValueString()
				someItem = node.getValueString()

				# Is thisItem a simple leafNode?, hence does object type match
				if thisTrackingNode.isSimpleLeafNode():
					#Y => Does thisNode contain the item we are looking for?
					# is this caseSesnsitive search?
					if(caseSensitive == 0):					 
						#N => Is This the node we are looking for?
						if (thisItem.lower() == someItem.lower()):
							#Y => Node found retun it
							return thisNode
					else: # Assume case sensitive search
						#Y => Is This the node we are looking for?
						if(thisItem == someItem):
							#Y => Node found retun it
							return thisNode

			# Is thisNode a OrderedDict Object?
			if node.isOrderedDict():
				#Y => Is thisItem a OrderedDict Object?, hence does object type match
				if thisTrackingNode.isOrderedDict():
					#Y => Does thisNode contain the item we are looking for?
					if(thisItem == someItem):
						#Y => Node found return it
						return thisNode

			# Is thisNode a list Object?
			if node.isList():
				#Y => Is thisItem a list Object, hence does object type match?
				if thisTrackingNode.isList():
					#Y => Does thisNode contain the item we are looking for?
					if(thisItem == someItem):
						#Y => Node found return it
						return thisNode

		# Assume the node was not found
		self.error_ = "getSubNodeByValue: Unable to find the node with value " + self.getString(item_)		   
		return ""

#----------------------- node dataAnalysis methods ------------------	 
	# Finds frequency of node value
	# Searches relative from thisNode to end of its sub-infoTree
	# Use rootNode if you are unsure where the value is located
	# Can be used in data-analysis to count the frequency of a given value if you have decided not to use the unique feature in the infoTree
	# NOTE: The Method can only be called when items are string or number objects!!
	def getNodeByValueFreq(self, item_, caseSensitive=0, startNode_ = ""):
		thisNode = self
		startNode = startNode_
		
		# Has node search been restricted to a specific endNode?
		if startNode_ == "":
			#N => Assume thisNode sub-infoTree 
			startNode = thisNode.parrentNode_
		
		# Search for every Node with the specified NodeId in this Nodes sub-Tree
		valueFreq= 0
		while(thisNode != ""):
			
			# is this caseSesnsitive search?
			if(caseSensitive == 0):					 
				# Is This the node we are looking for?
				if(thisNode.item_.lower() == item_.lower()):
					# Node found update freq
					valueFreq += 1
			else: # Assume case sensitive search
				# Is This the node we are looking for?
				if(thisNode.item_ == item_):
					# Node found update value freq
					valueFreq += 1

			# Get Next Node
			thisNode = thisNode.getNextNode(startNode)
		
		# return the value frequency
		return valueFreq

	#----------- peerNode dataAnalysis methods------------
	# Returns infoTree containg all differences between the peerNodes in thisNodes parrentNodes sub-nodeChain
	# TODO. Implement it (OK)
	# TODO: Implement all uniqueness Levels
	# NOTE: The Method can only be called when items are string or number objects!!	   
	def getPeerNodeValueDifferences(self, caseSensitive=0, uniqueLevel_=-1):
		thisNode = self

		# Has uniquenessLevel been specified?
		if uniqueLevel_ < 0:
			#N => Use/Enerit thisNodes
			uniqueLevel_ = self.uniqueLevel_		

		# Create New infoTree for storing diffrences
		diffinfoTree = jsonNode("Value Differences")
		
		# Should be the difference be counted using build in frequency count?
		if uniqueLevel_ > 0:
			for subNode in thisNode.parrentNode_.subNodes_:
				# Is this value unique?
				if subNode.freq_ < 2:
					# Has a subNode been created for this Diffrence?
					diffNode = diffinfoTree.getSubNodeByName(subNode.nodeId_)
					if(diffNode == ""):
						diffNode = diffinfoTree.addSubNode(subNode.nodeId_, subNode.item_)
					else:
						diffNode.item_ = subNode.item_

					# Update Diffrence freq/count
					diffinfoTree.freq_ += 1					   

			# Return the infoTree containing all diffrences
			return diffinfoTree

		else:
			# Compare Diffrences "Find Unique fields"
			uniqueNode = 1
			for subNodeA in thisNode.parrentNode_.subNodes_:
				# Assume the node is unique
				uniqueNode = 1
				for subNodeB in thisNode.parrentNode_.subNodes_: # No need to dbl check prev values
					# Is this self?
					if subNodeA != subNodeB:
						# Is subNodeB diffrent from subNodeA?
						# Is compare case sensitive?
						if(caseSensitive):
							if subNodeA.item_.lower() == subNodeB.item_.lower():
								# Exit for since subNode is not unique
								uniqueNode = 0
								break
						else:
							if subNodeA.item_ == subNodeB.item_:
								# Exit for since subNode is not unique
								uniqueNode = 0
								break

				# Was the node Unique within sub-nodeChain?
				if uniqueNode == 1:
					# Has a subNode been created for this Diffrence?
					diffNode = diffinfoTree.getSubNodeByName(subNodeA.nodeId_)
					if(diffNode == ""):
						diffNode = diffinfoTree.addSubNode(subNodeA.nodeId_, subNodeA.item_)
					else:
						diffNode.item_ = subNodeA.item_ 

					# Update difference freq/count
					diffinfoTree.freq_ += 1

			# Return the infoTree containing the differences
			return diffinfoTree				  

		# Assume no diffrences to be found
		self.error_ = "getPeerNodeValueDifferences: No Differences found in " + thisNode.name_ + " peerNodes"		 
		return ""

	# Returns infoTree containg all differences between the two peerNodes sub-nodeChain
	# TODO. Implement it
	# NOTE: The Method can only be called when items are string or number objects!!	   
	def getPeerNodeValuesDifferences(self, caseSensitive=0, uniqueLevel_=-1):
		thisNode = self

		# Has uniquenessLevel been specified?
		if uniqueLevel_ < 0:
			#N => Use/Enerit thisNodes
			uniqueLevel_ = self.uniqueLevel_		

		# Create New infoTree for storing diffrences
		diffinfoTree = jsonNode("Value Differences")
		
		# Should be the difference be counted using build in frequency count?
		if uniqueLevel_ > 0:
			for subNode in thisNode.parrentNode_.subNodes_:
				# Is this value unique?
				if subNode.freq_ < 2:
					# Has a subNode been created for this Diffrence?
					diffNode = diffinfoTree.getSubNodeByName(subNode.nodeId_)
					if(diffNode == ""):
						diffNode = diffinfoTree.addSubNode(subNode.nodeId_, subNode.item_)
					else:
						diffNode.item_ = subNode.item_

					# Update Diffrence freq/count
					diffinfoTree.freq_ += 1					   

			# Return the infoTree containing all diffrences
			return diffinfoTree

		else:
			# Compare Diffrences "Find Unique fields"
			uniqueNode = 1
			for subNodeA in thisNode.parrentNode_.subNodes_:
				# Assume the node is unique
				uniqueNode = 1
				for subNodeB in thisNode.parrentNode_.subNodes_: # No need to dbl check prev values
					# Is this self?
					if subNodeA != subNodeB:
						# Is subNodeB diffrent from subNodeA?
						# Is compare case sensitive?
						if(caseSensitive):
							if subNodeA.item_.lower() == subNodeB.item_.lower():
								# Exit for since subNode is not unique
								uniqueNode = 0
								break
						else:
							if subNodeA.item_ == subNodeB.item_:
								# Exit for since subNode is not unique
								uniqueNode = 0
								break

				# Was the node Unique within sub-nodeChain?
				if uniqueNode == 1:
					# Has a subNode been created for this Diffrence?
					diffNode = diffinfoTree.getSubNodeByName(subNodeA.nodeId_)
					if(diffNode == ""):
						diffNode = diffinfoTree.addSubNode(subNodeA.nodeId_, subNodeA.item_)
					else:
						diffNode.item_ = subNodeA.item_ 

					# Update difference freq/count
					diffinfoTree.freq_ += 1

			# Return the infoTree containing the differences
			return diffinfoTree				  

		# Ass no diffrences to be found
		return ""		 
	
	# Returns infoTree containg all similarities between the subNodes in thisNodes nodeChain
	# TODO. Implement it (OK)
	# NOTE: The Method can only be called when items are string or number objects!!	   
	def getPeerNodeValueSimilarities(self, caseSensitive=0, uniqueLevel_=-1):
		thisNode = self

		# Has uniquenessLevel been specified?
		if uniqueLevel_ < 0:
			#N => Use/Enerit thisNodes
			uniqueLevel_ = self.uniqueLevel_		
		
		# Create New infoTree for storing diffrences
		simiinfoTree = jsonNode("Value Similarities")
		simiinfoTree.freq_ = 0 # Ensure freq starts at 0 since we are are not using freq for its normal purpose
		
		# Should be the difference be counted using build in frequency count?
		if uniqueLevel_ > 0:
			for subNode in thisNode.parrentNode_.subNodes_:
				# Is this value non-unique?, hence does this exists more then once in the sub-nodeChain
				if subNode.freq_ > 1:
					# Has a subNode been created for this Diffrence?
					simiNode = simiinfoTree.getSubNodeByName(subNode.nodeId_)
					if(simiNode == ""):
						simiNode = simiinfoTree.addSubNode(subNode.nodeId_, subNode.item_)
						simiNode.freq_ = subNode.freq_
					else:
						simiNode.item_ = subNode.item_
						simiNode.freq_ = subNode.freq_

					# Update Diffrence freq/count
					simiinfoTree.freq_ += 1					   

			# Return the infoTree containing all diffrences
			return simiinfoTree

		else:
			# Compare Similarities "Find Dublet fields"
			for subNodeA in thisNode.parrentNode_.subNodes_:
				# Assume the node is unique
				for subNodeB in thisNode.parrentNode_.subNodes_: # No need to dbl check prev values
					# Is this self?
					if subNodeA != subNodeB:
						# Is subNodeB diffrent from subNodeA?
						# Is compare case sensitive?
						if(caseSensitive):
							if subNodeA.item_.lower() == subNodeB.item_.lower():
								# Has this value allready been added to infoTree?
								simiNode = simiinfoTree.getNodeByName(subNodeB.nodeId_)

								if simiNode != "":
									# Just update the freq count for this node->value
									simiNode.freq_ += 1
								else:
									# Add the new vaue to the infoTree
									simiinfoTree.addSubNode(subNodeA.nodeIx_, subNodeA.item_)
																
						else:
							if subNodeA.item_ == subNodeB.item_:
								# Has this value allready been added to infoTree?
								simiNode = simiinfoTree.getNodeByName(subNodeB.nodeId_)

								if simiNode != "":
									# Just update the freq count for this node->value
									simiNode.freq_ += 1
								else:
									# Add the new vaue to the infoTree
									simiinfoTree.addSubNode(subNodeA.nodeIx_, subNodeA.item_)

									# Update number of similarities
									simiinfoTree.freq_ += 1
								
			# Return the infoTree containing the similarities
			return simiinfoTree

		# Assume no similarities found between thisNodes peerNodes
		self.error_ = "getPeerNodeValueSimilarities: No Similarities found in " + thisNode.name_ + " peerNodes"		   
		return ""

	# Returns infoTree containg all similarities between the subNodes in thisNodes nodeChain
	# TODO. Implement it
	# NOTE: The Method can only be called when items are string or number objects!!	   
	def getPeerNodesValueSimilarities(self, caseSensitive=0, uniqueLevel_=-1):
		thisNode = self

		# Has uniquenessLevel been specified?
		if uniqueLevel_ < 0:
			#N => Use/Enerit thisNodes
			uniqueLevel_ = self.uniqueLevel_		
		
		# Create New infoTree for storing diffrences
		simiinfoTree = jsonNode("Value Similarities")
		simiinfoTree.freq_ = 0 # Ensure freq starts at 0 since we are are not using freq for its normal purpose
		
		# Should be the difference be counted using build in frequency count?
		if uniqueLevel_ > 0:
			for subNode in thisNode.parrentNode_.subNodes_:
				# Is this value non-unique?, hence does this exists more then once in the sub-nodeChain
				if subNode.freq_ > 1:
					# Has a subNode been created for this Diffrence?
					simiNode = simiinfoTree.getSubNodeByName(subNode.nodeId_)
					if(simiNode == ""):
						simiNode = simiinfoTree.addSubNode(subNode.nodeId_, subNode.item_)
						simiNode.freq_ = subNode.freq_
					else:
						simiNode.item_ = subNode.item_
						simiNode.freq_ = subNode.freq_

					# Update Diffrence freq/count
					simiinfoTree.freq_ += 1					   

			# Return the infoTree containing all diffrences
			return simiinfoTree

		else:
			# Compare Similarities "Find Dublet fields"
			for subNodeA in thisNode.parrentNode_.subNodes_:
				# Assume the node is unique
				for subNodeB in thisNode.parrentNode_.subNodes_: # No need to dbl check prev values
					# Is this self?
					if subNodeA != subNodeB:
						# Is subNodeB diffrent from subNodeA?
						# Is compare case sensitive?
						if(caseSensitive):
							if subNodeA.item_.lower() == subNodeB.item_.lower():
								# Has this value allready been added to infoTree?
								simiNode = simiinfoTree.getNodeByName(subNodeB.nodeId_)

								if simiNode != "":
									# Just update the freq count for this node->value
									simiNode.freq_ += 1
								else:
									# Add the new vaue to the infoTree
									simiinfoTree.addSubNode(subNodeA.nodeIx_, subNodeA.item_)
																
						else:
							if subNodeA.item_ == subNodeB.item_:
								# Has this value allready been added to infoTree?
								simiNode = simiinfoTree.getNodeByName(subNodeB.nodeId_)

								if simiNode != "":
									# Just update the freq count for this node->value
									simiNode.freq_ += 1
								else:
									# Add the new vaue to the infoTree
									simiinfoTree.addSubNode(subNodeA.nodeIx_, subNodeA.item_)

									# Update number of similarities
									simiinfoTree.freq_ += 1
								
			# Return the infoTree containing the similarities
			return simiinfoTree

		# Assume no similarities found between thisNodes peerNodes
		self.error_ = "getPeerNodesValueSimilarities: No Similarities found in " + thisNode.name_ + " peerNodes"		
		return ""		 
	#------------------------------------------------	 
	#------------------------------------------------

	#---------------------------------------------
#--------------- subNode searching -------------

	#--------- subNode Data-analysis methods -----------	
	# Returns infoTree containg all differences between the subNodes in thisNodes nodeChain
	# Name is the name nodeId for the unique node and value is the value of the unique node
	# TODO. Implement it (OK)
	# NOTE: The Method can only be called when items are string or number objects!!	   
	def getSubNodeValueDifferences(self, caseSensitive=0, uniqueLevel_=-1):
		thisNode = self

		# Has uniquenessLevel been specified?
		if uniqueLevel_ < 0:
			#N => Use/Enerit thisNodes
			uniqueLevel_ = self.uniqueLevel_		

		# Create New infoTree for storing diffrences
		diffinfoTree = jsonNode("Value Differences")
		diffinfoTree.freq_ = 0 # Ensure freq starts at 0 since we are are not using freq for its normal purpose
		
		# Should be the difference be counted using build in frequency count?
		if uniqueLevel_ > 0:
			for subNode in thisNode.subNodes_:
				# Is this value unique?
				if subNode.freq_ < 2:
					# Has a subNode been created for this Diffrence?
					diffNode = diffinfoTree.getSubNodeByName(subNode.nodeId_)
					if(diffNode == ""):
						diffNode = diffinfoTree.addSubNode(subNode.nodeId_, subNode.item_)
					else:
						diffNode.item_ = subNode.item_

					# Update Diffrence freq/count
					diffinfoTree.freq_ += 1					   

			# Return the infoTree containing all diffrences
			return diffinfoTree

		else:
			# Compare Diffrences "Find Unique fields"
			uniqueNode = 1
			for subNodeA in thisNode.subNodes_:
				# Assume the node is unique
				uniqueNode = 1
				for subNodeB in thisNode.subNodes_: # No need to dbl check prev values
					# Is this self?
					if subNodeA != subNodeB:
						# Is subNodeB diffrent from subNodeA?
						# Is compare case sensitive?
						if(caseSensitive):
							if subNodeA.item_.lower() == subNodeB.item_.lower():
								# Exit for since subNode is not unique
								uniqueNode = 0
								break
						else:
							if subNodeA.item_ == subNodeB.item_:
								# Exit for since subNode is not unique
								uniqueNode = 0
								break

				# Was the node Unique within sub-nodeChain?
				if uniqueNode == 1:
					# Has a subNode been created for this Diffrence?
					diffNode = diffinfoTree.getSubNodeByName(subNodeA.nodeId_)
					if(diffNode == ""):
						diffNode = diffinfoTree.addSubNode(subNodeA.nodeId_, subNodeA.item_)
					else:
						diffNode.item_ = subNodeA.item_ 

					# Update difference freq/count
					diffinfoTree.freq_ += 1

			# Return the infoTree containing the differences
			return diffinfoTree				  

		# Assume no diffrences to be found
		self.error_ = "getSubNodeValueDifferences: No Differences found in " + thisNode.name_ + "s sub-nodeChain"		 
		return ""

	# Returns infoTree containg all differences between the subNodes in thisNodes nodeChain
	# Name is the name nodeId for the unique node and value is the value of the unique node
	# TODO. Implement it
	# NOTE: The Method can only be called when items are string or number objects!!	   
	def getSubNodesValueDifferences(self, caseSensitive=0, uniqueLevel_=-1):
		thisNode = self

		# Has uniquenessLevel been specified?
		if uniqueLevel_ < 0:
			#N => Use/Enerit thisNodes
			uniqueLevel_ = self.uniqueLevel_		

		# Create New infoTree for storing diffrences
		diffinfoTree = jsonNode("Value Differences")
		diffinfoTree.freq_ = 0 # Ensure freq starts at 0 since we are are not using freq for its normal purpose
		
		# Should be the difference be counted using build in frequency count?
		if uniqueLevel_ > 0:
			for subNode in thisNode.subNodes_:
				# Is this value unique?
				if subNode.freq_ < 2:
					# Has a subNode been created for this Diffrence?
					diffNode = diffinfoTree.getSubNodeByName(subNode.nodeId_)
					if(diffNode == ""):
						diffNode = diffinfoTree.addSubNode(subNode.nodeId_, subNode.item_)
					else:
						diffNode.item_ = subNode.item_

					# Update Diffrence freq/count
					diffinfoTree.freq_ += 1					   

			# Return the infoTree containing all diffrences
			return diffinfoTree

		else:
			# Compare Diffrences "Find Unique fields"
			uniqueNode = 1
			for subNodeA in thisNode.subNodes_:
				# Assume the node is unique
				uniqueNode = 1
				for subNodeB in thisNode.subNodes_: # No need to dbl check prev values
					# Is this self?
					if subNodeA != subNodeB:
						# Is subNodeB diffrent from subNodeA?
						# Is compare case sensitive?
						if(caseSensitive):
							if subNodeA.item_.lower() == subNodeB.item_.lower():
								# Exit for since subNode is not unique
								uniqueNode = 0
								break
						else:
							if subNodeA.item_ == subNodeB.item_:
								# Exit for since subNode is not unique
								uniqueNode = 0
								break

				# Was the node Unique within sub-nodeChain?
				if uniqueNode == 1:
					# Has a subNode been created for this Diffrence?
					diffNode = diffinfoTree.getSubNodeByName(subNodeA.nodeId_)
					if(diffNode == ""):
						diffNode = diffinfoTree.addSubNode(subNodeA.nodeId_, subNodeA.item_)
					else:
						diffNode.item_ = subNodeA.item_ 

					# Update difference freq/count
					diffinfoTree.freq_ += 1

			# Return the infoTree containing the differences
			return diffinfoTree				  

		# Assume no diffrences to be found
		self.error_ = "getSubNodesValueDifferences: No Differences found in between " + thisNode.name_ + " sub-nodeChain & xx nodes sub-nodeChain"		  
		return ""		 

	# Returns infoTree containg all similarities & differences between the subNodes in thisNodes nodeChain
	# Name is the name nodeId for the unique node and value is the value of the unique node
	# TODO. Implement it
	# NOTE: The Method can only be called when items are string or number objects!!
	def getSubNodeValueFreqAnalysis(self, caseSensitive=0, uniqueLevel_=-1):
		thisNode = self

		# Create New infoTree for storing diffrences
		compinfoTree = jsonNode("Value Analysis")

		# Calc Diffrences
		compinfoTree.addSubNodeObj(thisNode.getSubNodeValueDifferences(caseSensitive, uniqueLevel_))
		compinfoTree.addSubNodeObj(thisNode.getSubNodeValueSimilarities(caseSensitive, uniqueLevel_))

		# return infoTree Containg all similarites and diffrences
		return compinfoTree

	# Returns infoTree containg all similarities & differences between the subNodes in thisNodes nodeChain
	# Name is the name nodeId for the unique node and value is the value of the unique node
	# TODO. Implement it
	def getSubNodesValueFreqAnalysis(self, caseSensitive=0, uniqueLevel_=-1):
		thisNode = self

		# Create New infoTree for storing diffrences
		compinfoTree = jsonNode("Value Analysis")

		# Calc Diffrences
		compinfoTree.addSubNodeObj(thisNode.getSubNodeValueDifferences(caseSensitive, uniqueLevel_))
		compinfoTree.addSubNodeObj(thisNode.getSubNodeValueSimilarities(caseSensitive, uniqueLevel_))

		# return infoTree Containg all similarites and diffrences
		return compinfoTree		   

	# Returns infoTree containg all similarities between the subNodes in thisNodes nodeChain
	# TODO. Implement it
	def getSubNodeValueSimilarities(self, caseSensitive=0, uniqueLevel_=-1):
		thisNode = self

		# Has uniquenessLevel been specified?
		if uniqueLevel_ < 0:
			#N => Use/Enerit thisNodes
			uniqueLevel_ = self.uniqueLevel_		

		# Create New infoTree for storing diffrences
		simiinfoTree = jsonNode("Value Similarities")
		simiinfoTree.freq_ = 0 # Ensure freq starts at 0 since we are are not using freq for its normal purpose
		
		# Should be the difference be counted using build in frequency count?
		if uniqueLevel_ > 0:
			for subNode in thisNode.subNodes_:
				# Is this value non-unique?, hence does this exists more then once in the sub-nodeChain
				if subNode.freq_ > 1:
					# Has a subNode been created for this Diffrence?
					simiNode = simiinfoTree.getSubNodeByName(subNode.nodeId_)
					if(simiNode == ""):
						simiNode = simiinfoTree.addSubNode(subNode.nodeId_, subNode.item_)
						simiNode.freq_ = subNode.freq_
					else:
						simiNode.item_ = subNode.item_
						simiNode.freq_ = subNode.freq_

					# Update Diffrence freq/count
					simiinfoTree.freq_ += 1					   

			# Return the infoTree containing all diffrences
			return simiinfoTree

		else:
			# Compare Similarities "Find Dublet fields"
			for subNodeA in thisNode.subNodes_:
				# Assume the node is unique
				for subNodeB in thisNode.subNodes_: # No need to dbl check prev values
					# Is this self?
					if subNodeA != subNodeB:
						# Is subNodeB diffrent from subNodeA?
						# Is compare case sensitive?
						if(caseSensitive):
							if subNodeA.item_.lower() == subNodeB.item_.lower():
								# Has this value allready been added to infoTree?
								simiNode = simiinfoTree.getNodeByName(subNodeB.nodeId_)

								if simiNode != "":
									# Just update the freq count for this node->value
									simiNode.freq_ += 1
								else:
									# Add the new vaue to the infoTree
									simiinfoTree.addSubNode(subNodeA.nodeIx_, subNodeA.item_)
																
						else:
							if subNodeA.item_ == subNodeB.item_:
								# Has this value allready been added to infoTree?
								simiNode = simiinfoTree.getNodeByName(subNodeB.nodeId_)

								if simiNode != "":
									# Just update the freq count for this node->value
									simiNode.freq_ += 1
								else:
									# Add the new vaue to the infoTree
									simiinfoTree.addSubNode(subNodeA.nodeIx_, subNodeA.item_)

									# Update number of similarities
									simiinfoTree.freq_ += 1
								
			# Return the infoTree containing the similarities
			return simiinfoTree

		# Assume No Similarities found
		self.error_ = "getSubNodeValueSimilarities: No Similarities found in between " + thisNode.name_ + " sub-nodeChain"
		return ""

	# Returns infoTree containg all similarities between the subNodes in thisNodes nodeChain
	# TODO. Implement it
	# NOTE: The Method can only be called when items are string or number objects!!	   
	def getSubNodesValueSimilarities(self, caseSensitive=0, uniqueLevel_=-1):
		thisNode = self

		# Has uniquenessLevel been specified?
		if uniqueLevel_ < 0:
			#N => Use/Enerit thisNodes
			uniqueLevel_ = self.uniqueLevel_		

		# Create New infoTree for storing diffrences
		simiinfoTree = jsonNode("Value Similarities")
		simiinfoTree.freq_ = 0 # Ensure freq starts at 0 since we are are not using freq for its normal purpose
		
		# Should be the difference be counted using build in frequency count?
		if uniqueLevel_ > 0:
			for subNode in thisNode.subNodes_:
				# Is this value non-unique?, hence does this exists more then once in the sub-nodeChain
				if subNode.freq_ > 1:
					# Has a subNode been created for this Diffrence?
					simiNode = simiinfoTree.getSubNodeByName(subNode.nodeId_)
					if(simiNode == ""):
						simiNode = simiinfoTree.addSubNode(subNode.nodeId_, subNode.item_)
						simiNode.freq_ = subNode.freq_
					else:
						simiNode.item_ = subNode.item_
						simiNode.freq_ = subNode.freq_

					# Update Diffrence freq/count
					simiinfoTree.freq_ += 1					   

			# Return the infoTree containing all diffrences
			return simiinfoTree

		else:
			# Compare Similarities "Find Dublet fields"
			for subNodeA in thisNode.subNodes_:
				# Assume the node is unique
				for subNodeB in thisNode.subNodes_: # No need to dbl check prev values
					# Is this self?
					if subNodeA != subNodeB:
						# Is subNodeB diffrent from subNodeA?
						# Is compare case sensitive?
						if(caseSensitive):
							if subNodeA.item_.lower() == subNodeB.item_.lower():
								# Has this value allready been added to infoTree?
								simiNode = simiinfoTree.getNodeByName(subNodeB.nodeId_)

								if simiNode != "":
									# Just update the freq count for this node->value
									simiNode.freq_ += 1
								else:
									# Add the new vaue to the infoTree
									simiinfoTree.addSubNode(subNodeA.nodeIx_, subNodeA.item_)
																
						else:
							if subNodeA.item_ == subNodeB.item_:
								# Has this value allready been added to infoTree?
								simiNode = simiinfoTree.getNodeByName(subNodeB.nodeId_)

								if simiNode != "":
									# Just update the freq count for this node->value
									simiNode.freq_ += 1
								else:
									# Add the new vaue to the infoTree
									simiinfoTree.addSubNode(subNodeA.nodeIx_, subNodeA.item_)

									# Update number of similarities
									simiinfoTree.freq_ += 1
								
			# Return the infoTree containing the similarities
			return simiinfoTree

		# Assume no Similarities has been found
		self.error_ = "getSubNodesValueSimilarities: No Similarities found between " + thisNode.name_ + " sub-nodeChain and xx nodes sub-nodeChain"
		return ""			 
	#------------------------------------------------	  
	
# ------------ infoTree Traversal/Navigation helper functions --------------
	# Returns first peerNode of thisNode
	def getFirstPeerNode(self):
		thisNode = self
		
		# Is this rootNode?
		if(thisNode.parrentNode_ == ""):
			# YES => rootNode has no peerNodes
			self.error_ = "getFirstPeerNode: rootNodes dont have peerNodes!!"			 
			return ""

		# Get parrentNode
		thisNode = thisNode.parrentNode_
		# Does this node have subNodes?
		if(thisNode.lastSubNodeIx_ == -1):
			# NO => This node dont have subNodes
			self.error_ = "getFirstPeerNode: No peerNode found!!"			 
			return ""

		thisNode = thisNode.subNodes_[0]

		return thisNode

	# Returns last peerNode of thisNode
	def getLastPeerNode(self):
		thisNode = self
		
		# Is this rootNode?
		if(thisNode.parrentNode_ == ""):
			# YES => rootNode has no peerNodes
			self.error_ = "getLastPeerNode: rootNodes dont have peerNodes!!"			
			return ""

		# Get parrentNode
		thisNode = thisNode.parrentNode_
		# Does this node have subNodes?
		if(thisNode.lastSubNodeIx_ == -1):
			# NO => This node dont have subNodes
			self.error_ = "getLastPeerNode: No peerNode found!!"			
			return ""
			
		thisNode = thisNode.subNodes_[thisNode.lastSubNodeIx_] # Remember binary math!!

		return thisNode

	# Returns first subNode of thisNode
	def getFirstSubNode(self):
		thisNode = self
		
		# Is this leafNode?
		if(thisNode.lastSubNodeIx_ == -1):
			# YES => leafNode has no subNodes
			self.error_ = "getFirstSubNode: leafNodes dont have subNodes!!"			   
			return ""

		thisNode = thisNode.subNodes_[0]

		return thisNode

	# Returns last subNode of thisNode
	def getLastSubNode(self):
		thisNode = self
		
		# Is this leafNode?
		if(thisNode.lastSubNodeIx_ == -1):
			# YES => leafNode has no subNodes
			self.error_ = "getLastSubNode: leafNodes dont have subNodes!!"			  
			return ""
			
		thisNode = thisNode.subNodes_[thisNode.lastSubNodeIx_] # Remember binary math!!

		return thisNode

	# Returns next parrentNode relative to thisNode
	def getNextParrentNode(self):
		thisNode = self

		# Is this rootNode?
		if(thisNode.parrentNode_ == ""):
			# YES => rootNode has no parrentNode
			self.error_ = "getNextParrentNode: rootNodes dont have parrentNodes!!"			  
			return ""

		# move upto Parrent
		thisNode = thisNode.parrentNode_
		# Get next peerNode
		thisNode = thisNode.getNextPeerNode()

		return thisNode
	
	# Returns prev parrentNode relative to thisNode		
	def getPrevParrentNode(self):
		thisNode = self

		# Is this rootNode?
		if(thisNode.parrentNode_ == ""):
			# YES => rootNode has no parrentNode
			self.error_ = "getPrevParrentNode: rootNodes dont have parrentNodes!!"			  
			return ""

		# move upto Parrent
		thisNode = thisNode.parrentNode_
		# Get prev peerNode
		thisNode = thisNode.getPrevPeerNode()

		return thisNode		   

#---------------------------------------------------------------------

#-----------------------------------------------------		 
# TODO: Implement it the same way at add, inseret, replace, hence core methods that helper/wrapper methdos can call to rapidly (OK)
# Implement additional helper methods
#-------------- REMOVE node handling (Search from thisNode to end of sub-infoTree)------------
	# Remove thisNode
	def removeNodeObj(self):
		thisNode = self
		thisParrentNode = thisNode.parrentNode_

		#Is this rootNode?
		if(thisNode.parrentNode_ == ""):
			# YES => You cannot remove rootNode
			self.error_ = "removeNodeObj: rootNodes cannot be removed!!"			
			return self
		
		# Remove the node
		thisParrentNode.subNodes_.remove(thisNode)

		# Update subNode Count
		thisParrentNode.lastSubNodeIx_ -= 1

		# Fix ParrentNode and its entire sub-infoTree
		thisParrentNode.updateSubinfoTreeNodeIds()

		# Update json object structure of parrentNode
		# Is parrentNode a orderedDict object?
		if thisParrentNode.isOrderedDict():
			#Y => Delete the Item
			thisParrentNode.item_.pop(thisNode.name_)
		else:
			#N => Assume parrentNode is a list Object
			thisParrentNode.item_.remove(thisNode.item_)

		return thisParrentNode

	# Remove node specified by Id, Search from thisNode to end of its sub-infoTree
	def removeNodeObjById(self, nodeId_, startNode_ = ""):
		thisNode = self
		thisParrentNode = thisNode.parrentNode_
		startNode = startNode_
		
		# Has node search been restricted to a specific endNode?
		if startNode == "":
			#N => Assume thisNode sub-infoTree 
			startNode = thisNode.parrentNode_		

		#Is this rootNode?
		if(thisNode.parrentNode_ == ""):
			# YES => You cannot remove rootNode
			self.error_ = "removeNodeObjById: rootNodes cannot be removed!!"			
			return self
		
		# Find the node
		thisParrentNode = ""
		while(thisNode != ""):
			# Is this the node we are looking for?
			if(thisNode.nodeId_.lower() == nodeId_.lower()):
				# Node found
				thisParrentNode = thisNode.parrentNode_
				# Forced exit node has been found
				break

			# Try nextNode
			thisNode = thisNode.getNextNode(startNode)

		# Was the node found?
		if(thisParrentNode == ""):
			# NO
			self.error_ = "removeNodeObjById: Unable to find node with Id " + nodeId_			 
			return self 

		# Remove the node
		thisParrentNode.subNodes_.remove(thisNode)

		# Update subNode Count
		thisParrentNode.lastSubNodeIx_ -= 1

		# Fix ParrentNode and its entire sub-infoTree
		thisParrentNode.updateSubinfoTreeNodeIds()

		# Update json object structure of parrentNode
		# Is parrentNode a orderedDict object?
		if thisParrentNode.isOrderedDict():
			#Y => Delete the Item
			thisParrentNode.item_.pop(thisNode.name_)
		else:
			#N => Assume parrentNode is a list Object
			thisParrentNode.item_.remove(thisNode.item_)		

		return thisParrentNode

	# Remove node specified by name, Search from thisNode to end of its sub-infoTree
	def removeNodeObjByName(self, name_, startNode_ = ""):
		thisNode = self
		thisParrentNode = thisNode.parrentNode_
		startNode = startNode_
		
		# Has node search been restricted to a specific endNode?
		if startNode == "":
			#N => Assume thisNode sub-infoTree 
			startNode = thisNode.parrentNode_		

		#Is this rootNode?
		if(thisNode.parrentNode_ == ""):
			# YES => You cannot remove rootNode
			self.error_ = "removeNodeObjByName: rootNodes cannot be removed!!"			  
			return self
		
		# Find the node
		thisParrentNode = ""
		while(thisNode != ""):
			# Is this the node we are looking for?
			if(thisNode.name_.lower() == name_.lower()):
				# Node found
				thisParrentNode = thisNode.parrentNode_
				# Forced exit node has been found
				break

			# Try nextNode
			thisNode = thisNode.getNextNode(startNode)

		# Was the node found?
		if(thisParrentNode == ""):
			# YES
			self.error_ = "removeNodeObjByName: Unable to find node with name " + name_			   
			return self 

		# Remove the node
		thisParrentNode.subNodes_.remove(thisNode)

		# Update subNode Count
		thisParrentNode.lastSubNodeIx_ -= 1

		# Fix ParrentNode and its entire sub-infoTree
		thisParrentNode.updateSubinfoTreeNodeIds()

		# Update json object structure of parrentNode
		# Is parrentNode a orderedDict object?
		if thisParrentNode.isOrderedDict():
			#Y => Delete the Item
			thisParrentNode.item_.pop(thisNode.name_)
		else:
			#N => Assume parrentNode is a list Object
			thisParrentNode.item_.remove(thisNode.item_)		

		return thisParrentNode		  

	# Remove node specified by value, Search from thisNode to end of its sub-infoTree
	def removeNodeObjByValue(self, value_, startNode_ = ""):
		thisNode = self
		thisParrentNode = thisNode.parrentNode_
		startNode = startNode_
		
		# Has node search been restricted to a specific endNode?
		if startNode == "":
			#N => Assume thisNode sub-infoTree 
			startNode = thisNode.parrentNode_		

		#Is this rootNode?
		if(thisNode.parrentNode_ == ""):
			# YES => You cannot remove rootNode
			self.error_ = "removeNodeObjByName: rootNodes cannot be removed!!"			  
			return self
		
		# Find the reference node
		thisParrentNode=""
		while(thisNode != ""):
			# Is this the node we are looking for?
			# Is thisNode and value a ordered dict object
			if thisNode.isOrderedDict() and thisNode.isOrderedDict(value_):
				#Y => Is this the value we are looking for
				if thisNode.item_ == value_:
					#Y
					thisParrentNode = thisNode.parrentNode_
					break

			# Is thisNode and value a list object
			if thisNode.isList() and thisNode.isList(value_):
				#Y => Is this the value we are looking for
				if thisNode.item_ == value_:
					#Y
					thisParrentNode = thisNode.parrentNode_
					break					

			# Is thisNode and value a string
			if thisNode.isString() and thisNode.isString(value_):
				#Y => Is this the value we are looking for
				if(thisNode.item_.lower() == value_.lower()):
					#Y
					thisParrentNode = thisNode.parrentNode_
					break

			# Is thisNode and value a number
			if thisNode.isNumber() and thisNode.isNumber(value_):
				#Y => Is this the value we are looking for
				if thisNode.item_ == value_:
					#Y
					thisParrentNode = thisNode.parrentNode_
					break

			# Get next node
			thisNode = thisNode.getNextNode(startNode)

		# Was the node found?
		if(thisParrentNode == ""):
			# YES
			self.error_ = "removeNodeObjByName: Unable to find node with value " + self.getString(value_)			   
			return self 

		# Remove the node
		thisParrentNode.subNodes_.remove(thisNode)

		# Update subNode Count
		thisParrentNode.lastSubNodeIx_ -= 1

		# Fix ParrentNode and its entire sub-infoTree
		thisParrentNode.updateSubinfoTreeNodeIds()

		# Update json object structure of parrentNode
		# Is parrentNode a orderedDict object?
		if thisParrentNode.isOrderedDict():
			#Y => Delete the Item
			thisParrentNode.item_.pop(thisNode.name_)
		else:
			#N => Assume parrentNode is a list Object
			thisParrentNode.item_.remove(thisNode.item_)		

		return thisParrentNode		  

#----------- Remove peerNode Handling (Search in thisNodes peerNodes) -------------	   
	# Remove peerNode relative to node specified Id, Search from thisNode to end of its sub-nodeChain
	def removePeerNodeObjById(self, nodeId_):
		thisNode = self
		thisParrentNode = thisNode.parrentNode_

		#Is this rootNode?
		if(thisNode.parrentNode_ == ""):
			# YES => You cannot remove rootNode
			self.error_ = "removePeerNodeObjById: rootNodes cannot be removed!!"
			return self
		
		# Find the peerNode
		thisParrentNode =""
		for node in thisNode.parrentNode_.subNodes_:
			# Is this the node we are looking for?
			if(node.nodeId_.lower() == nodeId_):
				# YES
				thisParrentNode = node.parrentNode_
				thisNode = node
				break

		# Was the node found?
		if(thisParrentNode == ""):
			# NO
			self.error_ = "removePeerNodeObjById: Unable to find peerNode with Id " + nodeId_			  
			return self

		# Remove the node
		thisParrentNode.subNodes_.remove(thisNode)

		# Update subNode Count
		thisParrentNode.lastSubNodeIx_ -= 1

		# Fix ParrentNode and its entire sub-infoTree
		thisParrentNode.updateSubinfoTreeNodeIds()

		# Update json object structure of parrentNode
		# Is parrentNode a orderedDict object?
		if thisParrentNode.isOrderedDict():
			#Y => Delete the Item
			thisParrentNode.item_.pop(thisNode.name_)
		else:
			#N => Assume parrentNode is a list Object
			thisParrentNode.item_.remove(thisNode.item_)		

		return thisParrentNode

	# Remove peerNode relative to node specified name, Search from thisNode to end of its sub-nodeChain
	def removePeerNodeObjByName(self, name_):
		thisNode = self
		thisParrentNode = thisNode.parrentNode_

		#Is this rootNode?
		if(thisNode.parrentNode_ == ""):
			# YES => You cannot remove rootNode
			self.error_ = "removePeerNodeObjByName: rootNodes cannot be removed!!"			  
			return self
		
		# Find the peerNode
		thisParrentNode =""
		for node in thisNode.parrentNode_.subNodes_:
			# Is this the node we are looking for?
			if(node.name_.lower() == name_):
				# YES
				thisParrentNode = node.parrentNode_
				thisNode = node
				break

		# Was the node found?
		if(thisParrentNode == ""):
			# NO
			self.error_ = "removePeerNodeObjByName: Unable to find peerNode with name " + name_			   
			return self

		# Remove the node
		thisParrentNode.subNodes_.remove(thisNode)

		# Update subNode Count
		thisParrentNode.lastSubNodeIx_ -= 1

		# Fix ParrentNode and its entire sub-infoTree
		thisParrentNode.updateSubinfoTreeNodeIds()

		# Update json object structure of parrentNode
		# Is parrentNode a orderedDict object?
		if thisParrentNode.isOrderedDict():
			#Y => Delete the Item
			thisParrentNode.item_.pop(thisNode.name_)
		else:
			#N => Assume parrentNode is a list Object
			thisParrentNode.item_.remove(thisNode.item_)		

		return thisParrentNode

	# Remove peerNode relative to node specified value, Search from thisNode to end of its sub-nodeChain
	def removePeerNodeObjByValue(self, value_):
		thisNode = self
		thisParrentNode = thisNode.parrentNode_

		#Is this rootNode?
		if(thisNode.parrentNode_ == ""):
			# YES => You cannot remove rootNode
			self.error_ = "removePeerNodeObjByValue: rootNodes cannot be removed!!"			  
			return self
		
		# Find the peerNode
		thisParrentNode =""
		for node in thisNode.parrentNode_.subNodes_:
			# Is this the node we are looking for?
			# Is thisNode and value a ordered dict object
			if node.isOrderedDict() and node.isOrderedDict(value_):
				#Y => Is this the value we are looking for
				if node.item_ == value_:
					#Y
					thisParrentNode = node.parrentNode_
					thisNode = node
					break

			# Is thisNode and value a list object
			if node.isList() and node.isList(value_):
				#Y => Is this the value we are looking for
				if node.item_ == value_:
					#Y
					thisParrentNode = node.parrentNode_
					thisNode = node
					break					

			# Is thisNode and value a string
			if node.isString() and node.isString(value_):
				#Y => Is this the value we are looking for
				if(node.item_.lower() == value_.lower()):
					#Y
					thisParrentNode = node.parrentNode_
					thisNode = node
					break

			# Is thisNode and value a number
			if node.isNumber() and node.isNumber(value_):
				#Y => Is this the value we are looking for
				if node.item_ == value_:
					#Y
					thisParrentNode = node.parrentNode_
					thisNode = node
					break

		# Was the node found?
		if(thisParrentNode == ""):
			# NO
			self.error_ = "removePeerNodeObjByValue: Unable to find peerNode with value " + self.getString(value_)			   
			return self

		# Remove the node
		thisParrentNode.subNodes_.remove(thisNode)

		# Update subNode Count
		thisParrentNode.lastSubNodeIx_ -= 1

		# Fix ParrentNode and its entire sub-infoTree
		thisParrentNode.updateSubinfoTreeNodeIds()

		# Update json object structure of parrentNode
		# Is parrentNode a orderedDict object?
		if thisParrentNode.isOrderedDict():
			#Y => Delete the Item
			thisParrentNode.item_.pop(thisNode.name_)
		else:
			#N => Assume parrentNode is a list Object
			thisParrentNode.item_.remove(thisNode.item_)		

		return thisParrentNode

	# Remove peerNode on same parrentNode/nodeChain as thisNode & relative nodeIx
	def removePeerNodeObjByIx(self, nodeIx_=0):
		thisNode = self
		thisParrentNode = thisNode.parrentNode_

		#Is this rootNode?
		if(thisNode.parrentNode_ == ""):
			# YES => You cannot remove rootNode
			self.error_ = "removePeerNodeObjByIx: rootNodes cannont be removed!!"			 
			return self
		
		# Is nodeIx valid?
		if(nodeIx_ < 0)|(nodeIx_ > thisParrentNode.subNodeCount - 1):
			# NO
			self.error_ = "removePeerNodeObjByIx: Unable to find peerNode with Ix " + str(nodeIx_)			  
			return self

		# Get peerNode
		thisNode = thisParrentNode.subNodes_[nodeIx_]

		# Remove the node
		thisParrentNode.subNodes_.remove(thisNode)

		# Update subNode Count
		thisParrentNode.lastSubNodeIx_ -= 1

		# Fix ParrentNode and its entire sub-infoTree
		thisParrentNode.updateSubinfoTreeNodeIds()

		# Update json object structure of parrentNode
		# Is parrentNode a orderedDict object?
		if thisParrentNode.isOrderedDict():
			#Y => Delete the Item
			thisParrentNode.item_.pop(thisNode.name_)
		else:
			#N => Assume parrentNode is a list Object
			thisParrentNode.item_.remove(thisNode.item_)		

		return thisParrentNode			  

#------------------ Remove suNode handling (Search in thisNodes subNodes) -----------------
	# Remove thisNodes subNode specified by ix, Search in thisNodes subNodes
	def removeSubNodeObj(self, nodeIx_=0):
		thisNode = self
		thisParrentNode = thisNode

		#Is this rootNode?
		if(thisParrentNode == ""):
			# YES => You cannot remove rootNode
			self.error_ = "removeSubNodeObj: rootNodes cannot be removed!!"			   
			return self
		
		# Is nodeIx valid?
		if(nodeIx_ < 0)|(nodeIx_ > thisParrentNode.lastSubNodeIx_):
			# NO
			self.error_ = "removeSubNodeObj: Unable to find subNode with Ix " + str(nodeIx_)			
			return self

		# Get subNode
		thisNode = thisParrentNode.subNodes_[nodeIx_]

		# Remove the node
		thisParrentNode.subNodes_.remove(thisNode)

		# Update subNode Count
		thisParrentNode.lastSubNodeIx_ -= 1

		# Fix ParrentNode and its entire sub-infoTree
		thisParrentNode.updateSubinfoTreeNodeIds()

		# Update json object structure of parrentNode
		# Is parrentNode a orderedDict object?
		if thisParrentNode.isOrderedDict():
			#Y => Delete the Item
			thisParrentNode.item_.pop(thisNode.name_)
		else:
			#N => Assume parrentNode is a list Object
			thisParrentNode.item_.remove(thisNode.item_)		

		return thisParrentNode

	# Remove thisNodes subNode specified by Id, Search in thisNodes subNodes
	def removeSubNodeObjById(self, nodeId_):
		thisNode = self
		thisParrentNode = thisNode
				
		# Find the node
		thisParrentNode =""
		for node in thisNode.parrentNode_.subNodes_:
			# Is this the node we are looking for?
			if(node.nodeId_.lower() == nodeId_.lower()):
				# YES
				thisParrentNode = node.parrentNode_
				thisNode = node
				break
		
		# Has the node been found?
		if(thisParrentNode == ""):
			# NO
			self.error_ = "removeSubNodeObjById: Unable to find node with Id " + nodeId_			
			return self
		
		# Remove the SubNode
		thisParrentNode.subNodes_.remove(thisNode)

		# Update subNode Count
		thisParrentNode.lastSubNodeIx_ -= 1

		# Fix ParrentNode and its entire sub-infoTree
		thisParrentNode.updateSubinfoTreeNodeIds()

		# Update json object structure of parrentNode
		# Is parrentNode a orderedDict object?
		if thisParrentNode.isOrderedDict():
			#Y => Delete the Item
			thisParrentNode.item_.pop(thisNode.name_)
		else:
			#N => Assume parrentNode is a list Object
			thisParrentNode.item_.remove(thisNode.item_)		

		return thisParrentNode		  

	# Remove thisNodes subNode specified by name, Search in thisNodes subNodes
	def removeSubNodeObjByName(self, name_):
		thisNode = self
		thisParrentNode = thisNode		
		
		# Find the node
		thisParrentNode =""
		for node in thisNode.parrentNode_.subNodes_:
			# Is this the node we are looking for?
			if(node.name_.lower() == name_.lower()):
				# YES
				thisParrentNode = node.parrentNode_
				thisNode = node
		
		# Has the node been found?
		if(thisParrentNode == ""):
			# NO
			self.error_ = "removeSubNodeObjByName: Unable to find node with name " + name_			  
			return self
		
		# Remove the SubNode
		thisParrentNode.subNodes_.remove(thisNode)

		# Update subNode Count
		thisParrentNode.lastSubNodeIx_ -= 1

		# Fix ParrentNode and its entire sub-infoTree
		thisParrentNode.updateSubinfoTreeNodeIds()

		# Update json object structure of parrentNode
		# Is parrentNode a orderedDict object?
		if thisParrentNode.isOrderedDict():
			#Y => Delete the Item
			thisParrentNode.item_.pop(thisNode.name_)
		else:
			#N => Assume parrentNode is a list Object
			thisParrentNode.item_.remove(thisNode.item_)		

		return thisParrentNode

	# Remove thisNodes subNode specified by value, Search in thisNodes subNodes
	def removeSubNodeObjByValue(self, value_):
		thisNode = self
		thisParrentNode = thisNode
				
		# Find the reference node
		thisParrentNode=""
		for node in thisNode.parrentNode_.subNodes_:
			# Is this the node we are looking for?
			# Is thisNode and value a ordered dict object
			if node.isOrderedDict() and node.isOrderedDict(value_):
				#Y => Is this the value we are looking for
				if node.item_ == value_:
					#Y
					thisParrentNode = node.parrentNode_
					thisNode = node
					break

			# Is thisNode and value a list object
			if node.isList() and node.isList(value_):
				#Y => Is this the value we are looking for
				if node.item_ == value_:
					#Y
					thisParrentNode = node.parrentNode_
					thisNode = node
					break					

			# Is thisNode and value a string
			if node.isString() and node.isString(value_):
				#Y => Is this the value we are looking for
				if(node.item_.lower() == value_.lower()):
					#Y
					thisParrentNode = node.parrentNode_
					thisNode = node
					break

			# Is thisNode and value a number
			if node.isNumber() and node.isNumber(value_):
				#Y => Is this the value we are looking for
				if node.item_ == value_:
					#Y
					thisParrentNode = node.parrentNode_
					thisNode = node
					break
		
		# Has the node been found?
		if(thisParrentNode == ""):
			# NO
			self.error_ = "removeSubNodeObjByValue: Unable to find node with value " + self.getString(value_)			  
			return self
		
		# Assume nodeIx is valid
		thisNode = thisParrentNode.subNodes_[nodeIx_]

		# Remove the SubNode
		thisParrentNode.subNodes_.remove(thisNode)

		# Update subNode Count
		thisParrentNode.lastSubNodeIx_ -= 1

		# Fix ParrentNode and its entire sub-infoTree
		thisParrentNode.updateSubinfoTreeNodeIds()

		# Update json object structure of parrentNode
		# Is parrentNode a orderedDict object?
		if thisParrentNode.isOrderedDict():
			#Y => Delete the Item
			thisParrentNode.item_.pop(thisNode.name_)
		else:
			#N => Assume parrentNode is a list Object
			thisParrentNode.item_.remove(thisNode.item_)		

		return thisParrentNode

	# Remove thisNodes subNode specified by ix
	def removeSubNodeObjByIx(self, nodeIx_=0):
		thisNode = self
		thisParrentNode = thisNode
				
		# Is node Ix valid?
		if nodeIx_ < 0 or nodeIx_ > thisParrentNode.lastSubNodeIx_:
			# NO
			self.error_ = "removeSubNodeObjByIx: Unable to find subNode with Ix " + str(nodeIx_)			
			return self

		# Assume nodeIx is valid
		thisNode = thisParrentNode.subNodes_[nodeIx_]

		# Remove the SubNode
		thisParrentNode.subNodes_.remove(thisNode)

		# Update subNode Count
		thisParrentNode.lastSubNodeIx_ -= 1

		# Fix ParrentNode and its entire sub-infoTree
		thisParrentNode.updateSubinfoTreeNodeIds()

		# Update json object structure of parrentNode
		# Is parrentNode a orderedDict object?
		if thisParrentNode.isOrderedDict():
			#Y => Delete the Item
			thisParrentNode.item_.pop(thisNode.name_)
		else:
			#N => Assume parrentNode is a list Object
			thisParrentNode.item_.remove(thisNode.item_)		

		return thisParrentNode

#----------------------- Remove node Helper/Wrapper Methods ------------------
#----------------------- Remove node Helper Methods (Search from thisNode to end of sub-infoTree) ----------------------	  
	# Remove thisNode
	def removeNode(self):
		thisNode = self

		# Revove thisNode
		thisNode = thisNode.removeNodeObj()

		return thisNode

	# Remove node specified by Id, Search from thisNode to end of its sub-infoTree
	def removeNodeById(self, nodeId_, startNode_ = ""):
		thisNode = self

		# Remove node specified by id
		thisNode = thisNode.removeNodeObjById(nodeId_, startNode_)

		return thisNode

	# Remove node specified by name, Search from thisNode to end of its sub-infoTree
	def removeNodeByName(self, name_, startNode_ = ""):
		thisNode = self

		# Remove node specifide by name
		thisNode = thisNode.removeNodeObjByName(name_, startNode_)

		return thisNode

	# Remove node specified by value, Search from thisNode to end of its sub-infoTree
	def removeNodeByValue(self, value_, startNode_ = ""):
		thisNode = self

		# Remove node specified by value
		thisNode = thisNode.removeNodeObjByValue(value_, startNode_)

		return thisNode			  
#------------------ REMOVE peerNode Helper/Wrapper Methods (Search in thisNodes peerNodes) --------------------------

	# Remove thisNodes peerNode specified by Id, Search in thisNode peerNodes
	def removePeerNodeById(self, nodeId_):
		thisNode = self

		# Remove node specified by id
		thisNode = thisNode.removePeerNodeObjById(nodeId_)

		return thisNode

	# Remove thisNodes peerNode specified by name, Search in thisNode peerNodes
	def removePeerNodeByName(self, name_):
		thisNode = self

		# Remove node specified by name
		thisNode = thisNode.removePeerNodeObjByName(name_)

		return thisNode

	# Remove peerNode relative to node specified value, Search from thisNode to end of its sub-nodeChain
	def removePeerNodeByValue(self, value_):
		thisNode = self

		thisParrentNode = thisNode.removePeerNodeObjByValue(value_)

		return thisParrentNode				  
		
	# Remove thisNodes peerNode specified by Ix
	def removePeerNodeByIx(self, nodeIx_=0):
		thisNode = self

		# Remove node specified by ix
		thisNode = thisNode.removePeerNodeObjByIx(nodeIx_)

		return thisParrentNode
		
#------------------ Remove subNode Helper/Wrapper Methods (Search in thisNodes subNodes)-----------------
	# Remove thisNode subNode specified by Ix, Search in thisNodes subNodes
	def removeSubNode(self, nodeIx_=0):
		thisNode = self

		# Remove node specified by ix
		thisNode = thisNode.removeSubNodeObj(nodeIx_)

		return thisNode		  
	
	# Remove thisNodes subNode specified by Id, Search in thisNodes subNodes
	def removeSubNodeById(self, nodeId_):
		thisNode = self

		# Remove node specified by id
		thisNode = thisNode.removeSubNodeObjById(nodeId_)

		return thisNode		  

	# Remove thisNodes subNode specified by name, Search in thisNodes subNodes
	def removeSubNodeByName(self, name_):
		thisNode = self

		# Remove node specified by name
		thisNode = thisNode.removeSubNodeObjByName(name_)

		return thisNode

	# Remove thisNodes subNode specified by value, Search in thisNodes subNodes
	def removeSubNodeByValue(self, value_):
		thisNode = self

		# Remove node specified by value
		thisNode = thisNode.removeSubNodeObjByValue(value_)

		return thisNode				  
	
	# Remove thisNodes subNode specified by Ix, Search in thisNodes subNodes
	def removeSubNodeByIx(self, nodeIx_=0):
		thisNode = self

		# Remove node specified by ix
		thisNode = thisNode.removeSubNodeObjByIx(nodeIx_)

		return thisNode		  
	
#---------------- node Searching & Navigation Methods -------------------		 

	# returns thisNodes next-peerNode if it has one
	def getNextPeerNode(self):
		thisNode = self
		thisParrentNode = thisNode.parrentNode_

		# Is this rootNode?
		if(thisNode.parrentNode_ ==""):
			# YES => Root node does not have peer nodes, ret nothing
			self.error_ = "getNextPeerNode: rootNodes dont have peerNodes"			  
			return ""

		# Assume this node does have peerNodes
		# Is this last-node in this sub-nodeChain?
		if(thisNode.nodeIx_ >= thisParrentNode.lastSubNodeIx_): #Remember its Binary count so array->lastIx = array->size - 1
			# YES => No more peerNodes in this sub-nodeChain
			self.error_ = "getNextPeerNode: no next peerNode found"			   
			return ""

		# Assume there are more peerNodes
		# Get next peerNode
		thisNode = thisParrentNode.subNodes_[thisNode.nodeIx_+1]
		
		return thisNode

	# returns thisNodes prev-peerNode if it has one
	def getPrevPeerNode(self):
		thisNode = self
		thisParrentNode = thisNode.parrentNode_

		# Is this rootNode?
		if(thisNode.parrentNode_ ==""):
			# YES => Root node does not have peer nodes, ret nothing
			self.error_ = "getPrevPeerNode: rootNodes dont have peerNodes"
			return ""

		# Assume this node does have peerNodes
		# Is this first-node in this sub-nodeChain?
		if(thisNode.nodeIx_ <= 0):
			# No more prev peerNodes in this sub-nodeChain
			self.error_ = "getPrevPeerNode: no previous peerNode found"			   
			return ""

		# Assume there are more prev-peerNodes
		# Get prev peerNode
		thisNode = thisParrentNode.subNodes_[thisNode.nodeIx_-1]
		
		return thisNode

	# Return the nextNode if all nodes hassent been looked-through
	# use startNode_ if you want to restrict search to a specific node and its sub-infoTree
	# TODO: Implement this semi-recursive node Traversal technique used in my DictTree semi-recursive node Traversal method getNextItem()
	# BUT IN NEW VERSION, since current semi-recursive technique allso works!!
	def getNextNode(self, startNode_=""):
		thisNode = self

		# Has node travesal/look-through been restricted to a specific node and its sub-infoTree?
		if(startNode_ != ""):
			# Has sub-infoTree been been looked-through?
			# Is thisNode at startNodes level?
			if(thisNode.nodeLevel_ == startNode_.nodeLevel_):
				#Y => Is thisNode starNodes peerNode?
				if(thisNode != startNode_):
					# YES => Tree read complete
					return ""
			# is thisNode on a higher nodeLevel then startNode?
			if(thisNode.nodeLevel_ < startNode_.nodeLevel_):
				# YES => Tree read complete
				return ""

		# is thisNode a leafNode?
		if(thisNode.lastSubNodeIx_ != -1):
			# NO => Get first subNode
#-----------------------------------------------------------------------------			  
#**			   thisNode = thisNode.getFirstSubNode() # In-line for speed
#-----------------------------------------------------------------------------
			thisNode = thisNode.subNodes_[0]
#--------------------------------------------------------------------------------				 
			return thisNode
		else: # Assume no more subNode or leafNode
			# YES => Get next valid node
			# Loop until next valid node found or end of tree
			while(True):
				# Has node travesal/look-through been restricted to a specific node and its sub-infoTree?
				if(startNode_ != ""):
					# YES => Has sub-infoTree been been looked-through?
					# is thisNode on same nodeLevel as startNode?
					if(thisNode.nodeLevel_ == startNode_.nodeLevel_):
						# YES
						#  Is thisNode the startNode?
						if(thisNode != startNode_):
							# NO => Tree read complete
							return ""

					# Is thisNodes at a higher nodeLevel then startNode?
					if(thisNode.nodeLevel_ < startNode_.nodeLevel_):
						# YES => Tree read complete
						return ""

				# Keep Track of thisNode
				prevNode = thisNode
#------------------------------------------------------------------------------------			   
#**				   thisNode = thisNode.getNextPeerNode() # In-line for speed
#------------------------------------------------------------------------------------
				# Loop until valid nextNode found or end Of Tree
				while(True):
					# Keep track of parrentNode
					thisParrentNode = thisNode.parrentNode_
					# Is this rootNode?
					if(thisParrentNode != ""):
						# NO =>
						#**lastSubNode = thisParrentNode.subNodes_[thisParrentNode.lastSubNodeIx_]
						# Is thisNode the last subNode?
						if(thisNode.nodeIx_ != thisParrentNode.lastSubNodeIx_): # Remember binary math!!
							# NO => Move/Point to next subNode
							thisNode = thisParrentNode.subNodes_[thisNode.nodeIx_+1]
							# Forced exit loop, nextNode found
							break
						else:
							# YES => Try next peerNode
							thisNode = thisParrentNode
					else:
						# YES => Signal no more subNodes for thisNode
						thisNode=""
						# Forced exit loop, no nextNode found
						break
#-------------------------------------------------------------					  
				# Is thisNode valid?
				if(thisNode != ""):
					# YES => Retun nextNode
					return thisNode
				else: 
					# NO => Restore prevNode state
					thisNode = prevNode
					# Assume no more peerNode on this sub-infoTree
					# Is thisNodes Parrent startNode?
					# Has startNode been specified?
					if(startNode_ != ""):
						# YES
						# Is thisNodes parrentNode the startNode?
						if(thisNode.parrentNode_ == startNode_):
							# YES => Signal Tree read complete
							return ""

	# Return the prevNode if all nodes hassent been looked-through
	# use startNode_ if you want to restrict search to a specific node and its sub-infoTree
	def getPrevNode(self, startNode_=""):
		thisNode = self

		# Look through infoTree
		while(thisNode != ""):
			# Keep track of prevNode
			prevNode = thisNode

			# Try nextNode
			thisNode = thisNode.getNextNode(startNode_)

			# Was a valid nextNode found?
			if thisNode == "":
				#N => Signal prevNode not found in the specified infoTree
				return ""

			# Assum nextNode was found
			# Is this the node we are looking for?, hence node before this
			if thisNode == self:
				#Y => Signal prevNode found
				return prevNode
		
		# Assume prevNode not found
		return ""

	def getParrentNode(self):
		# Get thisNodes parrentNode
		return self.parrentNode_

	def getSubNodeCount(self):
		return self.lastSubNodeIx_ + 1

	def hasSubNodes(self):
		if self.lastSubNodeIx_ > -1:
			return True
		else:
			return False

	def hasParrentNode(self):
		# Is this a rootNode?
		if self.parrentNode_ != "":
			# NO
			return True
		else: # YES => Assume this is rootNode
			return False

	# Returns wheter thisNode is root
	def isRootNode(self):
		# Is this the rootNode?
		if(self.parrentNode_ == ""):
			return True
		else:
			return False
			
	# Method used to go all the way back to rootNode
	def getRootNode(self):
		thisNode = self
		# Move up the infoTree until rootNode is found
		while(thisNode.parrentNode_ != ""):
			thisNode = thisNode.parrentNode_
		return thisNode

	# Method that updates the node name and "assoc" json object structure
	# STATUS: TESTED->OK
	def setName(self, name_):		 
		thisNode = self
		thisParrentNode = thisNode.parrentNode_
		 	  
		# Is this rootNode
		if thisParrentNode != "":
			#N => Update the parrentItem to reflect changes in json object structure
			# Update parrentItem to ensure it reflects the changes in the json object structure
			# Reconstruct sub-infoTree to refelct the new json object

			# Is thisParrent a orderdDict
			if thisParrentNode.isOrderedDict():
				#Y => Update json object structure to reflect the new name
				thisParrentNode.item_.pop(thisNode.name_)
				thisParrentNode.insertDictItemByIx(thisNode.nodeIx_, name_, thisNode.item_)
			else:
				#N => Assume list, update json object structure to reflect the new name
				thisParrentNode.item_.insert(thisNode.nodeIx_, thisNode.item_)
				thisParrentNode.item_.pop(thisNode.nodeIx_)

		# Update the Node->name and "assoc" json object structure
		thisNode.name_ = name_

		return True

	# Get the Node->name
	def getName(self):
		# Return the node->name
		return self.name_

	# Method used to update thisNodes sub-infoTree to reflect json object structure contained in item_
	# Status: DONE->TESTED->SO FAR SO GOOD
	def setValue(self, item_ = ""):
		thisNode = self
		thisParrentNode = thisNode.parrentNode_

		# Has Item been specified?
		if item_ == "":
			#N => Assum thisNodes item is used
			item_ = thisNode.item_

		# Is this rootNode
		if thisParrentNode != "":
			#N => Update the parrentItem to reflect changes in json object structure
			# Update parrentItem to ensure it reflects the changes in the json object structure
			# Reconstruct sub-infoTree to refelct the new json object

			# Is thisParrent a orderdDict
			if thisParrentNode.isOrderedDict():
				#Y => update the dict childItem
				thisParrentNode.item_[thisNode.name_] = item_
			else:
				#N => Assume list childItem
				thisParrentNode.item_[thisNode.nodeIx_] = item_
				
				# Is this last-subNode?
#				if thisNode.nodeIx_ != thisParrentNode.lastSubNodeIx_:
					#N => use insert
					# nodeIx + 1 => after nodeIx
#					thisParrentNode.item_.insert(thisNode.nodeIx_ + 1, thisNode.item_)
#					thisParrentNode.item_.pop(thisNode.nodeIx_)
#				else:
					#Y => Use add since you cannot insert a node after last-subNode
#					thisParrentNode.item_							
		   
		# Update thisItem
		thisNode.item_ = item_

		# Keep Track of ParrentNode
		# Is thisNode rootNode?
#**		if thisNode.parrentNode_ != "":
			# 
			#N => Point to parrentNode to ensure all affected nodes are updated
#**			thisNode = thisNode.parrentNode_		

		# Update the sub-infoTree
		# Remove all subNodes
		thisNode.subNodes_ = []
		thisNode.lastSubNodeIx_ = -1

		# Reconstruct sub-infoTree to refelct the new json object
		# Create root trackingNode
		thisTrackingNode = trackingNode(thisNode.name_, thisNode.item_) # -1 to signal read first subNode by def.
		myRootTrackingNode = thisTrackingNode.copyNode()
		# Keep track of prev trackingNode, so we can detemin relation between this and prev
		prevTrackingNode = thisTrackingNode		

		# Keep track of rootNode
		rootNode = thisNode.getRootNode()

		# Will thisNode be a leafNode?
		if thisTrackingNode.isSimpleLeafNode():
			#Y => Forced exit leafNodes dont have subNodes
			return True

		# Look through json object using the trackingNode
		# Loop until all nodes has been read
		while(thisTrackingNode != ""):

			# Keep track of prev trackingNode, so we can detemin relation between this and prev
			prevTrackingNode = thisTrackingNode
			# Get next trackingNode
			thisTrackingNode = thisTrackingNode.getNextNode(myRootTrackingNode)
			
			# Has a new node been found?
			if thisTrackingNode != "":
				#Y => Add the new node
				# Is newNode subNode of thisNode?
				if thisTrackingNode.prevNode_ == prevTrackingNode:
					#Y					
					# Is jsonTree in sync with json object structure, hence do both structures point to same parrentNode?
					if  thisNode.nodeLevel_ != thisTrackingNode.nodeLevel_ - 1:					
						#N => find correct parrentNode for jsonTree
						# Find thisNodes parrent "Ensure jsonTree is in sync with json object structure"
						thisParrentTrackingNode = thisTrackingNode.getParrentNode()
						# Find thisNode parrentNode
						#**thisParrentNode = thisNode.getNodeById(thisParrentTrackingNode.nodeId_)
						thisNode = rootNode.getNodeById(thisParrentTrackingNode.nodeId_)
					
					# Add new subNode and point/move to new subNode
					newNode = jsonNode(thisTrackingNode.key_, thisTrackingNode.value_, thisNode)
					# Call core methods to avoid recursive call to setValue
					thisNode = thisNode.addSubNodeObj(newNode)												
				else: #N
					# Is newNode peerNode of thisNode and a non-rootNode?
					if thisTrackingNode.prevNode_ == prevTrackingNode.prevNode_ and thisTrackingNode.prevNode_ != "":
						#Y => Add new peerNode and point/move to new peerNode
						newNode = jsonNode(thisTrackingNode.key_, thisTrackingNode.value_, thisNode.parrentNode_)
						# Call core methods to avoid recursive call to setValue
						thisNode = thisNode.addPeerNodeObj(newNode)
					else:
						#N => Assume jsonTree is out of sync with json object structure
						# Find thisNodes parrent "Ensure jsonTree is in sync with json object structure"
						thisParrentTrackingNode = thisTrackingNode.getParrentNode()
						# Find thisNode parrentNode
						#**thisParrentNode = thisNode.getNodeById(thisParrentTrackingNode.nodeId_)
						thisNode = rootNode.getNodeById(thisParrentTrackingNode.nodeId_)
						# Add new subNode
						newNode = jsonNode(thisTrackingNode.key_, thisTrackingNode.value_, thisNode)
						# Call core methods to avoid recursive call to setValue
						thisNode = thisNode.addSubNodeObj(newNode)					

		# Auto Discover Object Type
		# Does thisNode contain a OrderedDict Object?
		if self.isOrderedDict(item_):
			#Y => Signal thisNode contains orderedDict object
			self.type_ = 0

		# Does thisNode contain a list obejct?
		if self.isList(item_):
			#Y => Signal thisNode contains list object
			self.type_ = 1

		# Does thisNode contain a string object
		if self.isString(item_):
			#Y => Signal thisNode contains a string object
			self.type_ = 2

		if self.isNumber(item_):
			#Y => Signal thisNode contains a number object?
			self.type_ = 3

		return True

	# Method used to export a json object structre that reflect the jsonTree of a this or a specfied node
	# Status: DONE->TESTED->WORKS [DEPRECIATED json object structure update by setValue and setName]
	def exportJsonObject(self, node_):
		thisNode = self
		changedNode = thisNode
		thisParrentNode = thisNode.parrentNode_

		# Has a node been specified?
		if node_ != "":
			# Assume thisNodes json object structure should be synce with jsonTree
			thisNode = node_
			changedNode = thisNode
			thisParrentNode = thisNode.parrentNode_
		
		# Is thisNode a leafNode?
		if thisNode.lastSubNodeIx_ == -1:
			#Y => leafNodes dont have a json structure so just return the item
			return thisNode.item_

		# Keep track of next parrentNode
		nextParrentNode = thisNode.getNextPeerNode()

		# Keep track of rootNode
		rootNode = thisNode.getRootNode()
#--------------------------------
		# Is thisNode a OrderedDict
		if thisNode.isOrderedDict():
			#Y
			thisItem = OrderedDict()
		else:
			#N => Assume thisItem is a list "array" object
			thisItem = []

		# Reconstruct sub-infoTree to refelct the new json object
		# Create rootNode of trackingTree
		thisTrackingNode = jsonNode(thisNode.nodeId_, thisItem) # -1 to signal read first subNode by def.
		myRootTrackingNode = thisTrackingNode.copyNode()

		# Keep track of prevNode
		prevNode = thisNode


		# Look through json object using the trackingNode
		# Loop until all nodes has been read

		return True		

	# Get the Node->value
	def getValue(self):
		# Return the node->value
		return	self.getString(self.item_)

	# auto gen. new nodeId for non root nodes
	def genNodeId(self):
		# Ensure nodeId is not allready generated
		# Has thisNodes nodeId allready been specified?
		if(self.nodeId_ != ""):
			# YES
			self.error_ = "genNodeId: thisNode allready has a Id!!"
			return False

		# Is this root node?
		if(self.parrentNode_ == ""):
			# YES => Root node key cannot be changed forced exit
			return False

		# Generate and update new key "NodeId"		  
		self.nodeId_ = self.parrentNode_.nodeId_ + self.nodeLevelSeparator_ + str(self.nodeIx_)
		return True

#------------------------ nodeId, ix, and Level methods, Ensures that a sub nodes location is always reflected by its Id, level, ix ----------
	# Auto update thisNodes and all its peerNodes nodeId & nodeLevels in case they have been corrupted by copy, insert or replace functions
	def updatePeerNodeIds(self):
		thisNode = self
		thisParrentNode = thisNode.parrentNode_

		# Is this rootNode?
		if(thisNode.parrentNode_ == ""):
			# YES => Root node key cannot be changed forced exit
			self.error_ = "updatePeerNodeIds: rootNodes dont have peerNodes!!"			  
			return False
		
		# Generate & update NodeIds
		ix = 0
		for node in thisParrentNode.subNodes_:
			# Get next node
			# Fix node ix just in case it has been corrupted too
			node.nodeIx_ = ix
			node.nodeId_ = thisParrentNode.nodeId_ + node.nodeLevelSeparator_ + str(node.nodeIx_)
			# update thisNodes nodeLevel
			node.nodeLevel_ = node.getNodeLevel()

			# Update node ix
			ix += 1			   
		
		# Return number of updated nodeIds
		return ix

	# Auto update thisNode & its subNodes nodeIds & nodeLevels in case they have been corrupted by copy, insert or replace functions
	def updateSubNodeIds(self):
		thisNode = self
		thisParrentNode = thisNode.parrentNode_

		# Fix thisNode ix
		# Get Index
		ix = 0
		nodeFound = 0
		for node in thisParrentNode.subNodes_:
			# Is this the subNode we are looking for?
			if(thisNode == node):
				# YES => Ensure thisNode points to the subNode
				thisNode = node
				# node found, signal it
				nodeFound = 1
				break

			# Update node ix
			ix += 1

		# Was the node found?
		if(nodeFound):
			# YES => Update index, nodeId & nodeLevel
			thisNode.nodeIx_ = ix
			thisNode.nodeId_ = thisParrentNode.nodeId_ + thisNode.nodeLevelSeparator_ + str(thisNode.nodeIx_)
			thisNode.nodeLevel_ = thisNode.getNodeLevel()

			# Has value frequency been initialized?
			if(thisNode.freq_ == 0):
				thisNode.freq_ = 1
		else:
			# Unable to locate the node in parrentNodes subNodes
			self.error_ = "updateSubNodeIds: Unable to locate thisNode in parrentNode sub-nodeChain!!"
			return ""

		# Is thisNode as leafNode?
		if(thisNode.lastSubNodeIx_ == -1):
			# YES => leafNodes does not have subNodes!!
			self.error_ = "updateSubNodeIds: leafNodes does not have subNodes!!"
			return ""

		# Generetae & update all thisNodes subNodes nodeId
		ix = 0
		for node in thisNode.subNodes_:
			# Fix node ix just in case it has been corrupted too
			node.nodeIx_ = ix			 
			# Generate and update new NodeId		
			node.nodeId_ = thisNode.nodeId_ + node.nodeLevelSeparator_ + str(node.nodeIx_)
			# update thisNodes nodeLevel
			node.nodeLevel_ = node.getNodeLevel()
			# Has value frequency been initialized?
			if(node.freq_ == 0):
				node.freq_ = 1

			# Update node ix
			ix += 1

		return ix

	# Update thisNode & its sub-infoTrees nodesIds & Levels in case they have been corrupted by moving nodes around
	def updateSubinfoTreeNodeIds(self):
		thisNode = self
		startNode = thisNode.parrentNode_ # Must be from parrent to detect when the thisNodes sub-infoTree has been looked-through

		# look-through thisNodes sub-infoTree
		while(thisNode != ""):
			# Fix thisNodes subNodeIds
			thisNode.updateSubNodeIds()

			# Get next node
			thisNode = thisNode.getNextNode(startNode)

		return self 

	# Update the subNodes parrentNode association/linking to thisNode, to ensure they have
	# thisNode as parrentNode. Usefull after parrentNode change after copy, insert, replace actions on nodes
	def updateParrentNodeLink(self):
		thisNode = self

		# Is this a leafNode?
		if(thisNode.lastSubNodeIx_ == -1):
			# YES => leafNodes does not have subNodes
			self.error_ = "updateParrentNodeLink: leafNodes dont have subNodes!!"			 
			return ""

		# look-through thisNodes subNodes/sub-nodeChain
		for node in thisNode.subNodes_:
			# fix subNodes association/link to parrentNode
			node.parrentNode_ = thisNode

		return thisNode	   
#-------------------------------------------		

	def getNodeId(self):
		# Return this nodes NodeId
		return self.nodeId_

# ----- Analysis functionality ------

#------------------------------------

	# Swaps thisNode and its sub-infoTree with otherNode and its sub-infoTree
	# usefull when sorting by freq
	def swapNodes(self, otherNode_):
		thisNode = self
		
		thisParrentNode = thisNode.parrentNode_
		otherParrentNode = otherNode_.parrentNode_
		
		# Is this rootNode?
		if((thisParrentNode == "") | (otherParrentNode == "")):
			# YES => rootNodes cannot be replaced
			self.error_ = "swapNodes: rootNodes cannot be replaced!!"			 
			return ""

		# Create copies of the nodes to swap # NOTE: MUST BE COPIES & NOT ORG SINCE THE ORG NODES ARE LOST ON FIRST NODE "REPLACE"
		nodeA = thisNode.copyNodeObj()
		nodeB = otherNode_.copyNodeObj()			 

		# Get nodeIx of the nodes to swap # NOTE: MUST be ix copies since the Org node->nodeIx's are swapped!!
		ixA = nodeA.nodeIx_
		ixB = nodeB.nodeIx_
		
		# Swap the parrentNodes (fix parrent association/linking)
		nodeA.parrentNode_ = otherParrentNode
		nodeB.parrentNode_ = thisParrentNode

		# Swap the subNodes NOTE: For some reason node cannot be swapped unless its directly accessed in the array :O
		thisParrentNode.subNodes_[ixA] = nodeB
		otherParrentNode.subNodes_[ixB] = nodeA

		# Fix nodeIds for the swapped nodes and their sub-infoTree
		thisParrentNode.subNodes_[ixA].updateSubinfoTreeNodeIds()
		otherParrentNode.subNodes_[ixB].updateSubinfoTreeNodeIds()
				
		return thisParrentNode.subNodes_[ixA]
		
	# Swaps thisNode sub-infoTree with otherNodes sub-infoTree
	# usefull when sorting by freq
	def swapSubNodes(self, otherNode_):
		thisNode = self
		
		thisParrentNode = thisNode.parrentNode_
		otherParrentNode = otherNode_.parrentNode_
		
		# Is this rootNode?
		if((thisParrentNode == "") | (otherParrentNode == "")):
			# YES => rootNodes cannot be replaced
			self.error_ = "swapSubNodes: rootNodes cannot be replaced!!"			
			return ""

		# Create copies of the nodes to swap NOTE: MUST BE COPIES SINCE THE ORG. NODES ARE LOST ON FIRST "REPLACE"
		nodeA = thisNode.copyNodeObj()
		nodeB = otherNode_.copyNodeObj()			 
		
		# Swap the sub-infoTrees
		thisNode.subNodes_ = nodeB.subNodes_
		thisNode.lastSubNodeIx_ = nodeB.lastSubNodeIx_

		otherNode_.subNodes_ = nodeA.subNodes_
		otherNode_.lastSubNodeIx_ = nodeA.lastSubNodeIx_

		# Fix parrentNode assocation/linking for thisNode
		for node in thisNode.subNodes_:
			node.parrentNode_ = thisNode

		# Fix parrentNode association/linking for otherNode
		for node in otherNode_.subNodes_:
			node.parrentNode_ = otherNode_

		# Fix nodeIds for the swapped nodes and their sub-infoTree
		thisNode.updateSubinfoTreeNodeIds()
		otherNode_.updateSubinfoTreeNodeIds()
				
		return thisNode

	# Removes all peerNodes in the nodeChain, thisNode exist in
	def removePeerNodes(self):
		thisNode = self
		thisParrentNode = thisNode.parrentNode_

		# Is this rootNode?
		if(thisNode.parrentNode_ == ""):
			# YES => rootNode does not have peerNodes
			self.error_ = "removePeerNodes: rootNodes dont have peerNodes & rootNodes cannot be removed!!"			  
			return ""
	
		# Remove all subNodes "destroy sub-nodeChain"
		thisParrentNode.subNodes_ = []
		thisParrentNode.lastSubNodeIx_ = -1

		return thisParrentNode

	# Removes thisNodes subNodes if it has any
	def removeSubNodes(self):
		thisNode = self

		# Is this leafNode?
		if(thisNode.lastSubNodeIx_ == -1):
			# YES => leafNodes have no subNodes
			self.error_ = "removeSubNodes: leafNodes dont have subNodes!!"			  
			return ""

		# Remove all subNodes "destroy sub-nodeChain"
		thisNode.subNodes_ = []
		thisNode.lastSubNodeIx_ = -1		  

		return thisNode

#--------------------- COPY node Obj Methods ----------------------
	# Returns a copy of thisNode and its entire sub-infoTree
	def copyNodeObj(self):
		thisNode = self
		startNode = thisNode
		
		# Create new infoTree
		infoTreeCopy = jsonNode(thisNode.name_, thisNode.item_, thisNode.parrentNode_, thisNode.nodeLevelSeparator_)
		thatNode = infoTreeCopy

		# Copy thisNode attributes one-by-one to copy of node to ensure they have correct values
		infoTreeCopy.nodeId_ = thisNode.nodeId_ # No need handled by constructor
		infoTreeCopy.nodeIx_ = thisNode.nodeIx_ # No need handled by construtor when parrentNode is known
		infoTreeCopy.nodeLevel_ = thisNode.nodeLevel_ # No need handled by constructor
		infoTreeCopy.freq_ = thisNode.freq_
		infoTreeCopy.uniqueLevel_ = thisNode.uniqueLevel_
		
		# Does thisNode hav subNodes?
		if(thisNode.lastSubNodeIx_ == -1):
			# NO => No sub nodes to copy just return copy of this node
			return infoTreeCopy

		# Keep track of prev node
		prevNode = thisNode
		# Get First node of sub-infoTree
		thisNode = thisNode.getNextNode(startNode)

		# Copy sub-infoTree node-by-node
		while(thisNode != ""):
					
			# Is next node a peerNode?
			if(thisNode.nodeLevel_ == prevNode.nodeLevel_):
				# YES => Add new peerNode
				thatNode = thatNode.addPeerNode(thisNode.name_, thisNode.item_)

			# is next node a subNode?
			if(thisNode.nodeLevel_ > prevNode.nodeLevel_):
				# YES => add new subNode
				thatNode = thatNode.addSubNode(thisNode.name_, thisNode.item_)

			# is next node parrentNode?
			if(thisNode.nodeLevel_ < prevNode.nodeLevel_):
				# YES => add parrentNode
				thatNode = thatNode.parrentNode_
				thatNode = thatNode.addPeerNode(thisNode.name_, thisNode.item_)

			# Keep track of prev node
			prevNode = thisNode
			# Get Next node
			thisNode = thisNode.getNextNode(startNode)

		# Return copy of the node and its sub-infoTree
		return infoTreeCopy

	# Returns a copy of thisNodes sub-infoTree
	# basically the same as CopyNode except this one makes rootNode a standard root node
	def copySubNodesObj(self):
		thisNode = self
		startNode = thisNode
		
		# Create new infoTree
		infoTreeCopy = jsonNode("", "", "", thisNode.nodeLevelSeparator_)
		thatNode = infoTreeCopy

		# Does thisNode hav subNodes?
		if(thisNode.lastSubNodeIx_ == -1):
			# NO => No sub nodes to copy just return copy of this node
			return infoTreeCopy

		# Keep track of prev node
		prevNode = thisNode
		# Get First node of sub-infoTree
		thisNode = thisNode.getNextNode(startNode)

		# Copy sub-infoTree node-by-node
		while(thisNode != ""):
					
			# Is next node a peerNode?
			if(thisNode.nodeLevel_ == prevNode.nodeLevel_):
				# YES => Add new peerNode
				thatNode = thatNode.addPeerNode(thisNode.name_, thisNode.item_)

			# is next node a subNode?
			if(thisNode.nodeLevel_ > prevNode.nodeLevel_):
				# YES => add new subNode
				thatNode = thatNode.addSubNode(thisNode.name_, thisNode.item_)

			# is next node parrentNode?
			if(thisNode.nodeLevel_ < prevNode.nodeLevel_):
				# YES => add parrentNode
				thatNode = thatNode.parrentNode_
				thatNode = thatNode.addPeerNode(thisNode.name_, thisNode.item_)

			# Keep track of prev node
			prevNode = thisNode
			# Get Next node
			thisNode = thisNode.getNextNode(startNode)

		# Return copy of the node and its sub-infoTree
		return infoTreeCopy

#-------------------------------------------------		  

# --------------------- Simi Recursive sub-infoTree readering ----------------
	# Reads node in thisNodes sub-infoTree node-by-node
	# Uses all infoTree methods so it abit slow due to alot of function calls
	# Just a demonstartion of how the infoTree can be looked-through using its methods
	def getNextNodeInSubinfoTree(self, startNode_):
		thisNode = self

		# Has sub-infoTree been been looked-through?
		if(thisNode.nodeLevel_ == startNode_.nodeLevel_):
			if(thisNode.nodeId_ != startNode_.nodeId_):
				# YES => Tree read complete
				return ""
		if(thisNode.nodeLevel_ < startNode_.nodeLevel_):
			# YES => Tree read complete
			return ""

		# does this node have subNodes?
		if(thisNode.lastSubNodeIx_ != -1):
			# YES => get first subNode
			thisNode = thisNode.getFirstSubNode()
			return thisNode
		else: # Assume no more subNode or leafNode
			# Get next valid node
			while(True):
				# Has sub-infoTree been been read?
				if(thisNode.nodeLevel_ == startNode_.nodeLevel_):
					if(thisNode.nodeId_ != startNode_.nodeId_):
						# YES => Tree read complete
						return ""
				if(thisNode.nodeLevel_ < startNode_.nodeLevel_):
					# YES => Tree read complete
					return ""

				# Keep Track of thisNode
				prevNode = thisNode
				thisNode = thisNode.getNextPeerNode()
				# Is thisNode valid?
				if(thisNode != ""):
					# YES
					return thisNode
				else:
					# NO => Restore prevNode state
					thisNode = prevNode
					# Assume no more peerNode on this sub-infoTree
					# Is thisNodes parrentNode the startNode?
					if(thisNode.parrentNode_ == startNode_):
						# YES => Tree read complete
						return ""
					else: # NO
						thisNode = thisNode.getNextParrentNode()
					# Is thisNode valid?
					if(thisNode != ""):
						# YES
						return thisNode
					else:
						# NO => Restore prevNode state
						thisNode = prevNode

#-----------------------------

	# Method used to stip nodeId from dictornary keys so it is represented uniqueless in JSON Trees
	def stripNodeId(self, data_):
		seperatorIdIx = 0
		prevIx = 0
		while(True):
			# Keep track of prevIx
			prevIx = seperatorIdIx

			# find ix of nodeId seperator Id
			seperatorIdIx = data_.find("#", seperatorIdIx)

			# Was a seperator Id found?
			if seperatorIdIx == -1:
				#NO => last/true nodeId seperator id located
				# return uniqueless name
				# Did the name have any seperator ID?
				if prevIx == 0:
					#NO => Fix prevIx so data is returned unchanged
					prevIx = len(data_) + 1 # +1 to compensate for the -1
				
				return data_[:prevIx-1] # -1 to strip the sperator ID
					
			else:
				# set new search startIx
				seperatorIdIx = seperatorIdIx + 1

	# Method that strips the key part from a dictonary key using nodeId's for unique naming "[key]#[nodeId]"
	# So that the nodeId can be extracted and used to locate the node inside a OrderedDict Tree
	# If key is omitted thisNodes key is assumed
	def stripKey(self, key_=""):
		# Has a key been specifed?
		if key_ == "":
			#NO => Assume thisNode
			key_ = self.name_

		seperatorIdIx = 0
		prevIx = 0
		while(True):
			# Keep track of prevIx
			prevIx = seperatorIdIx

			# find ix of nodeId seperator Id
			seperatorIdIx = key_.find("#", seperatorIdIx)

			# Was a seperator Id found?
			if seperatorIdIx == -1:
				#NO => last/true nodeId seperator id located
				# return unique nodeId
				# Did the key have any seperator ID?
				if prevIx == 0:
					#NO => return empty string
					return ""
				
				return key_[prevIx:len(key_)] #
					
			else:
				# set new search startIx
				seperatorIdIx = seperatorIdIx + 1				 


#----------------- Data Conversion methods -----------------
	# Method used to convert a infoTree or subInfoTree to a Ordered Dictonary Tree object so it can be converetd to JSON and stored in a noSQL data format 
	# for further Analysis
	# TESTED: OK
	# Process: infoTree => OrderedDict Tree
	def conv2DictTree(self, startNode_ = ""):
		thisDict = OrderedDict()
		parrentDict = OrderedDict()
		someDict = OrderedDict()
		myNode = jsonNode(self.name_, self.item_)
		someRootNode = ""
		someNode = ""
		dictAdded = 0 # Flags that indicates wether a new dict node has been added

		# Start the semi-recursive process by setting root-node
		thisNode = self
		prevNode = self
		while(1):

			if thisNode == "":
				print("infoTree Read complete...")
				break
			else:
				print("Node found: " + "key: " + thisNode.nodeId_ + " Name: " + thisNode.name_ + " value: " + thisNode.getValue())

				# Reset new dict node added flag
				dictAdded = 0

				# Is this first node "rootNode"?
				if thisNode == self:
					#YES Add first child node
					myNode = myNode.getRootNode()

					# Is this a leafNode?
					if thisNode.isLeafNode():
						#YES => Add field:value
						myNode.item_ = thisNode.item_
						myNode.name_ = thisNode.name_

					else: # NO => Add dict item
						# Create unique dict key
						thisNodeId = thisNode.name_ + "#" + thisNode.nodeId_
						
						someDict[thisNodeId] = OrderedDict() #thisNode.item_
					
						# Add Root Dict node
						myNode.item_ = someDict
					
					# Keep track of dictonary object
					#**myNode = myNode.addSubNode(thisNode.name_, someDict)

					# Keep track of prev node
					prevNode = thisNode

					dictAdded = 1

				# Is thisNode a peerNode?
				if (thisNode.parrentNode_ == prevNode.parrentNode_) & (thisNode != self):
					#YES =>
					# Find parrent Dict
					someRootNode = myNode.getRootNode()
					someNode = someRootNode.getNodeById(thisNode.parrentNode_.nodeId_)
					parrentDict = someNode.item_

					# Create unique dict key
					thisNodeId = thisNode.name_ + "#" + thisNode.nodeId_
					parrentNodeId = thisNode.parrentNode_.name_ + "#" + thisNode.parrentNode_.nodeId_

					# Is this a leafNode?
					if thisNode.isLeafNode():
						#YES => Add field:value
						thisDict = parrentDict[parrentNodeId]
						thisDict[thisNodeId] = thisNode.item_

						# Keep track of dictonary object
						myNode = myNode.addPeerNode(thisNode.name_, thisNode.item_)

					else: # NO => Add child dict item
						# Add child dict

						someDict = OrderedDict() # New dict
						#**someDict[thisNodeId] = thisNode.item_
						#**parrentDict[parrentNodeId] = someDict
						thisDict = parrentDict[parrentNodeId]
						thisDict[thisNodeId] = someDict

						# Keep track of dictonary object
						myNode = myNode.addPeerNode(thisNode.name_, thisDict) #someDict)

					# Keep track of prev node
					prevNode = thisNode

					dictAdded = 1

				# Is thisNode a childNode?
				if thisNode.parrentNode_ == prevNode:
					#YES => Add new child Dict
					# Find parrent dict
					someRootNode = myNode.getRootNode()
					someNode = someRootNode.getNodeById(prevNode.nodeId_)
					parrentDict = someNode.item_

					# Create unique dict key
					thisNodeId = thisNode.name_ + "#" + thisNode.nodeId_
					parrentNodeId = thisNode.parrentNode_.name_ + "#" + thisNode.parrentNode_.nodeId_

					# Is this a leafNode?
					if thisNode.isLeafNode():
						#YES => Add field:value
						thisDict = parrentDict[parrentNodeId]
						thisDict[thisNodeId] = thisNode.item_

						# Keep track of dictonary object
						myNode = someNode.addSubNode(thisNode.name_, thisNode.item_)

					else: # NO => Add child dict item
						# Add Child dict						

						someDict = OrderedDict()
						#**someDict[thisNodeId] = thisNode.item_
						#**parrentDict[parrentNodeId] = someDict
						thisDict = parrentDict[parrentNodeId]
						thisDict[thisNodeId] = someDict
					
						# Keep track of dict object
						myNode = someNode.addSubNode(thisNode.name_, thisDict)#someDict)

					# Keep track of prev node
					prevNode = thisNode

					dictAdded = 1

				# Is thisNode a parrentNode?
				if thisNode == prevNode.parrentNode_:
					# YES => find the parrent dict
					someRootNode = myNode.getRootNode()
					someNode = someRootNode.getNodeById(thisNode.parrentNode_.nodeId_)
					parrentDict = someNode.item_

					# Create unique dict key
					thisNodeId = thisNode.name_ + "#" + thisNode.nodeId_
					prevNodeId = prevNode.name_ + "#" + prevNode.nodeId_
					parrentNodeId = thisNode.name_ + "#" + thisNode.nodeId_

					# Is this a leafNode?
					if thisNode.isLeafNode():
						#YES => Add field:value
						thisDict = parrentDict[parrentNodeId]
						thisDict[thisNodeId] = thisNode.item_

						# Keep track of dictonary object
						myNode = someNode.addSubNode(thisNode.name_, thisNode.item_)

					else: # NO => Add child dict item
						# Add child dict

						someDict = OrderedDict()
						#**someDict[prevNodeId] = prevNode.item_
						#**parrentDict[parrentNodeId] = someDict
						thisDict = parrentDict[parrentNodeId]
						thisDict[prevNodeId] = someDict

						# Keep track of dict object
						myNode = someNode.addSubNode(thisNode.name_, thisDict)#someDict)

					# Keep track of prev node
					prevNode = thisNode

					dictAdded = 1

				# Is thisNode a new parrent node
				if (thisNode != prevNode.parrentNode_) & dictAdded == 0:
					# YES => Find its parrent node
					someRootNode = myNode.getRootNode()
					someNode = someRootNode.getNodeById(thisNode.parrentNode_.nodeId_)
					parrentDict = someNode.item_

					# Create unique dict key
					thisNodeId = thisNode.name_ + "#" + thisNode.nodeId_
					parrentNodeId = thisNode.parrentNode_.name_ + "#" + thisNode.parrentNode_.nodeId_

					# Is this a leafNode?
					if thisNode.isLeafNode():
						#YES => Add field:value
						thisDict = parrentDict[parrentNodeId]
						thisDict[thisNodeId] = thisNode.item_

						# Keep track of dictonary object
						myNode = someNode.addSubNode(thisNode.name_, thisNode.item_)

					else: # NO => Add child dict item
						# Add child dict
						
						someDict = OrderedDict()
						#**someDict[thisNodeId] = thisNode.item_
						#**parrentDict[parrentNodeId] = someDict
						thisDict = parrentDict[parrentNodeId]
						thisDict[thisNodeId] = someDict

						# Keep track of dict object
						myNode = someNode.addSubNode(thisNode.name_, thisDict)#someDict)

					# Keep track of prev node
					prevNode = thisNode

			# Get next node
			thisNode = thisNode.getNextNode(startNode_)


		# Get root dict node
		someRootNode = myNode.getRootNode()
		thisDict = OrderedDict()
		thisDict = someRootNode.item_

		return thisDict

	# Method to convert a infoTree directly to JSON Object Tree
	# Process: infoTree => OrderedDict Tree => JSON Tree
	def conv2JsonTree(self, startNode=""):
		jsonTree = ""

		# Convert infoTree 2 Dict Tree
		dictTree = self.conv2DictTree(startNode)

		# Convert Dict Tree 2 JSON Object Tree
		jsonTree = json.dumps(dictTree, indent=4)

		# Retun json object infoTree
		return jsonTree

   # Method used to convert a infoTree or subInfoTree to a Ordered Dictonary infoTree object so it can be converetd to JSON and stored in a noSQL data format 
	# NOTE!! behaves alot like a linked list where where each OrderedDict are linked together to form structure
	# for further Analysis
	# NOTE!! The OrderedDict Tree can be found in rootNode's item_ field, so in short Dict infoTree is just a infoTree node that contains a dict Tree
	# TESTED: OK
	# Process: infoTree => OrderedDict Tree
	def conv2DictInfoTree(self, startNode_ = ""):
		thisDict = OrderedDict()
		parrentDict = OrderedDict()
		someDict = OrderedDict()
		myNode = jsonNode(self.name_, self.item_) # The resulting node that contains orderedDict Tree
		searchNode = jsonNode(self.name_, self.item_) # Used to keep track of Dict object using a infoTree structure
		someRootNode = ""
		someNode = ""
		dictAdded = 0 # Flags that indicates wether a new dict node has been added

		# Start the recursive process by setting root-node
		thisNode = self
		prevNode = self
		while(1):

			if thisNode == "":
				print("infoTree Read complete...")
				break
			else:
				print("Node found: " + "key: " + thisNode.nodeId_ + " Name: " + thisNode.name_ + " value: " + thisNode.getValue())

				# Reset new dict node added flag
				dictAdded = 0

				# Is this first node "rootNode"?
				if thisNode == self:
					#YES Add first child node
					searchNode = searchNode.getRootNode()

					# Is this a leafNode?
					if thisNode.isLeafNode():
						#YES => Add field:value
						searchNode.item_ = thisNode.item_
						searchNode.name_ = thisNode.name_

					else: # NO => Add dict item
						# Create unique dict key
						thisNodeId = thisNode.name_ + "#" + thisNode.nodeId_
						
						someDict[thisNodeId] = OrderedDict() #thisNode.item_
					
						# Add Root Dict node
						myNode.item_ = someDict
						searchNode.item_ = someDict
					
					# Keep track of dictonary object
					#**myNode = myNode.addSubNode(thisNode.name_, someDict)

					# Keep track of prev node
					prevNode = thisNode

					dictAdded = 1

				# Is thisNode a peerNode?
				if (thisNode.parrentNode_ == prevNode.parrentNode_) & (thisNode != self):
					#YES =>
					# Find parrent Dict
					someRootNode = searchNode.getRootNode()
					someNode = someRootNode.getNodeById(thisNode.parrentNode_.nodeId_)
					parrentDict = someNode.item_

					# Create unique dict key
					thisNodeId = thisNode.name_ + "#" + thisNode.nodeId_
					parrentNodeId = thisNode.parrentNode_.name_ + "#" + thisNode.parrentNode_.nodeId_

					# Is this a leafNode?
					if thisNode.isLeafNode():
						#YES => Add field:value
						thisDict = parrentDict[parrentNodeId]
						thisDict[thisNode.name_] = thisNode.item_

						# Keep track of dictonary object
						searchNode = searchNode.addPeerNode(thisNode.name_, thisNode.item_)

					else: # NO => Add child dict item
						# Add child dict

						someDict = OrderedDict() # New dict
						#**someDict[thisNodeId] = thisNode.item_
						#**parrentDict[parrentNodeId] = someDict
						thisDict = parrentDict[parrentNodeId]
						thisDict[thisNodeId] = someDict

						# Keep track of dictonary object
						searchNode = searchNode.addPeerNode(thisNode.name_, thisDict) #someDict)

					# Keep track of prev node
					prevNode = thisNode

					dictAdded = 1

				# Is thisNode a childNode?
				if thisNode.parrentNode_ == prevNode:
					#YES => Add new child Dict
					# Find parrent dict
					someRootNode = searchNode.getRootNode()
					someNode = someRootNode.getNodeById(prevNode.nodeId_)
					parrentDict = someNode.item_

					# Create unique dict key
					thisNodeId = thisNode.name_ + "#" + thisNode.nodeId_
					parrentNodeId = thisNode.parrentNode_.name_ + "#" + thisNode.parrentNode_.nodeId_

					# Is this a leafNode?
					if thisNode.isLeafNode():
						#YES => Add field:value
						thisDict = parrentDict[parrentNodeId]
						thisDict[thisNode.name_] = thisNode.item_

						# Keep track of dictonary object
						searchNode = someNode.addSubNode(thisNode.name_, thisNode.item_)

					else: # NO => Add child dict item
						# Add Child dict						

						someDict = OrderedDict()
						#**someDict[thisNodeId] = thisNode.item_
						#**parrentDict[parrentNodeId] = someDict
						thisDict = parrentDict[parrentNodeId]
						thisDict[thisNodeId] = someDict
					
						# Keep track of dict object
						searchNode = someNode.addSubNode(thisNode.name_, thisDict)#someDict)

					# Keep track of prev node
					prevNode = thisNode

					dictAdded = 1

				# Is thisNode a parrentNode?
				if thisNode == prevNode.parrentNode_:
					# YES => find the parrent dict
					someRootNode = searchNode.getRootNode()
					someNode = someRootNode.getNodeById(thisNode.parrentNode_.nodeId_)
					parrentDict = someNode.item_

					# Create unique dict key
					thisNodeId = thisNode.name_ + "#" + thisNode.nodeId_
					prevNodeId = prevNode.name_ + "#" + prevNode.nodeId_
					parrentNodeId = thisNode.name_ + "#" + thisNode.nodeId_

					# Is this a leafNode?
					if thisNode.isLeafNode():
						#YES => Add field:value
						thisDict = parrentDict[parrentNodeId]
						thisDict[thisNode.name_] = thisNode.item_

						# Keep track of dictonary object
						searchNode = someNode.addSubNode(thisNode.name_, thisNode.item_)

					else: # NO => Add child dict item
						# Add child dict

						someDict = OrderedDict()
						#**someDict[prevNodeId] = prevNode.item_
						#**parrentDict[parrentNodeId] = someDict
						thisDict = parrentDict[parrentNodeId]
						thisDict[prevNodeId] = someDict

						# Keep track of dict object
						searchNode = someNode.addSubNode(thisNode.name_, thisDict)#someDict)

					# Keep track of prev node
					prevNode = thisNode

					dictAdded = 1

				# Is thisNode a new parrent node
				if (thisNode != prevNode.parrentNode_) & dictAdded == 0:
					# YES => Find its parrent node
					someRootNode = searchNode.getRootNode()
					someNode = someRootNode.getNodeById(thisNode.parrentNode_.nodeId_)
					parrentDict = someNode.item_

					# Create unique dict key
					thisNodeId = thisNode.name_ + "#" + thisNode.nodeId_
					parrentNodeId = thisNode.parrentNode_.name_ + "#" + thisNode.parrentNode_.nodeId_

					# Is this a leafNode?
					if thisNode.isLeafNode():
						#YES => Add field:value
						thisDict = parrentDict[parrentNodeId]
						thisDict[thisNode.name_] = thisNode.item_

						# Keep track of dictonary object
						searchNode = someNode.addSubNode(thisNode.name_, thisNode.item_)

					else: # NO => Add child dict item
						# Add child dict
						
						someDict = OrderedDict()
						#**someDict[thisNodeId] = thisNode.item_
						#**parrentDict[parrentNodeId] = someDict
						thisDict = parrentDict[parrentNodeId]
						thisDict[thisNodeId] = someDict

						# Keep track of dict object
						searchNode = someNode.addSubNode(thisNode.name_, thisDict)#someDict)

					# Keep track of prev node
					prevNode = thisNode

			# Get next node
			thisNode = thisNode.getNextNode(startNode_)


		# Get root dict node
		someRootNode = myNode.getRootNode()

		return someRootNode

	# Method used to convert a Dict Tree or sub Dict Tree to a Dict infoTree object so it can so that it can be analyzed at node level 
	# NOTE!! Requires a Ordered Dict Tree, such as the one created when converting JSON2XML using xmltodict
	# TESTED: OK
	# Process: Dict Tree => Dict infoTree, uses infoTree as trackingNode to Look through a Dict Tree using a semi-recursive technique 
	def convDictTree2DictInfoTree(self, dictTree):
		thisTrackingNode = jsonNode("root", dictTree) # Used to keep track of Dict object using a infoTree structure

		#----- Look through Dict Tree using a Tracking Node --------

		# Loop until all nodes has been read
		while(1):
			
			# Show node traversal
			# Is this a simpe key:value?
			if not thisTrackingNode.isOrderedDict():
				# YES
				thisItem = thisTrackingNode.item_
			else:
				#NO => convert Dict to string
				thisItem = thisTrackingNode.convDictTree2JsonTree()

			print("Node found: " + "Id: " + thisTrackingNode.nodeId_ + " Key: " + thisTrackingNode.name_ + " value: " + thisItem)
			
			# Does thisNode have subNodes (does i contain a orderedDict, key:OrderedDict pair)?
			if thisTrackingNode.isOrderedDict():
				#YES => assume its a link to a ordered dict 
				# get next childNode dict 
				for k, v in thisTrackingNode.item_.items():
					
					# Keep track of thisNode
					# Add new subNode of thisNode
					thisTrackingNode = thisTrackingNode.addSubNode(k, v)
					break
			else: # NO => leafNode (simple key:value pair)
				# Get nextNode
				# Loop until valid nextNode found or Tree traversed
				while(1):
					# Is this lastNode in sub-nodeTree?
										
					# Assume lastNode on this branch has been looked through since this is a leafNode
					# Find thisNodes parrents peerNode					 
					# Get parrentNode dict
					# Does thisNode have a parrentNode?
					if thisTrackingNode.parrentNode_ == "":
						#NO => Assume this is rootNode => nodeTree traversed
						# Forced exit nodeTree look through complete
						break


					# Find peerNode of thisParrentNode

					# Is this last childNode?
					# Loop until valid parrentNode found
					while(1):

						if len(thisTrackingNode.parrentNode_.item_) == thisTrackingNode.parrentNode_.lastSubNodeIx_: 
							#NO => Find thisNodes parrents peerNode
							#Does thisNode have a parrent "Is this rootNode"?
							if thisTrackingNode.parrentNode_ != "":
								#YES  
								thisTrackingNode = thisTrackingNode.parrentNode_

								#Does thisNode have a parrentNode?
								if thisTrackingNode.parrentNode_ == "":
									#NO => Assume rootNode => nodeTree has been traversed
									# Forced exit the nodeTree look through complete
									break								  
							else: #NO => Assume this is rootNode
								# Forced exit, nodeTree traversed
								break
						else: # YES => New valid parrentNode found
							break 

					# Was a valid parrentNode found?
					# Does thisNode have a parrentNode?
					if thisTrackingNode.parrentNode_ == "":
						#NO => Assume rootNode => nodeTree has been traversed
						# Forced exit the nodeTree look through complete
						break 

					# Find nextNode
					ix = 0
					for k, v in thisTrackingNode.parrentNode_.item_.items():
						# Is this next childNode?
						if ix == thisTrackingNode.nodeIx_ + 1:
							#YES => nextNode found

							# Keep track of thisNode
							# Add new subNode of thisNode
							thisTrackingNode = thisTrackingNode.parrentNode_.addSubNode(k, v)
							break
						
						# update item ix
						ix = ix + 1

					# Was a valid nextNode found?
					if thisTrackingNode != "":
						#YES
						# Forced exit a nextNode has been found
						break

				
					# Does thisNode have a parrentNode?
					if thisTrackingNode.parrentNode_ == "":
					 #NO => Assume rootNode => nodeTree has been traversed
					 # Forced exit the nodeTree look through complete
					 break

			# Does thisNode have a parrentNode?
			if thisTrackingNode.parrentNode_ == "":
				#NO => Assume rootNode => nodeTree has been traversed
				# Forced exit nodeTree look through complete
				print("infoTree Read complete...")
				break					 

			# Get nextNode

		# Return the dynamically constructed dict infoTree
		return thisTrackingNode


#------------------------
	# Method to convert a Orderd Dictonary infoTree directly to JSON Object Tree
	# NOTE!! RREQUIRES that info tree consistes of a structure of Ordered Dicts "Is a Dict infoTree"
	# Process: Dict infoTree => OrderedDict Tree => JSON Tree
	def convDictInfoTree2JsonTree(self, startNode=""):
		jsonTree = ""

		# Convert Dict infoTree 2 Dict Tree
		dictTree = self.convDictInfoTree2DictTree(startNode)

		# Convert Dict Tree 2 JSON Object Tree
		jsonTree = json.dumps(dictTree, indent=4)

		# Retun json object Tree
		return jsonTree

	# Method that converts a OrderedDict Tree to JSON Tree
	def convDictTree2JsonTree(self):
		jsonTree = ""

		# Does thisNode contain a dict Tree?
		if not isinstance(self.item_, OrderedDict):
			#NO => Forced exit, nothing to convert
			# Just return the unchanged item
			return self.item_

		dictTree = self.item_

		# Convert Dict Tree 2 JSON Object Tree
		jsonTree = json.dumps(dictTree, indent=4)

		# return json object Tree
		return jsonTree

	# Method used to convert a OrderedDict infoTree "infoTree of OrderedDict Objects" or subInfoTree to a Ordered Dictonary object Tree so it can be converetd to JSON and stored in a noSQL data format 
	# for further Analysis
	# NOTE!! REQUIRES that info tree consistes of a structure of Ordered Dicts "Dict infoTree"
	# TESTED: OK
	# Process: Dict infoTree => OrderedDict Tree
	def convDictInfoTree2DictTree(self, startNode_ = ""):
		thisDict = OrderedDict()
		parrentDict = OrderedDict()
		someDict = OrderedDict()
		myNode = jsonNode(self.name_, self.item_)
		someRootNode = ""
		someNode = ""
		dictAdded = 0 # Flags that indicates wether a new dict node has been added

		# Start the recursive process by setting root-node
		thisNode = self
		prevNode = self
		while(1):

			if thisNode == "":
				print("infoTree Read complete...")
				break
			else:
				print("Node found: " + "key: " + thisNode.nodeId_ + " Name: " + thisNode.name_ + " value: " + thisNode.getValue())

				# Reset new dict node added flag
				dictAdded = 0

				# Is this first node?
				if thisNode == self:
					#YES Add first child node
					myNode = myNode.getRootNode()
					
					someDict = thisNode.item_
					
					# Add Root Dict node
					myNode.item_ = someDict
					# Keep track of dictonary object
					#**myNode = myNode.addSubNode(thisNode.nodeId_, thisDict)

					# Keep track of prev node
					prevNode = thisNode

					dictAdded = 1


				# Is thisNode a peerNode?
				if (thisNode.parrentNode_ == prevNode.parrentNode_) & (thisNode != self):
					#YES =>
					# Find parrent Dict
					someRootNode = myNode.getRootNode()
					someNode = someRootNode.getNodeById(thisNode.parrentNode_.nodeId_)
					parrentDict = someNode.item_
					# Add child dict
					someDict = OrderedDict() # New dict
					someDict = thisNode.item_
					parrentDict[thisNode.name_] = someDict

					# Keep track of dictonary object
					myNode = myNode.addPeerNode(thisNode.nodeId_, someDict)

					# Keep track of prev node
					prevNode = thisNode

					dictAdded = 1

				# Is thisNode a childNode?
				if thisNode.parrentNode_ == prevNode:
					#YES => Add new child Dict
					# Find parrent dict
					someRootNode = myNode.getRootNode()
					someNode = someRootNode.getNodeById(prevNode.nodeId_)
					parrentDict = someNode.item_
					# Add Child dict
					someDict = OrderedDict()
					someDict = thisNode.item_
					parrentDict[thisNode.name_] = someDict
					
					# Keep track of dict object
					myNode = someNode.addSubNode(thisNode.nodeId_, someDict)

					# Keep track of prev node
					prevNode = thisNode

					dictAdded = 1

				# Is thisNode a parrentNode?
				if thisNode == prevNode.parrentNode_:
					# YES => find the parrent dict
					someRootNode = myNode.getRootNode()
					someNode = someRootNode.getNodeById(thisNode.parrentNode_.nodeId_)
					parrentDict = someNode.item_
					# Add child dict
					someDict = OrderedDict()
					someDict = prevNode.item_
					parrentDict[thisNode.name_] = someDict

					# Keep track of dict object
					myNode = someNode.addSubNode(thisNode.nodeId_, someDict)

					# Keep track of prev node
					prevNode = thisNode

					dictAdded = 1

				# Is thisNode a new parrent node
				if (thisNode != prevNode.parrentNode_) & dictAdded == 0:
					# YES => Find its parrent node
					someRootNode = myNode.getRootNode()
					someNode = someRootNode.getNodeById(thisNode.parrentNode_.nodeId_)
					parrentDict = someNode.item_
					# Add child dict
					someDict = OrderedDict()
					someDict = thisNode.item_
					parrentDict[thisNode.name_] = someDict

					# Keep track of dict object
					myNode = someNode.addSubNode(thisNode.nodeId_, someDict)

					# Keep track of prev node
					prevNode = thisNode

			# Get next node
			thisNode = thisNode.getNextNode(startNode_)


		# Get root dict node
		someRootNode = myNode.getRootNode()
		thisDict = OrderedDict()
		thisDict = someRootNode.item_

		return thisDict

	# Method that converts a JSON object Tree to a Dict Tree
	def convJsonTree2DictTree(self, jsonTree_):
		dictTree = ""

		# Convert JSON Tree 2 Dict Tree
		dictTree = json.loads(jsonTree_, object_pairs_hook=OrderedDict) #xmltodict.unparse(json.loads(jsonTree_), pretty=True)

		return dictTree

	# Method that Converts a JSON Tree to a Dict InfoTree
	# Process: JSON Tree => Dict Tree => Dict InfoTree
	def convJsonTree2DictInfoTree(self, jsonTree_):
		dictInfoTree = ""

		# Convert JSON Tree 2 Dict Tree
		dictTree = self.convJsonTree2DictTree(jsonTree_)

		# Convert Dict Tree 2 Dict infoTree
		dictInfoTree = self.convDictTree2DictInfoTree(dictTree)

		# Return the resulting Dict infoTree
		return dictInfoTree		   