# from django.contrib.auth.models import AbstractUser
# from django.db import models
# from django.utils import timezone

# class User(AbstractUser):
#     pass

# class Wallet(models.Model):
#     CURRENCY_CHOICES = [
#         ('BTC', 'Bitcoin'),
#         ('ETH', 'Ethereum'),
#         ('LTC', 'Litecoin'),
#     ]

#     user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="wallets")
#     currency = models.CharField(max_length=10, choices=CURRENCY_CHOICES)
#     balance = models.DecimalField(max_digits=20, decimal_places=8, default=0)

#     def __str__(self):
#         return f"{self.user.username} - {self.currency}"

# class Transaction(models.Model):
#     TRANSACTION_TYPES = [
#         ('credit', 'Credit'),
#         ('debit', 'Debit'),
#     ]

#     wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name="transactions")
#     amount = models.DecimalField(max_digits=20, decimal_places=8)
#     transaction_type = models.CharField(max_length=6, choices=TRANSACTION_TYPES)
#     timestamp = models.DateTimeField(default=timezone.now)

#     def save(self, *args, **kwargs):
#         if self.transaction_type == 'debit' and self.amount > self.wallet.balance:
#             raise ValueError("Insufficient balance.")
#         if self.transaction_type == 'credit':
#             self.wallet.balance += self.amount
#         else:
#             self.wallet.balance -= self.amount
#         self.wallet.save()
#         super().save(*args, **kwargs)

#     def __str__(self):
#         return f"{self.transaction_type} {self.amount} {self.wallet.currency}"


from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone

class User(AbstractUser):
    pass

class Wallet(models.Model):
    CURRENCY_CHOICES = [
        ('BTC', 'Bitcoin'),
    ('ETH', 'Ethereum'),
    ('LTC', 'Litecoin'),
    ('BNB', 'Binance Coin'),
    ('SOL', 'Solana'),
    ('XRP', 'Ripple'),
    ('ADA', 'Cardano'),
    ('DOT', 'Polkadot'),
    ('DOGE', 'Dogecoin'),
    ('AVAX', 'Avalanche'),
    ('SHIB', 'Shiba Inu'),
    ('USDT', 'Tether'),
    ('USDC', 'USD Coin'),
    ('LINK', 'Chainlink'),
    ('HBAR', 'Hedera'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="wallets")
    currency = models.CharField(max_length=10, choices=CURRENCY_CHOICES)
    balance = models.DecimalField(max_digits=20, decimal_places=8, default=0)
    class Meta:
        unique_together = [
            ('user', 'currency'), # each user has only 1 wallet/currency
        ]
        indexes = [
            models.Index(fields=["user", "currency"]),
        ]
    def __str__(self):
        return f"{self.user.username} - {self.currency}"

class Transaction(models.Model):
    TRANSACTION_TYPES = [
        ('credit', 'Credit'),
        ('debit', 'Debit'),
    ]
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name="transactions")
    amount = models.DecimalField(max_digits=20, decimal_places=8)
    transaction_type = models.CharField(max_length=6, choices=TRANSACTION_TYPES)
    timestamp = models.DateTimeField(default=timezone.now)
    class Meta:
        indexes = [
            models.Index(fields=['wallet']),
            models.Index(fields=['timestamp']),
        ]
    def __str__(self):
        return f"{self.transaction_type} {self.amount} {self.wallet.currency}"
