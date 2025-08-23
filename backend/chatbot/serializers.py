from rest_framework import serializers
from .models import User
from .models import ChatMessage 
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        password = validated_data.pop('password')  # remove password from dict
        user = User(**validated_data)
        user.set_password(password)                # hash it properly
        user.save()
        return user



class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatMessage
        fields = '__all__'

from .models import ChatSuggestion

class ChatSuggestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatSuggestion
        fields = '__all__'
