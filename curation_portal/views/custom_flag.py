from rest_framework.exceptions import NotFound
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import SessionAuthentication
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from curation_portal.serializers import CustomFlagSerializer
from curation_portal.models import CustomFlag


class CustomFlagViewset(ModelViewSet):
    permission_classes = (IsAuthenticated,)
    queryset = CustomFlag.objects.all()
    serializer_class = CustomFlagSerializer
    authentication_classes = (SessionAuthentication,)
