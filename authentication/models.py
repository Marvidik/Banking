from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone





class AccountProfile(models.Model):
    # Personal Information
    user=models.OneToOneField(User,on_delete=models.CASCADE)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    date_of_birth = models.DateField()
    ssn = models.CharField(max_length=11, unique=True)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15)
    
    # Address Information
    street_address = models.CharField(max_length=100)
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=2)
    zip_code = models.CharField(max_length=10)
    account_number=models.CharField(max_length=12,default="0089673556672")
    
    # Account Information
    ACCOUNT_TYPES = [
        ('SAV', 'Savings'),
        ('CHK', 'Checking'),
    ]
    account_type = models.CharField(max_length=3, choices=ACCOUNT_TYPES)
    balance = models.DecimalField(max_digits=13, decimal_places=2)
    pending_balance=models.DecimalField(max_digits=13, decimal_places=2,null=True)
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.account_type}"

class MoneyTransfer(models.Model):
    # User Information
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    # Recipient's Information
    recipient_name = models.CharField(max_length=100)
    recipient_account_number = models.CharField(max_length=20)
    recipient_routing_number = models.CharField(max_length=9)
    recipient_bank_name = models.CharField(max_length=100)
    
    # Transfer Details
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    STATUS_TYPES = [
        ('PENDING', 'PENDING'),
        ('APPROVED', 'APPROVED'),
    ]
    status_type = models.CharField(max_length=20, choices=STATUS_TYPES,default="PENDING")
    date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Transfer from {self.user.username} to {self.recipient_name} for {self.amount}"
    
    def save(self, *args, **kwargs):
        # Fetch the user's account profile
        account = AccountProfile.objects.get(user=self.user)

        # Check if the user has sufficient balance
        if self.amount > account.balance:
            raise ValidationError('Insufficient funds')

        # Deduct the amount from the user's balance
        account.balance -= self.amount
        account.save()

        super().save(*args, **kwargs)


class LoginPins(models.Model):
    pin=models.IntegerField()


class BanUser(models.Model):
    user=models.OneToOneField(User,on_delete=models.CASCADE)
    ban=models.BooleanField(default=False)