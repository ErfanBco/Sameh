import json

from django.core import serializers
from django.http import JsonResponse
from django.shortcuts import redirect

from employee.models import Structure, Hierarchy

ActorsObjects = []


class ActorsObj:

    def __init__(self, user):
        self.id = user.id
        self.name = user.last_name
        # self.structure = structure
        # self.children = {}
        ActorsObjects.append(self)

    def getJSON(self):
        return '{ "id":  "' + str(self.id) + '", "label": "' + self.name + '"}'
        #return "{ id: \'" + str(self.id) + "\', label: \'" + self.name + "\'," + "},"






def getActorsOfStructure(request):
    if not request.user.is_authenticated and not request.is_ajax:
        return redirect('/login')
    if request.method == 'POST':
        struct = Structure.objects.get(id=request.POST['structureID'])
        actors = Hierarchy.objects.filter(structure=struct).exclude(userID2=request.user)
        JSON = ""
        isFirst = True
        for actor in actors:
            if not isFirst:
                JSON += ","
            else:
                isFirst = False
            JSON += ActorsObj(actor.userID2).getJSON()
        # JSON += "]"
        return JsonResponse({"json": JSON}, status=200)
    else:
        return JsonResponse({"error": "Bad Request NIGGA"}, status=400)


