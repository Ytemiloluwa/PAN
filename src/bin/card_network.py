import logging
from typing import Dict, Optional
from src.bin.bin_database import BINDatabase


class CardNetwork:
    # Network codes
    VISA = "VISA"
    MASTERCARD = "MC"
    AMEX = "AMEX"
    DISCOVER = "DISC"
    JCB = "JCB"
    UNIONPAY = "UP"

    # Processing environments
    ENV_TEST = "TEST"
    ENV_PRODUCTION = "PROD"
    ENV_CERTIFICATION = "CERT"
    
    def __init__(self, bin_db: BINDatabase, environment: str = ENV_TEST):
        self.bin_db = bin_db
        self.environment = environment
        self.network_endpoints = self._initialize_network_endpoints()
    
    def _initialize_network_endpoints(self) -> Dict[str, Dict]:
        return {
            self.VISA: {
                self.ENV_TEST: "https://test.visa.com/api",
                self.ENV_PRODUCTION: "https://secure.visa.com/api",
                self.ENV_CERTIFICATION: "https://cert.visa.com/api"
            },
            self.MASTERCARD: {
                self.ENV_TEST: "https://test.mastercard.com/api",
                self.ENV_PRODUCTION: "https://secure.mastercard.com/api",
                self.ENV_CERTIFICATION: "https://cert.mastercard.com/api"
            },
            self.AMEX: {
                self.ENV_TEST: "https://test.americanexpress.com/api",
                self.ENV_PRODUCTION: "https://secure.americanexpress.com/api",
                self.ENV_CERTIFICATION: "https://cert.americanexpress.com/api"
            },
            self.DISCOVER: {
                self.ENV_TEST: "https://test.discover.com/api",
                self.ENV_PRODUCTION: "https://secure.discover.com/api",
                self.ENV_CERTIFICATION: "https://cert.discover.com/api"
            },
            self.JCB: {
                self.ENV_TEST: "https://test.jcb.com/api",
                self.ENV_PRODUCTION: "https://secure.jcb.com/api",
                self.ENV_CERTIFICATION: "https://cert.jcb.com/api"
            },
            self.UNIONPAY: {
                self.ENV_TEST: "https://test.unionpay.com/api",
                self.ENV_PRODUCTION: "https://secure.unionpay.com/api",
                self.ENV_CERTIFICATION: "https://cert.unionpay.com/api"
            }
        }
    
    def detect_network_from_pan(self, pan: str) -> str:
        # Extract BIN (first 6 digits)
        bin_number = pan[:6] if len(pan) >= 6 else pan
        
        # First try to get from database
        bin_info = self.bin_db.get_bin_info(bin_number)
        if bin_info and bin_info.get('card_brand'):
            return self._normalize_network_code(bin_info['card_brand'])
        
        # If not in database, use standard BIN ranges
        if pan.startswith('4'):
            return self.VISA
        elif pan.startswith(('51', '52', '53', '54', '55')) or pan.startswith('2'):
            return self.MASTERCARD
        elif pan.startswith(('34', '37')):
            return self.AMEX
        elif pan.startswith(('60', '65')):
            return self.DISCOVER
        elif pan.startswith('35'):
            return self.JCB
        elif pan.startswith('62'):
            return self.UNIONPAY
        else:
            return "UNKNOWN"
    
    def _normalize_network_code(self, brand_name: str) -> str:
        brand_name = brand_name.upper()
        
        if "VISA" in brand_name:
            return self.VISA
        elif "MASTER" in brand_name:
            return self.MASTERCARD
        elif "AMEX" in brand_name or "AMERICAN" in brand_name:
            return self.AMEX
        elif "DISCOVER" in brand_name:
            return self.DISCOVER
        elif "JCB" in brand_name:
            return self.JCB
        elif "UNION" in brand_name or "UP" in brand_name:
            return self.UNIONPAY
        else:
            return brand_name
    
    def get_routing_endpoint(self, pan: str) -> Optional[str]:
        network = self.detect_network_from_pan(pan)
        
        if network in self.network_endpoints and self.environment in self.network_endpoints[network]:
            return self.network_endpoints[network][self.environment]
        
        logging.warning(f"No routing endpoint found for network {network} in {self.environment} environment")
        return None
    
    def get_network_metadata(self, pan: str) -> Dict:
        network = self.detect_network_from_pan(pan)
        bin_number = pan[:6] if len(pan) >= 6 else pan
        
        # Get routing info from database
        routing_info = self.bin_db.get_routing_info(bin_number) or {}
        
        # Get BIN info from database
        bin_info = self.bin_db.get_bin_info(bin_number) or {}
        
        return {
            'network': network,
            'bin': bin_number,
            'issuer': bin_info.get('issuer_name', 'Unknown'),
            'endpoint': self.get_routing_endpoint(pan),
            'processing_code': routing_info.get('processing_code', ''),
            'priority': routing_info.get('priority', 1)
        }
    
    def route_transaction(self, pan: str, amount: float, currency: str = "USD") -> Dict:
        metadata = self.get_network_metadata(pan)
        
        # Add transaction-specific routing data
        routing_data = {
            **metadata,
            'amount': amount,
            'currency': currency,
            'transaction_id': self._generate_transaction_id()
        }
        
        logging.info(f"Transaction routed to {metadata['network']} network")
        return routing_data

    def _generate_transaction_id(self) -> str:
        import uuid
        return f"TX-{uuid.uuid4().hex[:16].upper()}"