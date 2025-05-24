import numpy as np
import random
import re
import logging
import concurrent.futures
from typing import List, Dict, Optional
from src.utils.utils import luhn_check, IIN_Ranges, IIN_Ranges_List
from datetime import datetime, timedelta

# Try to import BIN database if available
try:
    from src.bin.bin_database import BINDatabase
    BIN_DB_AVAILABLE = True
except ImportError:
    BIN_DB_AVAILABLE = False


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

# New functions for enhanced PAN generation

class PANGenerator:
    """Enhanced PAN Generator with batch processing capabilities"""
    
    def __init__(self, bin_db=None):
        """
        Initialize the PAN Generator
        
        Args:
            bin_db: Optional BINDatabase instance
        """
        self.bin_db = bin_db
    
    def generate_single_pan(self, template: str) -> Optional[str]:
        """
        Generate a single valid PAN based on a template
        
        Args:
            template: PAN template with ? for unknown digits
            
        Returns:
            A valid PAN or None if generation fails
        """
        pans = generate_pan(template)
        return pans[0] if pans else None
    
    def generate_batch(self, template: str, count: int = 100, 
                      max_attempts: int = 10000) -> List[str]:
        """
        Generate a batch of valid PANs based on a template
        
        Args:
            template: PAN template with ? for unknown digits
            count: Number of PANs to generate
            max_attempts: Maximum number of attempts
            
        Returns:
            List of valid PANs
        """
        if template.count("?") == 0:
            # No wildcards, just validate the provided PAN
            if is_luhn_valid(template):
                return [template]
            return []
        
        # If there are too many wildcards, it might be inefficient
        # to generate all possibilities first
        if template.count("?") > 8:
            return self._generate_batch_random(template, count, max_attempts)
        
        # Otherwise use the standard approach
        all_pans = generate_pan(template)
        
        # If we need more than available, return all
        if count >= len(all_pans):
            return all_pans
        
        # Otherwise return a random subset
        return random.sample(all_pans, count)
    
    def _generate_batch_random(self, template: str, count: int, 
                              max_attempts: int) -> List[str]:
        """
        Generate PANs using a random approach for templates with many wildcards
        
        Args:
            template: PAN template with ? for unknown digits
            count: Number of PANs to generate
            max_attempts: Maximum number of attempts
            
        Returns:
            List of valid PANs
        """
        valid_pans = set()
        attempts = 0
        
        while len(valid_pans) < count and attempts < max_attempts:
            # Generate a random candidate
            candidate = self._generate_random_candidate(template)
            
            # Check if valid
            if is_luhn_valid(candidate):
                valid_pans.add(candidate)
            
            attempts += 1
        
        return list(valid_pans)
    
    def _generate_random_candidate(self, template: str) -> str:
        """
        Generate a random PAN candidate from a template
        
        Args:
            template: PAN template with ? for unknown digits
            
        Returns:
            A PAN candidate (not necessarily valid)
        """
        result = list(template)
        
        for i, char in enumerate(template):
            if char == '?':
                result[i] = str(random.randint(0, 9))
        
        return ''.join(result)
    
    def generate_multi_bin_batch(self, bin_list: List[str], 
                               count_per_bin: int = 10) -> Dict[str, List[str]]:
        """
        Generate PANs for multiple BINs
        
        Args:
            bin_list: List of BIN prefixes
            count_per_bin: Number of PANs to generate per BIN
            
        Returns:
            Dictionary mapping BINs to lists of PANs
        """
        result = {}
        
        for bin_prefix in bin_list:
            # Create template with appropriate length
            if len(bin_prefix) < 6:
                logging.warning(f"BIN {bin_prefix} is shorter than 6 digits")
            
            # Standard card length is 16 digits
            template = bin_prefix + "?" * (16 - len(bin_prefix))
            
            # Generate PANs for this BIN
            pans = self.generate_batch(template, count_per_bin)
            result[bin_prefix] = pans
        
        return result
    
    def generate_with_metadata(self, template: str, count: int = 1) -> List[Dict]:
        """
        Generate PANs with additional metadata
        
        Args:
            template: PAN template with ? for unknown digits
            count: Number of PANs to generate
            
        Returns:
            List of dictionaries with PAN and metadata
        """
        pans = self.generate_batch(template, count)
        result = []
        
        for pan in pans:
            # Get card brand
            brand = detect_card_brand(pan)
            
            # Generate expiry date (1-5 years in the future)
            years_ahead = random.randint(1, 5)
            expiry_date = datetime.now() + timedelta(days=365 * years_ahead)
            expiry = expiry_date.strftime("%m/%y")
            
            # Generate CVV
            cvv = generate_cvv()
            
            # Get BIN info if available
            bin_info = {}
            if self.bin_db and BIN_DB_AVAILABLE:
                bin_number = pan[:6]
                bin_data = self.bin_db.get_bin_info(bin_number)
                if bin_data:
                    bin_info = bin_data
            
            # Create metadata
            metadata = {
                'pan': pan,
                'brand': brand,
                'expiry': expiry,
                'cvv': cvv,
                'bin': pan[:6],
                'last_four': pan[-4:],
                'issuer': bin_info.get('issuer_name', 'Unknown')
            }
            
            result.append(metadata)
        
        return result

def batch_generate_pans(templates: List[str], count_per_template: int = 10) -> Dict[str, List[str]]:
    """
    Generate PANs for multiple templates in parallel
    
    Args:
        templates: List of PAN templates
        count_per_template: Number of PANs to generate per template
        
    Returns:
        Dictionary mapping templates to lists of PANs
    """
    generator = PANGenerator()
    result = {}
    
    # Use thread pool for parallel processing
    with concurrent.futures.ThreadPoolExecutor() as executor:
        # Submit tasks
        future_to_template = {
            executor.submit(generator.generate_batch, template, count_per_template): template
            for template in templates
        }
        
        # Collect results
        for future in concurrent.futures.as_completed(future_to_template):
            template = future_to_template[future]
            try:
                pans = future.result()
                result[template] = pans
            except Exception as e:
                logging.error(f"Error generating PANs for template {template}: {e}")
                result[template] = []
    
    return result

def save_pans_to_file(pans: List[str], filename: str) -> bool:
    """
    Save generated PANs to a file
    
    Args:
        pans: List of PANs to save
        filename: Output filename
        
    Returns:
        True if successful, False otherwise
    """
    try:
        with open(filename, 'w') as f:
            for pan in pans:
                f.write(f"{pan}\n")
        return True
    except Exception as e:
        logging.error(f"Error saving PANs to file: {e}")
        return False

def save_pans_with_metadata(pans_with_metadata: List[Dict], filename: str) -> bool:
    """
    Save PANs with metadata to a CSV file
    
    Args:
        pans_with_metadata: List of dictionaries with PAN and metadata
        filename: Output filename
        
    Returns:
        True if successful, False otherwise
    """
    import csv
    
    try:
        with open(filename, 'w', newline='') as f:
            if not pans_with_metadata:
                return True
                
            # Get field names from the first item
            fieldnames = pans_with_metadata[0].keys()
            
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            for pan_data in pans_with_metadata:
                writer.writerow(pan_data)
                
        return True
    except Exception as e:
        logging.error(f"Error saving PANs with metadata to file: {e}")
        return False
