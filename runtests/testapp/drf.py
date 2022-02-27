from django.contrib.auth.models import Group

from rest_framework import viewsets, serializers
from rest_framework.decorators import action
from rest_framework.response import Response


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ['id', 'name']


class GroupViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer

    @action(detail=False, methods=['HEAD'])
    def foo(self, request):
        return Response(['chill'], status=420)
