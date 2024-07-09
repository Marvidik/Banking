from django.contrib.auth.models import User
from rest_framework import serializers

from .models import AccountProfile,MoneyTransfer,LoginPins



#  user serializer
class UserSerializer(serializers.ModelSerializer):
    referral_name = serializers.CharField(required=False, allow_blank=True)
    class Meta(object):
        model = User
        fields = ( 'id','username', 'email', 'password', 'referral_name')


#Serializer for the password reset confirm
class PasswordResetConfirmSerializer(serializers.Serializer):
    email=serializers.EmailField(min_length=2)
    password = serializers.CharField(max_length=128)
    confirm_password = serializers.CharField(max_length=128)

    def validate(self, data):
        password = data.get('password')
        confirm_password = data.get('confirm_password')

        # Check if passwords match
        if password != confirm_password:
            raise serializers.ValidationError("Passwords do not match")

        return data


class AccountProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccountProfile
        fields = [
            'first_name', 'last_name', 'date_of_birth', 'ssn', 'email',
            'phone_number', 'street_address', 'city', 'state', 'zip_code',
            'account_type', 'balance','account_number'
        ]

class MoneyTransferSerializer(serializers.ModelSerializer):
    class Meta:
        model = MoneyTransfer
        fields = ['user', 'recipient_name', 'recipient_account_number', 'recipient_routing_number', 'recipient_bank_name', 'amount','status_type','date']



class LoginPinSerializer(serializers.ModelSerializer):
    class Meta:
        model=LoginPins
        fields="__all__"