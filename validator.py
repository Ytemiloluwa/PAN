from utils import luhn_check, bin_ranges
from datetime import datetime

def validate_pan(pan):
    if not luhn_check(pan):
        return False, "Failed Luhn check"
    if not bin_ranges(pan):
        return False, "Invalid BIN range"
    return True, "Valid PAN"

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
