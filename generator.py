import numpy as np
import random
import re
from utils import luhn_check, IIN_Ranges, IIN_Ranges_List


def detect_card_brand(bin_number):
    if bin_number.startswith('4'):
        return 'Visa'
    elif bin_number.startswith(('51', '52', '53', '54', '55')):
        return 'Mastercard'
    elif bin_number.startswith(('34', '37')):
        return 'American Express'
    else:
        return 'Unknown'

def update_card_brand_display(bin_entry, card_vars):
    bin_number = bin_entry.get()
    brand = detect_card_brand(bin_number)

    for var in card_vars.values():
        var.set(0)

    if brand in card_vars:
        card_vars[brand].set(1)

def generate_pan(credit_card):
    if credit_card.count("?") > 0 and len(credit_card) <= 16:
        possibilities = np.uint64(10 ** credit_card.count("?"))
        counter = 0

        IIN_tuple_ranges = IIN_Ranges_List()

        PANasList = list(credit_card)  # Convert the PAN number into a List

        L = []  # A list with the indexes of the ? characters as found in given PAN
        for m in re.finditer('\?', credit_card):
            L.append(m.start())

        valid_pans = []
        while counter < possibilities:
            STR = str(counter).zfill(credit_card.count("?"))
            counter += 1

            for index, char in zip(L, STR):
                PANasList[index] = char

            tempPAN = "".join(PANasList)

            if is_luhn_valid(tempPAN) and IIN_Ranges(tempPAN, IIN_tuple_ranges):
                valid_pans.append(tempPAN)

        return valid_pans

# function to check if a card number is valid based on the luhn algorithm.
def is_luhn_valid(card_number):
    return luhn_check(card_number) == 0

def generate_cvv():
    return str(random.randint(100, 999))
