from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone

import os
from django.core.files import File

import random

from django.core.mail import send_mail





class AccountProfile(models.Model):
    # Personal Information
    user=models.OneToOneField(User,on_delete=models.CASCADE)

    title= models.CharField(max_length=30,null=True)
    first_name = models.CharField(max_length=30,null=True)
    middle_name=models.CharField(max_length=30,null=True)
    last_name = models.CharField(max_length=30,null=True)
    date_of_birth = models.DateField(null=True)
    ssn = models.CharField(max_length=11, unique=True,null=True)
    email = models.EmailField(unique=True,null=True)
    phone_number = models.CharField(max_length=15,null=True)
    occupation=models.CharField(max_length=30,null=True)

    #Identity
    id_type=models.CharField(max_length=30,null=True)
    passport=models.ImageField(null=True)
    client_id=models.ImageField(null=True)
    id_number=models.CharField(max_length=30,null=True)

    # Address Information
    street_address = models.CharField(max_length=100,null=True)
    city = models.CharField(max_length=50,null=True)
    state = models.CharField(max_length=50,null=True)
    zip_code = models.CharField(max_length=10,null=True)
    account_number=models.CharField(max_length=12,null=True,unique=True)

    verified=models.BooleanField(default=False,null=True)
    # Account Information
    ACCOUNT_TYPES = [
        ('Joint', 'Joint'),
        ('Personal', 'Personal'),
        ('Business','Business'),
        ('Check','Check'),
        ('Fixed','Fixed'),
    ]
    account_type = models.CharField(max_length=10, choices=ACCOUNT_TYPES,null=True)
    balance = models.DecimalField(max_digits=13, decimal_places=2,default=0)
    pending_balance=models.DecimalField(max_digits=13, decimal_places=2,null=True,default=0)

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.account_type}"

    def save(self, *args, **kwargs):
        if not self.account_number:
            while True:
                # Generate a random 10-digit account number
                random_account_number = ''.join([str(random.randint(0, 9)) for _ in range(10)])

                # Check if the generated account number already exists
                if not AccountProfile.objects.filter(account_number=random_account_number).exists():
                    self.account_number = random_account_number
                    break

        # Set the email to be the same as the user's email
        self.user.email = self.email
        self.user.save()

        super().save(*args, **kwargs)

class SecurityAnswers(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    ans1=models.CharField(max_length=100,null=True)
    ans2=models.CharField(max_length=100,null=True)

    def __str__(self):
        return self.user.username

class TransactionPin(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    transfer_pin=models.IntegerField()

    def __str__(self):
        return self.user.username

class MoneyTransfer(models.Model):
    # User Information
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    # Recipient's Information
    recipient_name = models.CharField(max_length=100)
    recipient_account_number = models.CharField(max_length=20)
    recipient_routing_number = models.CharField(max_length=9)
    recipient_bank_name = models.CharField(max_length=100)
    swift_code=models.CharField(max_length=100,null=True)

    # Transfer Details
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    STATUS_TYPES = [
        ('PENDING', 'PENDING'),
        ('APPROVED', 'APPROVED'),
    ]
    status_type = models.CharField(max_length=20, choices=STATUS_TYPES,default="PENDING")
    date = models.DateTimeField(default=timezone.now)
    TRANS_TYPES = [
        ('Received', 'Received'),
        ('Local', 'Local'),
        ('International', 'International'),
        ('Inter-bank','Inter-bank'),
        ('Atm', 'Atm'),
    ]
    transaction_type=models.CharField(max_length=20, choices=TRANS_TYPES,default="Transfer",null=True)
    narration=models.TextField(max_length=200,null=True)

    def __str__(self):
        return f"{self.user.username} {self.transaction_type}   {self.amount}"

    def save(self, *args, **kwargs):
        if not self.date:
            self.date = timezone.now()

        # Fetch the user's account profile
        account = AccountProfile.objects.get(user=self.user)

        # Check if the user has sufficient balance
        if self.transaction_type == "International" or self.transaction_type == "Local":
            if self.amount > account.balance:
                raise ValidationError('Insufficient funds')

            # Deduct the amount from the user's balance
            account.balance -= self.amount
            account.save()
        elif self.transaction_type == "Received":
            account.balance += self.amount
            account.save()
        elif self.transaction_type == "Inter-bank":
            if self.amount > account.balance:

                raise ValidationError('Insufficient funds')
            # Validate recipient account number and update recipient balance if valid

            recipient_account = self.validate_recipient_account(self.recipient_account_number)
            if recipient_account:
                account.balance -= self.amount
                self.status_type='APPROVED'
                account.save()
                recipient_account.save()
                # Create a "Received" transaction entry for the recipient
                MoneyTransfer.objects.create(
                    user=recipient_account.user,
                    recipient_name=self.user.username,  # Sender's username as recipient name
                    recipient_account_number=self.user.accountprofile.account_number,  # Sender's account number as recipient account number
                    recipient_routing_number="",  # You may add sender's routing number if applicable
                    recipient_bank_name="",  # You may add sender's bank name if applicable
                    swift_code="",  # You may add sender's swift code if applicable
                    amount=self.amount,
                    status_type='APPROVED',
                    date=self.date,
                    transaction_type='Received',
                    narration=f"Received from {self.user.username}"
                )
            else:
                raise ValidationError('Invalid recipient account number')

        super().save(*args, **kwargs)

    def validate_recipient_account(self, account_number):
        try:
            return AccountProfile.objects.get(account_number=account_number)
        except AccountProfile.DoesNotExist:
            return None

class LoginPins(models.Model):
    pin=models.IntegerField()


class BanUser(models.Model):
    user=models.OneToOneField(User,on_delete=models.CASCADE)
    ban=models.BooleanField(default=False)


class Codes(models.Model):
    imfcode=models.CharField(max_length=20)
    ipncode=models.CharField(max_length=20)
    bank_transfercode=models.CharField(max_length=20)



class OTP(models.Model):
    user=models.OneToOneField(User,on_delete=models.CASCADE)
    otp=models.CharField(max_length=5)
