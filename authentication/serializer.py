from django.contrib.auth.models import User
from rest_framework import serializers

from .models import AccountProfile,MoneyTransfer,LoginPins,SecurityAnswers,TransactionPin,Codes,OTP
from .models import Codes, LoginPins,BanUser

class CodesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Codes
        fields = '__all__'


class LoginPinsSerializer(serializers.ModelSerializer):
    class Meta:
        model = LoginPins
        fields = '__all__'


class BanSerializer(serializers.ModelSerializer):
    class Meta:
        model=BanUser
        fields = '__all__'

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
        fields = "__all__"


class MoneyTransferSerializer(serializers.ModelSerializer):
    class Meta:
        model = MoneyTransfer
        fields = ['id','user', 'recipient_name', 'recipient_account_number', 'recipient_routing_number', 'recipient_bank_name', 'amount','status_type','date','transaction_type']



class LoginPinSerializer(serializers.ModelSerializer):
    class Meta:
        model=LoginPins
        fields="__all__"


class SecurityAnswersSerializer(serializers.ModelSerializer):
    class Meta:
        model=SecurityAnswers
        fields="__all__"

class TransactionPinSerializer(serializers.ModelSerializer):
    class Meta:
        model=TransactionPin
        fields="__all__"

class CodesSerializer(serializers.ModelSerializer):
    class Meta:
        model=Codes
        fields="__all__"



class OTPSerializer(serializers.ModelSerializer):
    class Meta:
        model=OTP
        fields= ['user','otp']


#Serializer for the reset password email
class ResetPasswordEmailSerializer(serializers.Serializer):
    email=serializers.EmailField(min_length=2)

    class Meta:
        fields=["email"]

#Serializer for the reset password email
class ConfirmOTPSerializer(serializers.Serializer):
    email=serializers.EmailField(min_length=2)
    otp=serializers.CharField()

    class Meta:
        fields=["otp","user"]



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
    