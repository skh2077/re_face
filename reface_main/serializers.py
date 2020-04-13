from reface_main.models import *

class UserSerializer(AccountSerializer):
    class Meta:
        model = User
        fields = '__all__'