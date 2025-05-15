import json
import uuid
from typing import Dict, List
from src.payment.payment_gateway import PaymentGateway, VirtualTerminal, ECommerceAPI
from src.transaction.transaction_engine_wrapper import TransactionEngine, BatchProcessor, Transaction, TransactionType


class PaymentProcessor:
    def __init__(self, 
                 api_key: str, 
                 merchant_id: str, 
                 environment: str = "test",
                 num_workers: int = 4):
        self.payment_gateway = PaymentGateway(api_key, merchant_id, environment)
        self.transaction_engine = TransactionEngine(num_workers)
        self.batch_processor = BatchProcessor(self.transaction_engine)
        self.batch_processor.set_batch_interval(60)  # Process batch every minute
        
        # Initialize E-commerce API
        self.ecommerce_api = ECommerceAPI(self.payment_gateway)
        
        # Track local transactions
        self.transactions = {}
    
    def process_payment(self, 
                      card_data: Dict, 
                      amount: float, 
                      currency: str = "USD",
                      customer_info: Dict = None,
                      metadata: Dict = None,
                      batch: bool = False) -> Dict:
        # Generate transaction ID
        transaction_id = f"tx-{uuid.uuid4().hex}"
        
        # Create transaction object for the engine
        tx = Transaction(
            id=transaction_id,
            type=TransactionType.PAYMENT,
            amount=amount,
            currency=currency,
            card_token=json.dumps(card_data),  # Serialize card data as token
            merchant_id=self.payment_gateway.merchant_id
        )
        
        # Store transaction for reference
        self.transactions[transaction_id] = tx
        
        # Submit to transaction engine
        if batch:
            self.batch_processor.add_transaction(tx)
            status = "queued_for_batch"
        else:
            self.transaction_engine.submit_transaction(tx)
            status = "processing"
        
        # Return immediate response
        return {
            "transaction_id": transaction_id,
            "status": status,
            "amount": amount,
            "currency": currency
        }
    
    def check_transaction_status(self, transaction_id: str) -> Dict:
        # Get transaction from engine
        tx_result = self.transaction_engine.get_transaction_result(transaction_id)
        
        if tx_result.status.name == "APPROVED":
            # If approved, process through payment gateway
            card_data = json.loads(tx_result.card_token)
            
            gateway_result = self.payment_gateway.process_card_payment(
                card_data=card_data,
                amount=tx_result.amount,
                currency=tx_result.currency,
                metadata={"transaction_id": transaction_id}
            )
            
            return {
                "transaction_id": transaction_id,
                "status": "approved",
                "gateway_reference": gateway_result.get("reference_id", ""),
                "amount": tx_result.amount,
                "currency": tx_result.currency,
                "response_code": tx_result.response_code,
                "response_message": tx_result.response_message
            }
        
        return {
            "transaction_id": transaction_id,
            "status": tx_result.status.name.lower(),
            "amount": tx_result.amount,
            "currency": tx_result.currency,
            "response_code": tx_result.response_code,
            "response_message": tx_result.response_message
        }
    
    def process_batch_now(self) -> Dict:
        self.batch_processor.process_batch_now()
        return {"status": "batch_processing_started"}
    
    def create_virtual_terminal(self, terminal_id: str, operator_id: str = None) -> VirtualTerminal:
        return VirtualTerminal(self.payment_gateway, terminal_id, operator_id)
    
    def create_payment_link(self, 
                          amount: float, 
                          currency: str = "USD",
                          description: str = "",
                          success_url: str = None,
                          cancel_url: str = None) -> Dict:
        return self.payment_gateway.create_payment_link(
            amount=amount,
            currency=currency,
            description=description,
            success_url=success_url,
            cancel_url=cancel_url
        )
    
    def create_checkout_session(self, 
                              items: List[Dict],
                              currency: str = "USD",
                              success_url: str = None,
                              cancel_url: str = None) -> Dict:
        return self.ecommerce_api.create_checkout_session(
            items=items,
            currency=currency,
            success_url=success_url,
            cancel_url=cancel_url
        )
    
    def convert_currency(self, 
                       amount: float, 
                       from_currency: str, 
                       to_currency: str) -> Dict:
        return self.payment_gateway.convert_amount(
            amount=amount,
            from_currency=from_currency,
            to_currency=to_currency
        )
    
    def get_supported_currencies(self) -> List[Dict]:
        return self.payment_gateway.get_supported_currencies()

# Example usage
if __name__ == "__main__":
    processor = PaymentProcessor(
        api_key="test_api_key",
        merchant_id="test_merchant",
        environment="test"
    )
    
    # Process a payment
    card_data = {
        "number": "4111111111111111",
        "expiry_month": "12",
        "expiry_year": "2025",
        "cvv": "123",
        "cardholder_name": "Test Customer"
    }
    
    result = processor.process_payment(
        card_data=card_data,
        amount=100.0,
        currency="USD",
        customer_info={"email": "customer@example.com"}
    )
    
    print(f"Payment initiated: {result}")
    
    # Check status
    status = processor.check_transaction_status(result["transaction_id"])
    print(f"Payment status: {status}")
    
    # Process a batch payment
    batch_result = processor.process_payment(
        card_data=card_data,
        amount=200.0,
        currency="EUR",
        batch=True
    )
    
    print(f"Batch payment queued: {batch_result}")
    
    # Process batch now
    processor.process_batch_now()
    
    # Check batch payment status
    batch_status = processor.check_transaction_status(batch_result["transaction_id"])
    print(f"Batch payment status: {batch_status}")
    
    # Create a payment link
    link = processor.create_payment_link(
        amount=150.0,
        currency="USD",
        description="Test payment"
    )
    
    print(f"Payment link: {link}")
    
    # Get supported currencies
    currencies = processor.get_supported_currencies()
    print(f"Supported currencies: {currencies}") 