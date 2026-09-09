import json
from decimal import Decimal, InvalidOperation

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST

from .models import PaymentTransaction


@csrf_exempt
@login_required
@require_POST
def submit_crypto_transaction(request):
    try:
        payload = json.loads(request.body or "{}")
    except json.JSONDecodeError:
        return JsonResponse({"detail": "بدنه درخواست معتبر نیست."}, status=400)

    try:
        amount_toman = Decimal(str(payload.get("amount_toman", 0)))
        rate_toman = Decimal(settings.CRYPTO_USDT_RATE_TOMAN)
        amount = (amount_toman / rate_toman).quantize(Decimal("0.000001"))
    except (InvalidOperation, TypeError, ValueError):
        amount_toman = Decimal("0")
        amount = Decimal("0")
    if amount_toman <= 0 or amount <= 0:
        return JsonResponse({"detail": "مبلغ تراکنش باید بیشتر از صفر باشد."}, status=400)

    user = request.user
    transaction = PaymentTransaction.objects.create(
        user=user,
        customer_name=user.get_full_name(),
        customer_email=user.email,
        customer_phone=user.username if user.username.startswith("09") else "",
        amount=amount,
        currency=payload.get("currency", "USDT"),
        method=PaymentTransaction.Method.CRYPTO,
        transaction_hash=str(payload.get("transaction_hash", "")).strip(),
        network=settings.CRYPTO_NETWORK,
        wallet_address=settings.CRYPTO_WALLET_ADDRESS,
        items=payload.get("items", []),
        shipping_address=payload.get("shipping_address", {}),
    )
    return JsonResponse({"ok": True, "transaction_id": transaction.pk, "status": transaction.status}, status=201)


@login_required
@require_GET
def my_orders(request):
    transactions = PaymentTransaction.objects.filter(user=request.user).order_by("-created_at")
    return JsonResponse({
        "orders": [
            {
                "id": transaction.id,
                "amount": str(transaction.amount),
                "currency": transaction.currency,
                "payment_status": transaction.status,
                "payment_status_label": transaction.get_status_display(),
                "order_status": transaction.order_status,
                "order_status_label": transaction.get_order_status_display(),
                "method_label": transaction.get_method_display(),
                "transaction_hash": transaction.transaction_hash,
                "items": transaction.items,
                "created_at": transaction.created_at.isoformat(),
                "paid_at": transaction.paid_at.isoformat() if transaction.paid_at else None,
            }
            for transaction in transactions
        ]
    })
