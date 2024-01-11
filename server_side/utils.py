import random

def generate_sample(time):
    # time || temperature || hum
    return f"{time} || {random.randint(0, 40)} || {random.randint(30, 100)}" 