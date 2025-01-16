from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import F

from users.models import UserProfile


async def deduct_tokens(user: User, amount: int) -> bool:
    """
    Deduct a specified number of tokens from a user's profile.

    Args:
        user (User): The user whose tokens are to be deducted.
        amount (int): The number of tokens to deduct.

    Returns:
        bool: True if tokens were successfully deducted, False otherwise.
    """
    try:
        profile: UserProfile = await UserProfile.objects.aget(user=user)

        if profile.available_tokens >= amount:
            # Perform the update on the queryset level
            await UserProfile.objects.filter(user=user).aupdate(available_tokens=F("available_tokens") - amount)
            return True
    except ObjectDoesNotExist:
        return False
    else:
        return False
