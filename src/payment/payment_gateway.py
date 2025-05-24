import uuid
import requests
from datetime import datetime
from typing import Dict, List, Any


class PaymentGateway:
    ENV_TEST = "test"
    ENV_PRODUCTION = "production"
    
    def __init__(self, api_key: str, merchant_id: str, environment: str = ENV_TEST):
        self.api_key = api_key
        self.merchant_id = merchant_id
        self.environment = environment
        self.base_url = self._get_base_url()
        self.supported_currencies = self._load_supported_currencies()
        
    def _get_base_url(self) -> str:
        if self.environment == self.ENV_PRODUCTION:
            return "https://api.fintechx-payments.com/v1"
        else:
            return "https://api-sandbox.fintechx-payments.com/v1"
    
    def _load_supported_currencies(self) -> Dict[str, Dict[str, Any]]:
        currencies = {
            "USD": {"name": "US Dollar", "symbol": "$", "decimal_places": 2},
            "EUR": {"name": "Euro", "symbol": "€", "decimal_places": 2},
            "GBP": {"name": "British Pound", "symbol": "£", "decimal_places": 2},
            "JPY": {"name": "Japanese Yen", "symbol": "¥", "decimal_places": 0},
            "CAD": {"name": "Canadian Dollar", "symbol": "$", "decimal_places": 2},
            "AUD": {"name": "Australian Dollar", "symbol": "$", "decimal_places": 2},
            "CNY": {"name": "Chinese Yuan", "symbol": "¥", "decimal_places": 2},
            "INR": {"name": "Indian Rupee", "symbol": "₹", "decimal_places": 2},
            "NGN": {"name": "Nigerian Naira", "symbol": "₦", "decimal_places": 2},
            "ZAR": {"name": "South African Rand", "symbol": "R", "decimal_places": 2}
        }
        return currencies
    
    def _generate_request_id(self) -> str:
        return f"req-{uuid.uuid4().hex}"
    
    def _format_amount(self, amount: float, currency: str) -> str:
        if currency not in self.supported_currencies:
            return str(amount)
        
        decimal_places = self.supported_currencies[currency]["decimal_places"]
        return f"{amount:.{decimal_places}f}"
    
    def _make_api_request(self, endpoint: str, method: str, data: Dict = None) -> Dict:
        url = f"{self.base_url}/{endpoint}"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "X-Merchant-ID": self.merchant_id,
            "X-Request-ID": self._generate_request_id()
        }
        
        if method.upper() == "GET":
            response = requests.get(url, headers=headers)
        elif method.upper() == "POST":
            response = requests.post(url, headers=headers, json=data)
        elif method.upper() == "PUT":
            response = requests.put(url, headers=headers, json=data)
        elif method.upper() == "DELETE":
            response = requests.delete(url, headers=headers)
        else:
            return {"error": "Invalid HTTP method"}
        
        if response.status_code in (200, 201):
            return response.json()
        else:
            return {
                "error": f"API request failed with status {response.status_code}",
                "details": response.text
            }
    
    def process_card_payment(self, card_data: Dict, amount: float, currency: str = "USD", 
                           customer_info: Dict = None, metadata: Dict = None) -> Dict:
        formatted_amount = self._format_amount(amount, currency)
        
        payload = {
            "transaction_type": "payment",
            "amount": formatted_amount,
            "currency": currency,
            "card": card_data,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {}
        }
        
        if customer_info:
            payload["customer"] = customer_info
        
        return self._make_api_request("payments/card", "POST", payload)
    
    def process_virtual_terminal_payment(self, card_data: Dict, amount: float, 
                                       currency: str = "USD", terminal_id: str = None,
                                       operator_id: str = None) -> Dict:
        formatted_amount = self._format_amount(amount, currency)
        
        payload = {
            "transaction_type": "card_present",
            "amount": formatted_amount,
            "currency": currency,
            "card": card_data,
            "timestamp": datetime.now().isoformat(),
            "terminal_id": terminal_id,
            "operator_id": operator_id
        }
        
        return self._make_api_request("terminal/process", "POST", payload)
    
    def create_payment_link(self, amount: float, currency: str = "USD", 
                           description: str = "", expiry_minutes: int = 60,
                           success_url: str = None, cancel_url: str = None) -> Dict:
        formatted_amount = self._format_amount(amount, currency)
        
        payload = {
            "amount": formatted_amount,
            "currency": currency,
            "description": description,
            "expiry_minutes": expiry_minutes,
            "success_url": success_url,
            "cancel_url": cancel_url
        }
        
        return self._make_api_request("payment-links", "POST", payload)
    
    def get_exchange_rate(self, from_currency: str, to_currency: str) -> Dict:
        endpoint = f"exchange-rates?from={from_currency}&to={to_currency}"
        return self._make_api_request(endpoint, "GET")
    
    def convert_amount(self, amount: float, from_currency: str, to_currency: str) -> Dict:
        rate_info = self.get_exchange_rate(from_currency, to_currency)
        
        if "error" in rate_info:
            return rate_info
        
        rate = rate_info.get("rate", 0)
        converted_amount = amount * rate
        
        return {
            "original_amount": amount,
            "original_currency": from_currency,
            "converted_amount": converted_amount,
            "target_currency": to_currency,
            "exchange_rate": rate,
            "timestamp": rate_info.get("timestamp")
        }
    
    def get_supported_currencies(self) -> List[Dict]:
        currencies = []
        for code, details in self.supported_currencies.items():
            currencies.append({
                "code": code,
                "name": details["name"],
                "symbol": details["symbol"]
            })
        return currencies
    
    def verify_transaction(self, transaction_id: str) -> Dict:
        return self._make_api_request(f"transactions/{transaction_id}/verify", "GET")
    
    def refund_transaction(self, transaction_id: str, amount: float = None, 
                          reason: str = None) -> Dict:
        payload = {
            "transaction_id": transaction_id,
            "reason": reason
        }
        
        if amount is not None:
            payload["amount"] = amount
            
        return self._make_api_request("refunds", "POST", payload)
    
    def create_customer(self, email: str, name: str = None, phone: str = None, 
                          metadata: Dict = None) -> Dict:
        payload = {
            "email": email,
            "name": name,
            "phone": phone,
            "metadata": metadata or {}
        }
        
        return self._make_api_request("customers", "POST", payload)
    
    def save_card(self, customer_id: str, card_data: Dict) -> Dict:
        payload = {
            "customer_id": customer_id,
            "card": card_data
        }
        
        return self._make_api_request("payment-methods/card", "POST", payload)
    
    def get_payment_methods(self, customer_id: str) -> Dict:
        return self._make_api_request(f"customers/{customer_id}/payment-methods", "GET")
    
    def create_webhook(self, url: str, events: List[str]) -> Dict:
        payload = {
            "url": url,
            "events": events
        }
        
        return self._make_api_request("webhooks", "POST", payload)

