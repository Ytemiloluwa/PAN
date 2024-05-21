from utils import luhn_check, bin_ranges

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
        # Add more brands here
    }
    return brands.get(pan[0], "Unknown")

