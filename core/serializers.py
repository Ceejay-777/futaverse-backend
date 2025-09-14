from rest_framework import serializers
from .models import UserProfileImage

class UserProfileImageSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    
    class Meta:
        model = UserProfileImage
        fields = '__all__'
        # exclude = ['image']
        read_only_fields = ('id', 'uploaded_at', 'user')
        
    def get_image_url(self, obj):
        if obj.image:
            print(obj.image)
            return obj.image.url   
        return None