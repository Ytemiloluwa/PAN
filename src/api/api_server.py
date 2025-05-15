from flask import Flask, request, jsonify
import os
import json
from src.payment.payment_processor import PaymentProcessor

app = Flask(__name__)

# Initialize payment processor
processor = PaymentProcessor(
    api_key=os.environ.get("API_KEY", "test_api_key"),
    merchant_id=os.environ.get("MERCHANT_ID", "test_merchant"),
    environment=os.environ.get("ENVIRONMENT", "test")
)

@app.route("/health", methods=["GET"])
def health_check():
    return jsonify({"status": "ok"})

@app.route("/payments", methods=["POST"])
def create_payment():
    data = request.json
    
    if not data:
        return jsonify({"error": "Invalid request data"}), 400
    
    card_data = data.get("card")
    amount = data.get("amount")
    currency = data.get("currency", "USD")
    customer_info = data.get("customer")
    metadata = data.get("metadata")
    batch = data.get("batch", False)
    
    if not card_data or not amount:
        return jsonify({"error": "Missing required fields"}), 400
    
    result = processor.process_payment(
        card_data=card_data,
        amount=amount,
        currency=currency,
        customer_info=customer_info,
        metadata=metadata,
        batch=batch
    )
    
    return jsonify(result)

@app.route("/payments/<transaction_id>", methods=["GET"])
def get_payment_status(transaction_id):
    result = processor.check_transaction_status(transaction_id)
    return jsonify(result)

@app.route("/batch/process", methods=["POST"])
def process_batch():
    result = processor.process_batch_now()
    return jsonify(result)

@app.route("/payment-links", methods=["POST"])
def create_payment_link():
    data = request.json
    
    if not data:
        return jsonify({"error": "Invalid request data"}), 400
    
    amount = data.get("amount")
    currency = data.get("currency", "USD")
    description = data.get("description", "")
    success_url = data.get("success_url")
    cancel_url = data.get("cancel_url")
    
    if not amount:
        return jsonify({"error": "Missing required fields"}), 400
    
    result = processor.create_payment_link(
        amount=amount,
        currency=currency,
        description=description,
        success_url=success_url,
        cancel_url=cancel_url
    )
    
    return jsonify(result)

@app.route("/checkout/session", methods=["POST"])
def create_checkout_session():
    data = request.json
    
    if not data:
        return jsonify({"error": "Invalid request data"}), 400
    
    items = data.get("items")
    currency = data.get("currency", "USD")
    success_url = data.get("success_url")
    cancel_url = data.get("cancel_url")
    
    if not items:
        return jsonify({"error": "Missing required fields"}), 400
    
    result = processor.create_checkout_session(
        items=items,
        currency=currency,
        success_url=success_url,
        cancel_url=cancel_url
    )
    
    return jsonify(result)

@app.route("/currencies", methods=["GET"])
def get_currencies():
    currencies = processor.get_supported_currencies()
    return jsonify(currencies)

@app.route("/currencies/convert", methods=["POST"])
def convert_currency():
    data = request.json
    
    if not data:
        return jsonify({"error": "Invalid request data"}), 400
    
    amount = data.get("amount")
    from_currency = data.get("from")
    to_currency = data.get("to")
    
    if not amount or not from_currency or not to_currency:
        return jsonify({"error": "Missing required fields"}), 400
    
    result = processor.convert_currency(
        amount=amount,
        from_currency=from_currency,
        to_currency=to_currency
    )
    
    return jsonify(result)

@app.route("/virtual-terminal/initialize", methods=["POST"])
def initialize_virtual_terminal():
    data = request.json
    
    if not data:
        return jsonify({"error": "Invalid request data"}), 400
    
    terminal_id = data.get("terminal_id")
    operator_id = data.get("operator_id")
    
    if not terminal_id:
        return jsonify({"error": "Missing required fields"}), 400
    
    terminal = processor.create_virtual_terminal(terminal_id, operator_id)
    
    return jsonify({
        "terminal_id": terminal_id,
        "operator_id": operator_id,
        "status": "initialized"
    })

@app.route("/virtual-terminal/process", methods=["POST"])
def process_virtual_terminal_payment():
    data = request.json
    
    if not data:
        return jsonify({"error": "Invalid request data"}), 400
    
    terminal_id = data.get("terminal_id")
    card_data = data.get("card")
    amount = data.get("amount")
    currency = data.get("currency", "USD")
    operator_id = data.get("operator_id")
    
    if not terminal_id or not card_data or not amount:
        return jsonify({"error": "Missing required fields"}), 400
    
    terminal = processor.create_virtual_terminal(terminal_id, operator_id)
    result = terminal.process_payment(card_data, amount, currency)
    
    return jsonify(result)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=os.environ.get("DEBUG", False)) 