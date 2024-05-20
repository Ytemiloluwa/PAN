import logging

logging.basicConfig(filename='pan_generator.log', level=logging.INFO)

def luhn_check(pan):
    sum = 0
    num_length = len(pan)
    oddeven = num_length & 1
    for count in range(num_length):
        digit = int(pan[count])
        if not ((count & 1) ^ oddeven):
            digit *= 2
        if digit > 9:
            digit -= 9
        sum += digit
    return (sum % 10) == 0

def bin_ranges(pan):
    # Validate against known BIN ranges
    bin_list = ['4', '5', '51', '52', '53', '54', '55', '6011', '65', '35', '34', '37']
    return any(pan.startswith(bin) for bin in bin_list)
