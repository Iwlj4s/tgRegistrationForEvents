import random
import string


def get_code():
    code = ''.join(random.choice(string.digits) for _ in range(5))
    return code


print(get_code())
