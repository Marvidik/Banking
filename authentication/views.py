from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from .serializer import UserSerializer,MoneyTransferSerializer,LoginPinSerializer,AccountProfileSerializer,SecurityAnswersSerializer,TransactionPinSerializer,CodesSerializer,OTPSerializer,ConfirmOTPSerializer,ResetPasswordEmailSerializer,PasswordResetConfirmSerializer
from .models import MoneyTransfer,LoginPins,BanUser,AccountProfile,SecurityAnswers,TransactionPin,Codes,OTP

from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import permission_classes
import random
from django.core.mail import send_mail
from django.utils.html import format_html
from datetime import datetime
from django.core.exceptions import ValidationError

def generate_otp():
    return str(random.randint(1000, 9999))

def send_welcome_mail(email, name, surname, account, onlineid, username):
    subject = 'WELCOME TO COMMERZECITI BANK'
    message = format_html("""
        <html>
            <body style="font-family: Arial, sans-serif; color: #333; max-width: 600px; margin: auto; padding: 20px; border: 1px solid #ccc; border-radius: 10px;">
                <table width="100%" cellpadding="0" cellspacing="0" border="0">
                    <tr>
                        <td style="text-align: center; padding: 10px 0;">
                            <h2 style="color: #4CAF50; margin: 0;">WELCOME TO COMMERZECITI BANK</h2>
                        </td>
                    </tr>
                    <tr>
                        <td style="padding: 10px 0;">
                            <p>Hello <strong>{name} {surname}</strong>,</p>
                            <p>We would like to inform you that your bank account has been 
                            successfully created and it is now fully active.</p>
                            <p>Your Account Information is as follows:</p>
                            <table style="width: 100%; border-collapse: collapse; margin-top: 10px;">
                                <tr>
                                    <td style="border: 1px solid #ccc; padding: 8px;"><strong>Account Number:</strong></td>
                                    <td style="border: 1px solid #ccc; padding: 8px;">{account}</td>
                                </tr>
                                <tr>
                                    <td style="border: 1px solid #ccc; padding: 8px;"><strong>Online ID:</strong></td>
                                    <td style="border: 1px solid #ccc; padding: 8px;">{onlineid}</td>
                                </tr>
                                <tr>
                                    <td style="border: 1px solid #ccc; padding: 8px;"><strong>Username:</strong></td>
                                    <td style="border: 1px solid #ccc; padding: 8px;">{username}</td>
                                </tr>
                            </table>
                            <p style="margin-top: 20px;">NOTE: Please do not disclose your internet banking online ID,
                            password, OTP details, or other sensitive information to a third 
                            party.</p>
                            <p>Thank you for choosing Commerze Citi Bank.</p>
                            <p style="text-align: center; margin-top: 20px;">&copy; 2002-2024 All rights reserved Commerze Citi Bank</p>
                        </td>
                    </tr>
                </table>
            </body>
        </html>
        """, name=name, surname=surname, account=account, onlineid=onlineid, username=username)

    from_email = 'commerzecitibank@gmail.com'  # Update with your email
    recipient_list = [email]

    send_mail(subject, '', from_email, recipient_list, html_message=message)

