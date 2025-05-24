import ctypes
import json
import os
import uuid
from enum import Enum
from typing import Dict


class TransactionType(Enum):
    PAYMENT = 0
    REFUND = 1
    AUTHORIZATION = 2
    CAPTURE = 3
    VOID = 4


class TransactionStatus(Enum):
    PENDING = 0
    PROCESSING = 1
    APPROVED = 2
    DECLINED = 3
    ERROR = 4
    TIMEOUT = 5


class Transaction:
    def __init__(self, 
                 id: str = None,
                 type: TransactionType = TransactionType.PAYMENT,
                 amount: float = 0.0,
                 currency: str = "USD",
                 card_token: str = "",
                 merchant_id: str = ""):
        self.id = id or f"tx-{uuid.uuid4().hex}"
        self.type = type
        self.amount = amount
        self.currency = currency
        self.card_token = card_token
        self.merchant_id = merchant_id
        self.status = TransactionStatus.PENDING
        self.response_code = None
        self.response_message = None
        self.created_at = None
        self.processed_at = None
    
    @classmethod
    def from_json(cls, json_str: str) -> 'Transaction':
        data = json.loads(json_str)
        tx = cls(
            id=data.get('id'),
            type=TransactionType[data.get('type', 'PAYMENT').upper()],
            amount=data.get('amount', 0.0),
            currency=data.get('currency', 'USD'),
            card_token=data.get('card_token', ''),
            merchant_id=data.get('merchant_id', '')
        )
        
        tx.status = TransactionStatus[data.get('status', 'PENDING').upper()]
        tx.response_code = data.get('response_code')
        tx.response_message = data.get('response_message')
        tx.created_at = data.get('created_at')
        tx.processed_at = data.get('processed_at')
        
        return tx
    
    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'type': self.type.name.lower(),
            'amount': self.amount,
            'currency': self.currency,
            'card_token': self.card_token,
            'merchant_id': self.merchant_id,
            'status': self.status.name.lower(),
            'response_code': self.response_code,
            'response_message': self.response_message,
            'created_at': self.created_at,
            'processed_at': self.processed_at
        }


class TransactionEngine:
    def __init__(self, num_workers: int = 4):
        lib_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "lib", "libtransaction_engine.so"))
        self._lib = ctypes.CDLL(lib_path)
        
        # Set up function signatures
        self._lib.createTransactionProcessor.argtypes = [ctypes.c_int]
        self._lib.createTransactionProcessor.restype = ctypes.c_void_p
        
        self._lib.startProcessor.argtypes = [ctypes.c_void_p]
        self._lib.stopProcessor.argtypes = [ctypes.c_void_p]
        self._lib.destroyProcessor.argtypes = [ctypes.c_void_p]
        
        self._lib.submitTransaction.argtypes = [
            ctypes.c_void_p, 
            ctypes.c_char_p, 
            ctypes.c_int, 
            ctypes.c_double, 
            ctypes.c_char_p, 
            ctypes.c_char_p, 
            ctypes.c_char_p
        ]
        self._lib.submitTransaction.restype = ctypes.c_char_p
        
        self._lib.getTransactionResult.argtypes = [ctypes.c_void_p, ctypes.c_char_p]
        self._lib.getTransactionResult.restype = ctypes.c_char_p
        
        # Initialize the processor
        self._processor = self._lib.createTransactionProcessor(num_workers)
        self._lib.startProcessor(self._processor)
    
    def __del__(self):
        if hasattr(self, '_processor') and self._processor:
            self._lib.stopProcessor(self._processor)
            self._lib.destroyProcessor(self._processor)
    
    def submit_transaction(self, transaction: Transaction) -> str:
        result = self._lib.submitTransaction(
            self._processor,
            transaction.id.encode('utf-8'),
            transaction.type.value,
            transaction.amount,
            transaction.currency.encode('utf-8'),
            transaction.card_token.encode('utf-8'),
            transaction.merchant_id.encode('utf-8')
        )
        
        return result.decode('utf-8')
    
    def get_transaction_result(self, transaction_id: str) -> Transaction:
        result = self._lib.getTransactionResult(
            self._processor,
            transaction_id.encode('utf-8')
        )
        
        json_str = result.decode('utf-8')
        return Transaction.from_json(json_str)


class BatchProcessor:
    def __init__(self, transaction_engine: TransactionEngine):
        self._engine = transaction_engine
        self._lib = transaction_engine._lib
        
        # Set up function signatures
        self._lib.createBatchProcessor.argtypes = [ctypes.c_void_p]
        self._lib.createBatchProcessor.restype = ctypes.c_void_p
        
        self._lib.startBatchProcessor.argtypes = [ctypes.c_void_p]
        self._lib.stopBatchProcessor.argtypes = [ctypes.c_void_p]
        self._lib.destroyBatchProcessor.argtypes = [ctypes.c_void_p]
        
        self._lib.addTransactionToBatch.argtypes = [
            ctypes.c_void_p, 
            ctypes.c_char_p, 
            ctypes.c_int, 
            ctypes.c_double, 
            ctypes.c_char_p, 
            ctypes.c_char_p, 
            ctypes.c_char_p
        ]
        
        self._lib.processBatchNow.argtypes = [ctypes.c_void_p]
        self._lib.setBatchInterval.argtypes = [ctypes.c_void_p, ctypes.c_int]
        
        # Initialize the batch processor
        self._processor = self._lib.createBatchProcessor(transaction_engine._processor)
        self._lib.startBatchProcessor(self._processor)
    
    def __del__(self):
        if hasattr(self, '_processor') and self._processor:
            self._lib.stopBatchProcessor(self._processor)
            self._lib.destroyBatchProcessor(self._processor)
    
    def add_transaction(self, transaction: Transaction):
        self._lib.addTransactionToBatch(
            self._processor,
            transaction.id.encode('utf-8'),
            transaction.type.value,
            transaction.amount,
            transaction.currency.encode('utf-8'),
            transaction.card_token.encode('utf-8'),
            transaction.merchant_id.encode('utf-8')
        )
    
    def process_batch_now(self):
        self._lib.processBatchNow(self._processor)
    
    def set_batch_interval(self, seconds: int):
        self._lib.setBatchInterval(self._processor, seconds)


if __name__ == "__main__":
    # Create transaction engine
    engine = TransactionEngine(num_workers=4)
    
    # Create batch processor
    batch = BatchProcessor(engine)
    batch.set_batch_interval(30)  # Process batch every 30 seconds
    
    # Create a transaction
    tx = Transaction(
        amount=100.0,
        currency="USD",
        card_token="visa-token-1234",
        merchant_id="merchant-123"
    )

    engine.submit_transaction(tx)
    
    # Create another transaction for batch processing
    tx2 = Transaction(
        amount=200.0,
        currency="EUR",
        card_token="mc-token-5678",
        merchant_id="merchant-123"
    )
    
    # Add to batch
    batch.add_transaction(tx2)
    
    # Process batch now
    batch.process_batch_now()
    
    # Get results
    result1 = engine.get_transaction_result(tx.id)
    result2 = engine.get_transaction_result(tx2.id)
    
    print(f"Transaction 1 status: {result1.status}")
    print(f"Transaction 2 status: {result2.status}") 