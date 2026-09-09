from decimal import Decimal, InvalidOperation

from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.http import require_GET


@require_GET
def crypto_info(request):
    """Return the public receiving details used by the checkout UI."""
    return JsonResponse(
        {
            "network": settings.CRYPTO_NETWORK,
            "symbol": settings.CRYPTO_SYMBOL,
            "wallet_address": settings.CRYPTO_WALLET_ADDRESS,
            "token_contract": settings.CRYPTO_USDT_CONTRACT,
        }
    )


@require_GET
def crypto_quote(request):
    try:
        amount_toman = Decimal(request.GET.get("amount_toman", "0"))
        rate_toman = Decimal(settings.CRYPTO_USDT_RATE_TOMAN)
    except (InvalidOperation, TypeError, ValueError):
        return JsonResponse({"detail": "مبلغ یا نرخ معتبر نیست."}, status=400)
    if amount_toman <= 0 or rate_toman <= 0:
        return JsonResponse({"detail": "مبلغ باید بیشتر از صفر باشد."}, status=400)
    return JsonResponse({
        "amount_toman": str(amount_toman),
        "rate_toman": str(rate_toman),
        "amount_usdt": str((amount_toman / rate_toman).quantize(Decimal("0.000001"))),
        "currency": "USDT",
    })
