# from rest_framework import viewsets, permissions, filters, status
# from rest_framework.response import Response
# from django.db import transaction as db_transaction
# import requests
# from rest_framework.views import APIView
# from .models import Wallet, Transaction
# from .serializers import WalletSerializer, TransactionSerializer

# class WalletViewSet(viewsets.ModelViewSet):
#     serializer_class = WalletSerializer
#     permission_classes = [permissions.IsAuthenticated]

#     def get_queryset(self):
#         return Wallet.objects.filter(user=self.request.user)

#     def perform_create(self, serializer):
#         serializer.save(user=self.request.user)

# class TransactionViewSet(viewsets.ModelViewSet):
#     serializer_class = TransactionSerializer
#     permission_classes = [permissions.IsAuthenticated]
#     filter_backends = [filters.OrderingFilter, filters.SearchFilter]
#     search_fields = ['wallet__currency']
#     ordering_fields = ['timestamp']

#     def get_queryset(self):
#         return Transaction.objects.filter(wallet__user=self.request.user)

#     @db_transaction.atomic
#     def perform_create(self, serializer):
#         wallet = serializer.validated_data['wallet']
#         amount = serializer.validated_data['amount']
#         transaction_type = serializer.validated_data['transaction_type']

#         wallet = Wallet.objects.select_for_update().get(pk=wallet.pk)

#         if transaction_type == 'debit' and wallet.balance < amount:
#             raise serializers.ValidationError("Insufficient balance")

#         if transaction_type == 'credit':
#             wallet.balance += amount
#         else:
#             wallet.balance -= amount
#         wallet.save()
#         serializer.save()

# class PriceTicker(APIView):
#     permission_classes = [permissions.AllowAny]

#     def get(self, request):
#         currencies = request.query_params.get('currencies', 'bitcoin,ethereum')
#         url = f"https://api.coingecko.com/api/v3/simple/price?ids={currencies}&vs_currencies=usd"
#         response = requests.get(url)
#         if response.status_code == 200:
#             return Response(response.json())
#         return Response({"error": "Failed to fetch prices"}, status=status.HTTP_503_SERVICE_UNAVAILABLE)



from rest_framework import status, generics, permissions, viewsets, filters
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django.db import transaction as db_transaction
from .models import Wallet, Transaction
from .serializers import (
    UserRegisterSerializer, UserSerializer,
    WalletSerializer, TransactionSerializer
)
from .permissions import IsOwner
from rest_framework.views import APIView
import requests
from django_filters.rest_framework import DjangoFilterBackend

User = get_user_model()

class RegisterUserView(generics.CreateAPIView):
    serializer_class = UserRegisterSerializer
    permission_classes = [permissions.AllowAny]

class MeView(generics.RetrieveAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    def get_object(self):
        return self.request.user

class WalletViewSet(viewsets.ModelViewSet):
    serializer_class = WalletSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['currency']
    ordering_fields = ['balance']

    def get_queryset(self):
        return Wallet.objects.filter(user=self.request.user).select_related('user')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class TransactionViewSet(viewsets.ModelViewSet):
    serializer_class = TransactionSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    filterset_fields = ['wallet', 'wallet__currency']
    ordering_fields = ['timestamp']
    search_fields = ['wallet__currency']

    def get_queryset(self):
        qs = Transaction.objects.filter(wallet__user=self.request.user).select_related('wallet', 'wallet__user')
        # date filtering (optional)
        start = self.request.query_params.get('start')
        end = self.request.query_params.get('end')
        if start:
            qs = qs.filter(timestamp__gte=start)
        if end:
            qs = qs.filter(timestamp__lte=end)
        return qs

    @db_transaction.atomic
    def perform_create(self, serializer):
        wallet = serializer.validated_data['wallet']
        amount = serializer.validated_data['amount']
        transaction_type = serializer.validated_data['transaction_type']
        wallet = Wallet.objects.select_for_update().get(pk=wallet.pk)  # Row lock

        if wallet.user != self.request.user:
            raise PermissionError("Not your wallet.")

        if transaction_type == 'debit':
            if wallet.balance < amount:
                raise serializers.ValidationError("Insufficient balance")
            wallet.balance -= amount
        else:
            wallet.balance += amount
        wallet.save()
        serializer.save()

# class PriceTicker(APIView):
#     """
#     currencies param: 'bitcoin,ethereum'
#     """
#     permission_classes = [permissions.AllowAny]
#     def get(self, request):
#         currencies = request.query_params.get('currencies', 'bitcoin,ethereum')
#         url = f"https://api.coingecko.com/api/v3/simple/price?ids={currencies}&vs_currencies=usd"
#         resp = requests.get(url, timeout=10)
#         if resp.status_code == 200:
#             return Response(resp.json())
#         return Response({'error': 'Failed to fetch prices'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)


class PriceTicker(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        currencies = request.query_params.get('currencies', 'bitcoin,ethereum')
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={currencies}&vs_currencies=usd"
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return Response(response.json())
        except requests.RequestException:
            return Response({"error": "Failed to fetch prices"}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
