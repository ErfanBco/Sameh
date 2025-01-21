from django.http import JsonResponse
from django.shortcuts import redirect

from employee.models import Structure, Hierarchy, Contract


class ContractObj:

    def __init__(self, contract):
        self.id = contract.id
        self.name = contract.name
        # self.structure = structure
        # self.children = {}
        #ActorsObjects.append(self)

    def getJSON(self):
        return '{ "id":  "' + str(self.id) + '", "label": "' + self.name + '"}'




def getContractsOfStructure(request):
    #if not request.user.is_authenticated and not request.is_ajax:
    #    return redirect('/login')
    if request.method == 'GET':
        struct = Structure.objects.get(id=request.GET['structureID'])
        contracts = Contract.objects.filter(employeesStructure=struct).exclude(userID2=request.user)
        JSON = ""
        isFirst = True
        for contract in contracts:
            if not isFirst:
                JSON += ","
            else:
                isFirst = False
            JSON += ContractObj(contract).getJSON()
        # JSON += "]"
        return JsonResponse({"json": JSON}, status=200)
    else:
        return JsonResponse({"error": "Bad Request NIGGA"}, status=400)