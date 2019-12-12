from jsonTree import jsonNode
from collections import OrderedDict

def importjsonTest():
	# Cerate new jsonObject root node
	myJsonObject = jsonNode()
	myJsonObject.importFromFile(testImportFile) #OK

	print("importjsonTest done")

	# Run search Test(s)
	# Get node by item (OK)
	thisNode = myJsonObject.getNodeByItem("name", "Jupiter") #OK
	# get peerNode by item # (OK)
	thisDict = OrderedDict()
	thisDict["value"] = 69.911
	thisDict["unit"] = "km"
	thisNode = thisNode.getPeerNodeByItem("radius", thisDict) #OK
	# get subNode by item (OK)
	thisNode = thisNode.getSubNodeByItem("unit", "km") #OK

	# Run Modify Test(s)
	
	# Modify Value Test # (OK) " TESTED WITH A LEAF LEAFNODE"
	thisNode = myJsonObject.getNodeByValue("Jupiter") #OK
	thisNode.setValue("Jupiter Modified") #OK

	# modify Name "Key" 
	# # FIXED ISSUE: getDictItem method nees to be implemented with while loop since item iteration fails if keys are removed douring iteration >_<" (OK)
	thisNode = myJsonObject.getNodeByName("dateField")
	thisNode.setName("datoFelt") # (OK)

	# Add peerItem Test (OK)
	thisNode = myJsonObject.getNodeByValue("Earth") #OK
	thisNode = thisNode.insertPeerNodeByValue("Earth", "popluation", 5000000000) # OK
	thisNode = myJsonObject.getNodeByValue("Earth") # OK
	thisNode = thisNode.addPeerNode("SI UNIT", "NO")

	# Add subItem Test, try to add subNode to a simple leafNode (OK)
	thisNode.addSubNode("Male", 5000000000*0.24) #OK
	thisNode.addSubNode("Female", 5000000000*(1-0.24)) #OK

	# Add subItem Test, Add subNode to dict parrentNode
	thisNode = myJsonObject.getNodeByValue("Earth") #OK
	thisNode = thisNode.getNodeByName("radius")
	thisNode = thisNode.addSubNode("SI UNIT", "YES")

	# Add subItem Test, Add subNode to list parrentNode
	thisNode = myJsonObject.getNodeByValue("planets")
	thisNode = thisNode.addSubNode("UNKNOWN PLANET", "URANUS")	

	# Insert peerItem test
	thisNode = myJsonObject.getNodeByValue("Mars")
	thisNode.insertPeerNode("nickName", "Warface")

	# Insert subItem after subItem at ix 0
	myJsonObject.insertSubNodeByName("object0.0.0.0.0", 0, "fieldA0", "valueA0")

	# Move Item between parrentNodes
	newParrentNode = myJsonObject.getNodeByValue("object0.0.0")
	myJsonObject.moveNodeByName("object0.0.0.0.0", newParrentNode)

	# Move peerItem between parrentNodes
	thisNode = myJsonObject.getNodeByName("binaryField")
	thisNode.movePeerNodeByName("codeField", newParrentNode)

	# Move subItem between parrentNodes
	newParrentNode = myJsonObject.getNodeByName("object0")
	thisNode = myJsonObject.getNodeByName("object0.0.0.0")
	thisNode.moveSubNodeByName("filed0.0.0.0", newParrentNode)

	# Move peerItem between Items
	thisNode = myJsonObject.getNodeByName("codeField")
	otherNode = myJsonObject.getNodeByName("int32Field")
	thisNode.relocatePeerNodeByName("codeField", otherNode.nodeIx_)

	# Move subItem between subItems
	thisNode = myJsonObject.getNodeByName("object0.0.0.0.0")
	otherNode = myJsonObject.getNodeByName("filedC")
	thisNode.relocateSubNodeByName("fieldA", otherNode.nodeIx_)

	# Run exportJsonTest(s)
	# Try Expot the import
	exportjsonTest(myJsonObject)

	return

def exportjsonTest(jsonObject_):
	jsonObject_.exportToFile(testExportFile)
	print("exportjsonTest done")
	return


# Main code
testImportFile = "D:/pythonTools/Tree Structure Templates/jsonTree/planets.json"
testExportFile = "D:/pythonTools/Tree Structure Templates/jsonTree/planetsExport.json"

# Run importjsonTest(s)
importjsonTest()

