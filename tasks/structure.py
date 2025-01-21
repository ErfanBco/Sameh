from django.contrib.auth.models import User
from employee.models import Hierarchy, Contract, Structure

StructureObjects = []


class StructureObj:

    def __init__(self, structure):
        self.id = structure.id
        self.name = structure.name
        self.structure = structure
        self.children = {}
        StructureObjects.append(self)

    def AddChild(self, structureObj):
        self.children[structureObj.name] = structureObj

    def getJSON(self, isDefaultExpanded):
        print("j" + str(self.id))
        Json = "{ id: '" + str(self.id) + "\', label: \'" + self.name + "\'," + "isDefaultExpanded: " + isDefaultExpanded + ","
        if self.children:
            Json += " children: ["
            for key, val in self.children.items():
                Json += val.getJSON('false')
            Json += "],"
        Json += "},"
        return Json


def getAvailableStructures(UserID):
    hierarchy = Hierarchy.objects.get(userID=UserID)
    if not hierarchy.canDefineTasks:
        return None

    global StructureObjects
    StructureObjects = []
    createStructuresObjects(StructureObj(hierarchy.structure))

    return StructureObjects[0].getJSON('true')


def createStructuresObjects(structObj):
    query = Structure.objects.filter(upLine=structObj.structure)
    for q in query:
        newObj = StructureObj(q)
        structObj.AddChild(newObj)
        createStructuresObjects(newObj)


#####################################################################

def getEmployees(UserID, contract=None):
    # ToDo What Does No Contact Mean?
    options = []
    if contract is not None:
        Employees = Hierarchy.objects.filter(structure=contract.employeesStructure).exclude(userID=UserID)
    else:
        Employees = Hierarchy.objects.filter(structure=Hierarchy.objects.get(userID=UserID).structure).exclude(
            userID=UserID)

    i = 0
    while i < len(Employees):
        options.append((i, User.objects.get(id=Employees[i].userID).last_name))
        i += 1
    return options


def getContracts(UserID):
    hierarchy = Hierarchy.objects.get(userID=UserID)
    if not hierarchy.canDefineTasks:
        return None

    contracts = Contract.objects.filter(isValid=True, employerStructure=hierarchy.structure)
    # str = ""
    # for cont in contracts:
    #    str += cont.name + "\n"
    return contracts
