import logging

logging.basicConfig(filename='pan_generator.log', level=logging.INFO)

def luhn_check(pan):
    def digits_of(n):
        return [int(d) for d in str(n)]
    digits = digits_of(pan)
    odd_digits = digits[-1::-2]
    even_digits = digits[-2::-2]
    checksum = sum(odd_digits)
    for d in even_digits:
        checksum += sum(digits_of(d * 2))
    return checksum % 10

def bin_ranges(pan):
    # Validate against known BIN ranges
    bin_list = ['4', '5', '51', '52', '53', '54', '55', '6011', '65', '35', '34', '37']
    return any(pan.startswith(bin) for bin in bin_list)

def IIN_Ranges_List():

    # Example ranges for Visa, Mastercard,and AmEX
    return ["4", "5", "3", "6"]

# function to check if a card number matches IIN(issuer identification number)ranges
def IIN_Ranges(credit_card, IIN_tuple_ranges):
    for iin in IIN_tuple_ranges:
        if credit_card[0:len(iin)] == str(iin):
            return True
            break
    return False
