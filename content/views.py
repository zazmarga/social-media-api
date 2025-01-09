from django.shortcuts import render
from rest_framework import viewsets

from content.models import Profile
from content.serializers import ProfileSerializer


class ProfileViewSet(viewsets.ModelViewSet):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
