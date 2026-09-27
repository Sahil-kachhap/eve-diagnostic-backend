import uuid


class MockPaymentProvider:

    @staticmethod
    def create_payment(*, amount):
        return {
            "provider_payment_id": f"mock_{uuid.uuid4().hex}",
            "status": "PENDING",
            "amount": amount,
        }