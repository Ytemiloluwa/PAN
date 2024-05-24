import numpy as np
import random
from utils import luhn_check, bin_ranges

CARD_BRANDS = {
    'Visa': '4',
    'Mastercard': '5',
    'American Express': '3'
}

def generate_pan(bin_input, count=1, brand=None):
    pan_list = []
    prefix = CARD_BRANDS.get(brand, '') if brand else ''
    for _ in range(count):
        temp_pan = ''.join([str(random.randint(0, 9)) if c == '?' else c for c in bin_input])
        temp_pan = prefix + temp_pan[len(prefix):]
        if luhn_check(temp_pan) and bin_ranges(temp_pan):
            pan_list.append(temp_pan)
    return pan_list

def generate_cvv():
    return str(random.randint(100, 999))
