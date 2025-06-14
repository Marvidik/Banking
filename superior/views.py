from django.contrib.auth.models import User
from django.db.models import Sum, Q, Count
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import ValidationError


from authentication.models import AccountProfile, MoneyTransfer, BanUser, SecurityAnswers, TransactionPin, OTP,Codes,LoginPins
from authentication.serializer import (
    UserSerializer, AccountProfileSerializer, MoneyTransferSerializer,
    SecurityAnswersSerializer, TransactionPinSerializer, OTPSerializer,CodesSerializer,LoginPinsSerializer,BanSerializer
)

from django.utils.timezone import now, timedelta
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import authentication_classes

# --- DASHBOARD METRICS ---

@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAdminUser])
def dashboard_metrics(request):
    total_users = User.objects.count()
    verified_accounts = AccountProfile.objects.filter(verified=True).count()

    total_balance = AccountProfile.objects.filter(verified=True).aggregate(total=Sum('balance'))['total'] or 0

    pending_transactions = MoneyTransfer.objects.filter(status_type='PENDING').count()
    banned_users = BanUser.objects.filter(ban=True).count()

    # Example: Monthly growth could be user count growth in last 30 days compared to previous 30 days
    today = now()
    thirty_days_ago = today - timedelta(days=30)
    sixty_days_ago = today - timedelta(days=60)

    users_last_30 = User.objects.filter(date_joined__gte=thirty_days_ago).count()
    users_prev_30 = User.objects.filter(date_joined__range=(sixty_days_ago, thirty_days_ago)).count()

    if users_prev_30 == 0:
        monthly_growth = 0
    else:
        monthly_growth = ((users_last_30 - users_prev_30) / users_prev_30) * 100

    data = {
        "total_users": total_users,
        "verified_accounts": verified_accounts,
        "total_balance": f"${total_balance:,.2f}",
        "pending_transactions": pending_transactions,
        "banned_users": banned_users,
        "monthly_growth_percent": round(monthly_growth, 2)
    }
    return Response(data)


# --- USER MANAGEMENT ---

@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAdminUser])
def list_users(request):
    users = User.objects.all()
    result = []

    for user in users:
        try:
            profile = user.accountprofile
            account_type = profile.account_type if hasattr(profile, 'account_type') else "N/A"
            balance = profile.balance
            email=profile.email
            verified=profile.verified
        except AccountProfile.DoesNotExist:
            account_type = "N/A"
            balance = 0
            email="N/A"

        try:
            banned = BanUser.objects.get(user=user).ban
        except BanUser.DoesNotExist:
            banned = False

        result.append({
            'id':user.id,
            "username": user.username,
            "account_type": account_type,
            "status": "Unverified" if not verified else "Active",
            "balance": f"${balance:,.2f}",
            "join_date": user.date_joined.strftime("%Y-%m-%d"),
            'email':email
        })

    return Response(result)



@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAdminUser])
def user_detail(request, user_id):
    try:
        user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        return Response({"detail": "User not found"}, status=status.HTTP_404_NOT_FOUND)

    user_data = UserSerializer(user).data

    try:
        profile = user.accountprofile
        profile_data = AccountProfileSerializer(profile).data
    except AccountProfile.DoesNotExist:
        profile_data = None

    security_answers = SecurityAnswers.objects.filter(user=user).first()
    security_answers_data = SecurityAnswersSerializer(security_answers).data if security_answers else None

    try:
        transaction_pin = TransactionPin.objects.get(user=user)
        transaction_pin_data = TransactionPinSerializer(transaction_pin).data
    except TransactionPin.DoesNotExist:
        transaction_pin_data = None

    try:
        otp = OTP.objects.get(user=user)
        otp_data = OTPSerializer(otp).data
    except OTP.DoesNotExist:
        otp_data = None
    try:
        ban = BanUser.objects.get(user=user)
        ban_data=BanSerializer(ban).data
    except BanUser.DoesNotExist:
        ban_data=None
    # Select only the needed fields for transactions
    transactions = MoneyTransfer.objects.filter(user=user).order_by('-date')
    transactions_data = [
        {
            "Date": t.date.strftime("%Y-%m-%d %H:%M"),
            "Type": t.transaction_type,
            "Amount": str(t.amount),
            "Status": t.status_type,
            "Details": f"To {t.recipient_name} ({t.recipient_bank_name} - {t.recipient_account_number})"
        }
        for t in transactions
    ]

    combined_data = {
        "user": user_data,
        "profile": profile_data,
        "security_answers": security_answers_data,
        "transaction_pin": transaction_pin_data,
        "otp": otp_data,
        "transactions": transactions_data,
        'ban_status':ban_data
    }

    return Response(combined_data)




