import sqlite3
import os
import csv
import logging
from typing import Dict, List, Optional, Tuple


class BINDatabase:
    """
    BIN (Bank Identification Number) database manager for storing and retrieving
    card issuer information and routing details.
    """
    
    def __init__(self, db_path="bin_database.db"):
        """Initialize the BIN database connection"""
        self.db_path = db_path
        self.conn = None
        self.cursor = None
        self.initialize_database()
    
    def initialize_database(self):
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.cursor = self.conn.cursor()
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS bin_info (
                    bin TEXT PRIMARY KEY,
                    issuer_name TEXT,
                    card_brand TEXT,
                    card_type TEXT,
                    country_code TEXT,
                    bank_phone TEXT,
                    bank_url TEXT
                )
            ''')
            
            # Create routing table
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS routing_info (
                    bin TEXT PRIMARY KEY,
                    network_id TEXT,
                    processing_code TEXT,
                    priority INTEGER,
                    FOREIGN KEY (bin) REFERENCES bin_info(bin)
                )
            ''')
            
            self.conn.commit()
            logging.info("BIN database initialized successfully")
        except sqlite3.Error as e:
            logging.error(f"Database initialization error: {e}")
    
    def add_bin(self, bin_number: str, issuer_name: str, card_brand: str, 
                card_type: str = "", country_code: str = "", 
                bank_phone: str = "", bank_url: str = "") -> bool:
        """
        Add a new BIN to the database
        
        Args:
            bin_number: The Bank Identification Number
            issuer_name: Name of the issuing bank
            card_brand: Card brand (Visa, Mastercard, etc.)
            card_type: Type of card (Debit, Credit, etc.)
            country_code: ISO country code
            bank_phone: Contact phone for the bank
            bank_url: URL of the bank's website
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            self.cursor.execute('''
                INSERT OR REPLACE INTO bin_info 
                (bin, issuer_name, card_brand, card_type, country_code, bank_phone, bank_url)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (bin_number, issuer_name, card_brand, card_type, country_code, bank_phone, bank_url))
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            logging.error(f"Error adding BIN {bin_number}: {e}")
            return False
    
    def add_routing_info(self, bin_number: str, network_id: str, 
                         processing_code: str = "", priority: int = 1) -> bool:
        """
        Add routing information for a BIN
        
        Args:
            bin_number: The Bank Identification Number
            network_id: ID of the processing network
            processing_code: Code used for routing
            priority: Priority level for routing decisions
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            self.cursor.execute('''
                INSERT OR REPLACE INTO routing_info 
                (bin, network_id, processing_code, priority)
                VALUES (?, ?, ?, ?)
            ''', (bin_number, network_id, processing_code, priority))
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            logging.error(f"Error adding routing info for BIN {bin_number}: {e}")
            return False
    
    def get_bin_info(self, bin_number: str) -> Optional[Dict]:
        """
        Get information about a specific BIN
        
        Args:
            bin_number: The BIN to look up
            
        Returns:
            Dict containing BIN information or None if not found
        """
        try:
            self.cursor.execute('''
                SELECT bin, issuer_name, card_brand, card_type, country_code, bank_phone, bank_url
                FROM bin_info WHERE bin = ?
            ''', (bin_number,))
            
            row = self.cursor.fetchone()
            if row:
                return {
                    'bin': row[0],
                    'issuer_name': row[1],
                    'card_brand': row[2],
                    'card_type': row[3],
                    'country_code': row[4],
                    'bank_phone': row[5],
                    'bank_url': row[6]
                }
            return None
        except sqlite3.Error as e:
            logging.error(f"Error retrieving BIN info for {bin_number}: {e}")
            return None
    
    def get_routing_info(self, bin_number: str) -> Optional[Dict]:
        """
        Get routing information for a specific BIN
        
        Args:
            bin_number: The BIN to look up routing for
            
        Returns:
            Dict containing routing information or None if not found
        """
        try:
            self.cursor.execute('''
                SELECT bin, network_id, processing_code, priority
                FROM routing_info WHERE bin = ?
            ''', (bin_number,))
            
            row = self.cursor.fetchone()
            if row:
                return {
                    'bin': row[0],
                    'network_id': row[1],
                    'processing_code': row[2],
                    'priority': row[3]
                }
            return None
        except sqlite3.Error as e:
            logging.error(f"Error retrieving routing info for {bin_number}: {e}")
            return None
    
    def import_bins_from_csv(self, file_path: str) -> Tuple[int, int]:
        """
        Import BINs from a CSV file
        
        Args:
            file_path: Path to the CSV file
            
        Returns:
            Tuple of (success_count, error_count)
        """
        if not os.path.exists(file_path):
            logging.error(f"File not found: {file_path}")
            return (0, 0)
        
        success = 0
        errors = 0
        
        try:
            with open(file_path, 'r') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    try:
                        bin_number = row.get('bin', '')
                        if not bin_number:
                            errors += 1
                            continue
                            
                        # Add BIN info
                        if self.add_bin(
                            bin_number=bin_number,
                            issuer_name=row.get('issuer_name', ''),
                            card_brand=row.get('card_brand', ''),
                            card_type=row.get('card_type', ''),
                            country_code=row.get('country_code', ''),
                            bank_phone=row.get('bank_phone', ''),
                            bank_url=row.get('bank_url', '')
                        ):
                            # Add routing if network_id is present
                            if 'network_id' in row:
                                self.add_routing_info(
                                    bin_number=bin_number,
                                    network_id=row.get('network_id', ''),
                                    processing_code=row.get('processing_code', ''),
                                    priority=int(row.get('priority', 1))
                                )
                            success += 1
                        else:
                            errors += 1
                    except Exception as e:
                        logging.error(f"Error processing row: {e}")
                        errors += 1
                        
            return (success, errors)
        except Exception as e:
            logging.error(f"Error importing from CSV: {e}")
            return (success, errors)
    
    def search_bins(self, search_term: str, limit: int = 100) -> List[Dict]:
        """
        Search for BINs matching the search term
        
        Args:
            search_term: Term to search for
            limit: Maximum number of results to return
            
        Returns:
            List of matching BIN records
        """
        try:
            search_pattern = f"%{search_term}%"
            self.cursor.execute('''
                SELECT bin, issuer_name, card_brand, card_type, country_code
                FROM bin_info 
                WHERE bin LIKE ? OR issuer_name LIKE ? OR card_brand LIKE ?
                LIMIT ?
            ''', (search_pattern, search_pattern, search_pattern, limit))
            
            results = []
            for row in self.cursor.fetchall():
                results.append({
                    'bin': row[0],
                    'issuer_name': row[1],
                    'card_brand': row[2],
                    'card_type': row[3],
                    'country_code': row[4]
                })
            return results
        except sqlite3.Error as e:
            logging.error(f"Error searching BINs: {e}")
            return []
    
    def close(self):
        if self.conn:
            self.conn.close() 