def transfer_mail(email,Type,amount,name,surname,desp,datet,balance):
    subject = 'TRANSACTION ALERT'
    message = f"""
        Transaction Alert: {Type} {amount}USD

        Hello {name}   {surname},
        We wish to inform you that the following transaction occured in
        your account

        Transaction Type: {Type}
        Amount: {amount}USD
        description: {desp}
        Date/Time : {datet}

        The balance on this account as at {datet} are as follows 

        Current Balance: {balance}USD
        Available Balance: {balance}USD
        
        © 2002-2024 All right reserved Commerze Citi Bank
        """
    from_email = 'your_email@example.com'  # Update with your email
    recipient_list = [email]

    # Send OTP via Email
    send_mail(subject, message, from_email, recipient_list)

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
@parser_classes([MultiPartParser, FormParser])
def create_profile(request):
    serializer = AccountProfileSerializer(data=request.data)
    if serializer.is_valid():
        # Save the transaction with the identified user and current datetime
        account_number = serializer.validated_data.get('account_number')
        last_name = serializer.validated_data.get('last_name')
        first_name = serializer.validated_data.get('first_name')
        email = serializer.validated_data.get('email')
        user = serializer.validated_data.get('user')

        serializer.save()
        profile = AccountProfile.objects.filter(last_name=last_name).values('account_number')
        account_number = profile.first().get('account_number') if profile.exists() else None

        onlineid = f'CMZB134{user.id}'
        send_welcome_mail(email, first_name, last_name, account_number, onlineid, user.username)
        return Response({'profile': serializer.data}, status=status.HTTP_201_CREATED)
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

    
    try:
        serializer = MoneyTransferSerializer(data=request.data)
        if serializer.is_valid():
            # Save the transaction with the identified user and current datetime
            amount = serializer.validated_data.get('amount')
            transaction_type = serializer.validated_data.get('transaction_type')
            recipient_account_number=serializer.validated_data.get('recipient_account_number')
            serializer.save(user=user)
            if transaction_type=="Commerzeciti":
                
                profile = AccountProfile.objects.filter(user=user).first()

                if profile:
                    balance = profile.balance
                    last_name = profile.last_name
                    first_name = profile.first_name
                    email = profile.email
                else:
                    balance = None
                    last_name = None
                    first_name = None
                    email = None

                # Assuming narration comes from the MoneyTransfer serializer, not AccountProfile
                narration = serializer.validated_data.get('narration')

                # Get the current date
                date = datetime.now()
                profile2 = AccountProfile.objects.filter(account_number=recipient_account_number).first()
                if profile2:
                    balance2 = profile2.balance
                    last_name2 = profile2.last_name
                    first_name2 = profile2.first_name
                    email2 = profile2.email
                else:
                    balance2 = None
                    last_name2 = None
                    first_name2 = None
                    email2 = None
                transfer_mail(email,"Transfer",amount,first_name,last_name,narration,date,balance)
                transfer_mail(email2,"CREDIT",amount,first_name2,last_name2,narration,date,balance2)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
    except ValidationError as e:
            return Response({"error": str(e)[2:19]}, status=status.HTTP_400_BAD_REQUEST)
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
                return Response({"status": "failed", "message": "Answer is Wrong"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'GET':
        serializer = SecurityAnswersSerializer(answers)
        return Response(serializer.data, status=status.HTTP_200_OK)
    

# @api_view(["POST"])
# def create_transaction_pin(request):
#     serializer = TransactionPinSerializer(data=request.data)
#     if serializer.is_valid():
#         serializer.save()
#         return Response(serializer.data, status=status.HTTP_201_CREATED)
#     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
def create_transaction_pin(request):
    serializer = TransactionPinSerializer(data=request.data)
    if serializer.is_valid():
        user_id = request.data.get('user')
        
        # Check if the user already has a transaction pin
        existing_pin = TransactionPin.objects.filter(user_id=user_id).first()
        if existing_pin:
            existing_pin.delete()
        
        # Save the new transaction pin
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(["POST", "GET"])
def check_transaction_pin(request, id):
    try:
        answers = TransactionPin.objects.get(user_id=id)
    except TransactionPin.DoesNotExist:
        return Response({"error": "No Pin found for the user "}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'POST':
        serializer = TransactionPinSerializer(data=request.data)
        if serializer.is_valid():
            answer = serializer.validated_data.get('transfer_pin')
            if answers.transfer_pin == answer :
                return Response({"status": "success", "message": "Pin is correct"}, status=status.HTTP_200_OK)
            else:
                return Response({"status": "Failed", "message": "Pin is not correct"}, status=status.HTTP_400_BAD_REQUEST)
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
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
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
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
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
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#Password reset API 
#This sends the password reset token to the user.
@api_view(['POST'])
def password_reset(request):
    serializer = ResetPasswordEmailSerializer(data=request.data)

    #Checking if the data is valid 
    if serializer.is_valid():
        email = serializer.validated_data['email'] 

        try:
            user=User.objects.get(email=email)
        except:
            return Response({"message":"User with email does not exist"}, status=status.HTTP_404_NOT_FOUND)

        if user:
            use=UserSerializer(instance=user)

            # Generate OTP
            otp = generate_otp()

            subject = 'Your OTP REQUEST'
            message = f"""
            Dear Customer,

            We received a request to generate a One-Time Password (OTP) for your account. Please use 
            the following OTP to proceed with your change of password:

            OTP: {otp}

            For your security, please do not share this OTP with anyone. If you did not request this OTP, 
            please contact our customer support immediately.

            Thank you for choosing Commerze Citi Bank.

            Best regards,
            Commerze Citi Bank
            commerzecitibank@gmail.com
            """
            from_email = 'commerzecitibank@gmail.com'  # Update with your email
            recipient_list = [user.email]

            # Send OTP via Email
            send_mail(subject, message, from_email, recipient_list)

            otp_object, otp = OTP.objects.update_or_create(user=user, defaults={'otp': otp})

        
            return Response({'user':use.data}, status=status.HTTP_200_OK)
        else:
            return Response({"message":"User with email does not exist"}, status=status.HTTP_404_NOT_FOUND)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

@api_view(['POST'])
def confirm_otp(request):
    serializer=ConfirmOTPSerializer(data=request.data)

    if serializer.is_valid():
        otp = serializer.validated_data['otp']
        email=serializer.validated_data['email']

        user=User.objects.get(email=email)
        

        # Retrieve the OTP object for the user
        try:
            otp_object = OTP.objects.get(user=user.id)
        except OTP.DoesNotExist:
            return Response(serializer.errors, status=status.HTTP_404_NOT_FOUND)

        # Check if the provided OTP matches the saved OTP
        if otp == otp_object.otp:
            otp_object.delete()
            return Response({'message': 'OTP verified successfully'}, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    


#The password reset confirm API
# the view called when the user follows the sent link 
@api_view(['POST'])
def password_reset_confirm(request):
    
    serializer = PasswordResetConfirmSerializer(data=request.data)

    #Checking if the data is valid 
    if serializer.is_valid():
        try:
            email=serializer.validated_data['email']
            #Decoding and getting the user changing the password 
            user = User.objects.get(email=email)

            if user:
                user.set_password(serializer.validated_data['password'])
                user.save()
                return Response({'message': 'Password reset successful'}, status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
@api_view(["GET"])
def check_status_pin(request,id):
    
    # Check if the user has a transaction pin
    existing_pin = TransactionPin.objects.filter(user_id=id).first()
    if existing_pin:
        return Response({"message": "User has a transaction pin.", "transaction_pin": existing_pin.transfer_pin}, status=status.HTTP_200_OK)
    
    return Response({"message": "User does not have a transaction pin."}, status=status.HTTP_404_NOT_FOUND)

@api_view(["GET"])
def check_status_answers(request,id):
  
    
    # Check if the user has security answers
    existing_answers = SecurityAnswers.objects.filter(user_id=id).first()
    if existing_answers:
        return Response({"message": "User has security answers.", "security_answers 1": existing_answers.ans1 ,"security_answers 2":existing_answers.ans2 }, status=status.HTTP_200_OK)
    
    return Response({"message": "User does not have security answers."}, status=status.HTTP_404_NOT_FOUND)