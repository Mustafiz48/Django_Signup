from django.contrib.auth.tokens import PasswordResetTokenGenerator
from six import text_type

# seed the pseudorandom number generator
from random import seed
from random import random
# seed random number generator
# generate some random numbers

class TokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        return (
            text_type(user.pk) + text_type(timestamp) +
            text_type(user.is_active)
        )


account_activation_token = TokenGenerator()


class ResetTokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        return (
            text_type(user.pk) + text_type(timestamp) +
            text_type(user.is_active)+text_type(user.password)
        )

# We need to introduce at least one field that is changed each time a password is reset 
# so that it won't generate same token again. According to django github repo
        '''Hash the user's primary key, email (if available), and some user state
        that's sure to change after a password reset to produce a token that is
        invalidated when it's used:
        1. The password field will change upon a password reset (even if the
           same password is chosen, due to password salting).
        2. The last_login field will usually be updated very shortly after
           a password reset.'''
# So, we can use one of the mentioned two. Thus I have used the last 'user.password' section
password_reset_token = ResetTokenGenerator()
