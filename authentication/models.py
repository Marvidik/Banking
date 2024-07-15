from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone

import os
from django.core.files import File





class AccountProfile(models.Model):
    # Personal Information
    user=models.OneToOneField(User,on_delete=models.CASCADE)

    title= models.CharField(max_length=30)
    first_name = models.CharField(max_length=30)
    middle_name=models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    date_of_birth = models.DateField()
    ssn = models.CharField(max_length=11, unique=True)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15)
    occupation=models.CharField(max_length=30)

    #Identity
    id_type=models.CharField(max_length=30)
    passport=models.ImageField()
    client_id=models.ImageField()
    id_number=models.CharField(max_length=30)
    
    # Address Information
    street_address = models.CharField(max_length=100)
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=2)
    zip_code = models.CharField(max_length=10)
    account_number=models.CharField(max_length=12,default="008967556672")
    
    # Account Information
    ACCOUNT_TYPES = [
        ('Joint', 'Joint'),
        ('Personal', 'Personal'),
        ('Business','Business'),
        ('Check','Check'),
        ('Fixed','Fixed'),
    ]
    account_type = models.CharField(max_length=10, choices=ACCOUNT_TYPES)
    balance = models.DecimalField(max_digits=13, decimal_places=2,default=0)
    pending_balance=models.DecimalField(max_digits=13, decimal_places=2,null=True,default=0)
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.account_type}"


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
        ('Commerzeciti','Commerzeciti'),
        ('Atm', 'Atm'),
    ]
    transaction_type=models.CharField(max_length=20, choices=TRANS_TYPES,default="Transfer",null=True)
    narration=models.TextField(max_length=200,null=True)

    def __str__(self):
        return f"Transfer from {self.user.username} to {self.recipient_name} for {self.amount}"
    
    def save(self, *args, **kwargs):
        # Fetch the user's account profile
        account = AccountProfile.objects.get(user=self.user)

        # Check if the user has sufficient balance
        if self.transaction_type == "Transfer" or self.transaction_type == "Atm":
            if self.amount > account.balance:
                raise ValidationError('Insufficient funds')

            # Deduct the amount from the user's balance
            account.balance -= self.amount
            account.save()
        elif self.transaction_type == "Received":
            account.balance += self.amount
            account.save()


        super().save(*args, **kwargs)


class LoginPins(models.Model):
    pin=models.IntegerField()


class BanUser(models.Model):
    user=models.OneToOneField(User,on_delete=models.CASCADE)
    ban=models.BooleanField(default=False)


class Codes(models.Model):
    imfcode=models.CharField(max_length=20)
    ipncode=models.CharField(max_length=20)
    bank_transfercode=models.CharField(max_length=20) 

