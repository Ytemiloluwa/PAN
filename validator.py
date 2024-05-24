from utils import luhn_check, bin_ranges
from datetime import datetime
import re
from generator import is_luhn_valid

def validate_pan(pan):
    if re.match(r'^\d+$', pan) and len(pan) == 16:
        if is_luhn_valid(pan):
            return True, "The PAN is valid."
        else:
            return False, "The PAN is invalid (Failed Luhn Check)."
    else:
        return False, "The PAN must be a 16-digit number."

def detect_card_brand(pan):
    brands = {
        '4': 'Visa',
        '5': 'MasterCard',
        '3':  'American Express'
    }
    return brands.get(pan[0], "Unknown")

def validate_expiry_date(expiry_date):
    try:
        exp_date = datetime.strptime(expiry_date, "%m/%y")
        if exp_date > datetime.now():
            return True, "Card is not expired"
        else:
            return False, "Card is expired"
    except ValueError:
        return False, "Invalid date format"
