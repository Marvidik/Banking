from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializer import UserSerializer,MoneyTransferSerializer,LoginPinSerializer,AccountProfileSerializer,SecurityAnswersSerializer,TransactionPinSerializer,CodesSerializer
from .models import MoneyTransfer,LoginPins,BanUser,AccountProfile,SecurityAnswers,TransactionPin,Codes

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
        return Response({"details":"Wrong Password"},status=status.HTTP_401_UNAUTHORIZED)
    
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

@api_view(["POST"])
def create_profile(request):
    serializer = AccountProfileSerializer(data=request.data)
    if serializer.is_valid():
        # Save the transaction with the identified user and current datetime
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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


@api_view(["POST"])
def create_security_answers(request):
    serializer = SecurityAnswersSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST", "GET"])
def check_security_answer(request, id):
    try:
        answers = SecurityAnswers.objects.get(user_id=id)
    except SecurityAnswers.DoesNotExist:
        return Response({"error": "Security answers for the user do not exist"}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'POST':
        serializer = SecurityAnswersSerializer(data=request.data)
        if serializer.is_valid():
            answer = serializer.validated_data.get('ans1')
            answer2 = serializer.validated_data.get('ans2')
            if answers.ans1 == answer or answers.ans2 == answer2:
                return Response({"status": "success", "message": "Answer is correct"}, status=status.HTTP_200_OK)
            else:
                return Response({"status": "failure", "message": f"Answer is incorrect {answers.ans1}{answers.ans2} {answer}"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'GET':
        serializer = SecurityAnswersSerializer(answers)
        return Response(serializer.data, status=status.HTTP_200_OK)
    

@api_view(["POST"])
def create_transaction_pin(request):
    serializer = TransactionPinSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST", "GET"])
def check_transaction_pin(request, id):
    try:
        answers = TransactionPin.objects.get(user_id=id)
    except TransactionPin.DoesNotExist:
        return Response({"error": "Security answers for the user do not exist"}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'POST':
        serializer = TransactionPinSerializer(data=request.data)
        if serializer.is_valid():
            answer = serializer.validated_data.get('transfer_pin')
            if answers.transfer_pin == answer :
                return Response({"status": "success", "message": "Pin is correct"}, status=status.HTTP_200_OK)
            else:
                return Response({"status": "failure", "message": f"Pin is incorrect {answers.ans1}{answers.ans2} {answer}"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'GET':
        serializer = TransactionPinSerializer(answers)
        return Response(serializer.data, status=status.HTTP_200_OK)
    

@api_view(["POST"])
def check_imf_code(request):
    serializer = CodesSerializer(data=request.data)
    if serializer.is_valid():
        imfcode = serializer.validated_data.get('imfcode')
        try:
            Codes.objects.get(imfcode=imfcode)
            return Response({"status": "success", "message": "IMF code is correct"}, status=status.HTTP_200_OK)
        except Codes.DoesNotExist:
            return Response({"status": "failure", "message": "IMF code is incorrect"}, status=status.HTTP_400_BAD_REQUEST)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(["POST"])
def check_ipn_code(request):
    serializer = CodesSerializer(data=request.data)
    if serializer.is_valid():
        ipncode = serializer.validated_data.get('ipncode')
        try:
            Codes.objects.get(ipncode=ipncode)
            return Response({"status": "success", "message": "IPN code is correct"}, status=status.HTTP_200_OK)
        except Codes.DoesNotExist:
            return Response({"status": "failure", "message": "IPN code is incorrect"}, status=status.HTTP_400_BAD_REQUEST)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(["POST"])
def check_bank_transfer_code(request):
    serializer = CodesSerializer(data=request.data)
    if serializer.is_valid():
        bank_transfercode = serializer.validated_data.get('bank_transfercode')
        try:
            Codes.objects.get(bank_transfercode=bank_transfercode)
            return Response({"status": "success", "message": "Bank Transfer code is correct"}, status=status.HTTP_200_OK)
        except Codes.DoesNotExist:
            return Response({"status": "failure", "message": "Bank Transfer code is incorrect"}, status=status.HTTP_400_BAD_REQUEST)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
