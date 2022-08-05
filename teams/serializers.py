from rest_framework import serializers
from .models import Team

class TeamSerializer(serializers.ModelSerializer):
  members = serializers.StringRelatedField(many=True, read_only=True)
  
  class Meta:
    model = Team
    fields = ['name', 'slug', 'description', 'members']