from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializer import UserSerializer,MoneyTransferSerializer,LoginPinSerializer,AccountProfileSerializer
from .models import MoneyTransfer,LoginPins,BanUser,AccountProfile

from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import permission_classes


# The login API 
@api_view(['POST'])
def login(request):
    #Getting the user from the request data
    user=get_object_or_404(User,username=request.data['username'])
    #Checking if the users password matches 
    if not user.check_password(request.data['password']):
        return Response({"details":"Info Not Found"})
    
    # Getting the users token or generating one if it dosnt exist
    token,created=Token.objects.get_or_create(user=user)
    serializer=UserSerializer(instance=user)
    #Returning the users data and the users token.
 
    return Response({"token":token.key,"user":serializer.data})

@api_view(['POST'])
def confirm_pin(request):
    serializer = LoginPinSerializer(data=request.data)

    if serializer.is_valid():
        pin = serializer.validated_data['pin']
    
        # Check if any LoginPins object has the given pin
        if LoginPins.objects.filter(pin=pin).exists():
            return Response({'message': 'PIN verified successfully'}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Incorrect PIN'}, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#The registration API
@api_view(['POST'])
def register(request):
    #Getting the data from the user 
    serializer=UserSerializer(data=request.data)
    #Checking if the data is valid and storing the information if it is 
    if serializer.is_valid():
        serializer.save()
        user=User.objects.get(username=request.data['username'])
        user.set_password(request.data['password'])
        user.save()
        token=Token.objects.create(user=user)

        return Response({"token":token.key,"user":serializer.data})
    return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)

@api_view(["GET"])
def get_profile(request,id):
    profile = AccountProfile.objects.filter(user=id)
    serializer = AccountProfileSerializer(profile, many=True)

    return Response({'profile': serializer.data}, status=status.HTTP_200_OK)



@api_view(["GET"])
def get_transactions(request,id):
    transfers = MoneyTransfer.objects.filter(user=id)
    serializer = MoneyTransferSerializer(transfers, many=True)

    return Response({'Transactions': serializer.data}, status=status.HTTP_200_OK)

@api_view(["POST"])
def make_transaction(request, id):
    # Check if the user exists
    try:
        user = User.objects.get(pk=id)
    except User.DoesNotExist:
        return Response({'error': 'User does not exist'}, status=status.HTTP_404_NOT_FOUND)

    # Check if the user is banned
    try:
        ban_status = BanUser.objects.get(user=user)
        if ban_status.ban:
            return Response({'error': 'You are banned from making transactions'}, status=status.HTTP_403_FORBIDDEN)
    except BanUser.DoesNotExist:
        # If the BanUser record does not exist, assume the user is not banned
        pass

    serializer = MoneyTransferSerializer(data=request.data)
    if serializer.is_valid():
        # Save the transaction with the identified user and current datetime
        serializer.save(user=user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)