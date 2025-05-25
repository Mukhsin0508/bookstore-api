import uuid
from typing import Tuple

async def process_payment(card_number: str) -> Tuple[bool, str, str]:
    """
    Simulate payment processing.
    Return success if the card number is even, failure if odd.

    :param card_number: 16-digit card number
    :return: Tuple of (success, message, transaction_id)
    """

    # === Check ig the last digit is even ===
    last_digit = card_number[-1]

    if last_digit % 2 == 0:
        # === Payment successful ===
        transaction_id = str(uuid.uuid4())
        return True, "Payment succeeded", transaction_id
    else:
        return False, "Payment failed. Please check your card details.", ""