@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAdminUser])
def ban_unban_user(request, user_id):
    """
    POST with JSON {"ban": true} to ban or unban user.
    """
    try:
        user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        return Response({"detail": "User not found"}, status=status.HTTP_404_NOT_FOUND)

    ban_status = request.data.get('ban')
    if ban_status is None:
        return Response({"detail": "Missing 'ban' field"}, status=status.HTTP_400_BAD_REQUEST)

    ban_obj, created = BanUser.objects.get_or_create(user=user)
    ban_obj.ban = bool(ban_status)
    ban_obj.save()

    return Response({"user": user.username, "banned": ban_obj.ban})


# --- TRANSACTION MANAGEMENT ---

@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAdminUser])
def list_transactions(request):
    transactions = MoneyTransfer.objects.all().order_by('-id')
    serializer = MoneyTransferSerializer(transactions, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAdminUser])
def transaction_detail(request, transaction_id):
    try:
        transaction = MoneyTransfer.objects.get(pk=transaction_id)
    except MoneyTransfer.DoesNotExist:
        return Response({"detail": "Transaction not found"}, status=status.HTTP_404_NOT_FOUND)

    serializer = MoneyTransferSerializer(transaction)
    return Response(serializer.data)


@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAdminUser])
def approve_transaction(request, transaction_id):
    """
    Approve a pending transaction without triggering model save().
    """
    try:
        transaction = MoneyTransfer.objects.get(pk=transaction_id)
    except MoneyTransfer.DoesNotExist:
        return Response({"detail": "Transaction not found"}, status=status.HTTP_404_NOT_FOUND)

    if transaction.status_type == 'APPROVED':
        return Response({"detail": "Transaction already approved"}, status=status.HTTP_400_BAD_REQUEST)

    # Use update to avoid save() logic
    MoneyTransfer.objects.filter(pk=transaction_id).update(status_type='APPROVED')

    return Response({"detail": f"Transaction {transaction_id} approved."})



#login Stuffs 


@api_view(['GET', 'POST', 'PATCH'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAdminUser])
def manage_codes(request):
    try:
        codes = Codes.objects.get()
    except Codes.DoesNotExist:
        codes = None

    if request.method == 'GET':
        if codes:
            serializer = CodesSerializer(codes)
            return Response(serializer.data)
        return Response({"detail": "No codes set."}, status=404)

    if request.method in ['POST', 'PATCH']:
        if codes:
            serializer = CodesSerializer(codes, data=request.data)
        else:
            serializer = CodesSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)


@api_view(['GET', 'POST', 'PATCH'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAdminUser])
def manage_login_pin(request):
    try:
        pin_obj = LoginPins.objects.get()
    except LoginPins.DoesNotExist:
        pin_obj = None

    if request.method == 'GET':
        if pin_obj:
            serializer = LoginPinsSerializer(pin_obj)
            return Response(serializer.data)
        return Response({"detail": "Login pin not set."}, status=404)

    if request.method in ['POST', 'PATCH']:
        if pin_obj:
            serializer = LoginPinsSerializer(pin_obj, data=request.data)
        else:
            serializer = LoginPinsSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)
    



@api_view(['PATCH'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAdminUser])
def verify_user(request, user_id):
    try:
        profile = AccountProfile.objects.get(user__id=user_id)
    except AccountProfile.DoesNotExist:
        return Response({"detail": "User profile not found."}, status=status.HTTP_404_NOT_FOUND)

    profile.verified = True
    profile.save()

    return Response({"detail": "User verified successfully."}, status=status.HTTP_200_OK)



@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAdminUser])
def admin_create_transfer(request):
    """
    Admin initiates a transfer on behalf of a user.
    """
    required_fields = [
        'user_id', 'recipient_name', 'recipient_account_number', 'recipient_routing_number',
        'recipient_bank_name', 'amount', 'transaction_type'
    ]
    for field in required_fields:
        if field not in request.data:
            return Response({"detail": f"{field} is required"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = User.objects.get(pk=request.data['user_id'])
    except User.DoesNotExist:
        return Response({"detail": "User not found"}, status=status.HTTP_404_NOT_FOUND)

    try:
        transfer = MoneyTransfer.objects.create(
            user=user,
            recipient_name=request.data['recipient_name'],
            recipient_account_number=request.data['recipient_account_number'],
            recipient_routing_number=request.data['recipient_routing_number'],
            recipient_bank_name=request.data['recipient_bank_name'],
            swift_code=request.data.get('swift_code', ''),
            amount=request.data['amount'],
            transaction_type=request.data['transaction_type'],
            narration=request.data.get('narration', ''),
            date=request.data.get('date','')
        )
    except ValidationError as e:
        return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    return Response({"detail": "Transfer successfully created", "id": transfer.id}, status=status.HTTP_201_CREATED)