class ECommerceAPI:
    def __init__(self, payment_gateway: PaymentGateway):
        self.payment_gateway = payment_gateway
        
    def create_checkout_session(self, items: List[Dict], currency: str = "USD", 
                              success_url: str = None, cancel_url: str = None) -> Dict:
        total_amount = sum(item.get("price", 0) * item.get("quantity", 1) for item in items)
        
        return self.payment_gateway.create_payment_link(
            amount=total_amount,
            currency=currency,
            description=f"Purchase of {len(items)} items",
            success_url=success_url,
            cancel_url=cancel_url
        )
    
    def process_payment(self, payment_token: str, amount: float, 
                      currency: str = "USD", customer_info: Dict = None) -> Dict:
        card_data = {"token": payment_token}
        
        return self.payment_gateway.process_card_payment(
            card_data=card_data,
            amount=amount,
            currency=currency,
            customer_info=customer_info
        )
    
    def create_subscription(self, customer_id: str, plan_id: str, 
                          payment_method_id: str = None) -> Dict:
        payload = {
            "customer_id": customer_id,
            "plan_id": plan_id,
            "payment_method_id": payment_method_id
        }
        
        return self.payment_gateway._make_api_request("subscriptions", "POST", payload)
    
    def generate_client_token(self) -> Dict:
        return self.payment_gateway._make_api_request("client-token", "POST")


class VirtualTerminal:
    def __init__(self, payment_gateway: PaymentGateway, terminal_id: str, operator_id: str = None):
        self.payment_gateway = payment_gateway
        self.terminal_id = terminal_id
        self.operator_id = operator_id
        self.transaction_history = []
        
    def process_payment(self, card_data: Dict, amount: float, currency: str = "USD") -> Dict:
        result = self.payment_gateway.process_virtual_terminal_payment(
            card_data=card_data,
            amount=amount,
            currency=currency,
            terminal_id=self.terminal_id,
            operator_id=self.operator_id
        )
        
        if "error" not in result:
            self.transaction_history.append({
                "transaction_id": result.get("transaction_id"),
                "amount": amount,
                "currency": currency,
                "timestamp": datetime.now().isoformat(),
                "status": result.get("status")
            })
            
        return result
    
    def get_transaction_history(self) -> List[Dict]:
        return self.transaction_history
    
    def print_receipt(self, transaction_id: str) -> Dict:
        for transaction in self.transaction_history:
            if transaction.get("transaction_id") == transaction_id:
                return {
                    "receipt_data": transaction,
                    "terminal_id": self.terminal_id,
                    "merchant_id": self.payment_gateway.merchant_id,
                    "printed": True
                }
                
        return {"error": "Transaction not found", "printed": False}
    
    def void_transaction(self, transaction_id: str) -> Dict:
        payload = {
            "transaction_id": transaction_id,
            "terminal_id": self.terminal_id,
            "operator_id": self.operator_id
        }
        
        return self.payment_gateway._make_api_request("terminal/void", "POST", payload) 