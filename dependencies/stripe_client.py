import stripe
from stripe import StripeClient

from src.env_variables.env import env_variables


class StripeClientInstance:
    _stripe_instance: StripeClient = None

    def __init__(self):
        if self._stripe_instance is None:
            self._stripe_instance = stripe.StripeClient(api_key=env_variables.stripe_secret_key)

    def __call__(self):
        return self._stripe_instance
