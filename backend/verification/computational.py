
from backend.sandbox.executor import arithmetic
def check(expression, claimed):
    return arithmetic(expression)==claimed
