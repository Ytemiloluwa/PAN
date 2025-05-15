#include <iostream>
#include <vector>
#include <queue>
#include <unordered_map>
#include <string>
#include <chrono>
#include <thread>
#include <mutex>
#include <condition_variable>
#include <atomic>
#include <functional>
#include <random>
#include <sstream>
#include <iomanip>

class Transaction {
public:
    enum class Status {
        PENDING,
        PROCESSING,
        APPROVED,
        DECLINED,
        ERROR,
        TIMEOUT
    };

    enum class Type {
        PAYMENT,
        REFUND,
        AUTHORIZATION,
        CAPTURE,
        VOID
    };

    Transaction(
        const std::string& id,
        Type type,
        double amount,
        const std::string& currency,
        const std::string& card_token,
        const std::string& merchant_id
    ) : id(id),
        type(type),
        amount(amount),
        currency(currency),
        card_token(card_token),
        merchant_id(merchant_id),
        status(Status::PENDING),
        created_at(std::chrono::system_clock::now()),
        processed_at({}),
        response_code(""),
        response_message("") {}

    std::string getId() const { return id; }
    Type getType() const { return type; }
    double getAmount() const { return amount; }
    std::string getCurrency() const { return currency; }
    std::string getCardToken() const { return card_token; }
    std::string getMerchantId() const { return merchant_id; }
    Status getStatus() const { return status; }
    std::chrono::system_clock::time_point getCreatedAt() const { return created_at; }
    std::chrono::system_clock::time_point getProcessedAt() const { return processed_at; }
    std::string getResponseCode() const { return response_code; }
    std::string getResponseMessage() const { return response_message; }

    void setStatus(Status newStatus) { status = newStatus; }
    void setProcessedAt(std::chrono::system_clock::time_point time) { processed_at = time; }
    void setResponseCode(const std::string& code) { response_code = code; }
    void setResponseMessage(const std::string& message) { response_message = message; }

    std::string toJson() const {
        std::stringstream ss;
        ss << "{";
        ss << "\"id\":\"" << id << "\",";
        ss << "\"type\":\"" << typeToString(type) << "\",";
        ss << "\"amount\":" << std::fixed << std::setprecision(2) << amount << ",";
        ss << "\"currency\":\"" << currency << "\",";
        ss << "\"card_token\":\"" << card_token << "\",";
        ss << "\"merchant_id\":\"" << merchant_id << "\",";
        ss << "\"status\":\"" << statusToString(status) << "\",";
        ss << "\"created_at\":\"" << timePointToString(created_at) << "\",";
        
        if (status != Status::PENDING && status != Status::PROCESSING) {
            ss << "\"processed_at\":\"" << timePointToString(processed_at) << "\",";
            ss << "\"response_code\":\"" << response_code << "\",";
            ss << "\"response_message\":\"" << response_message << "\"";
        } else {
            ss << "\"processed_at\":null,";
            ss << "\"response_code\":null,";
            ss << "\"response_message\":null";
        }
        
        ss << "}";
        return ss.str();
    }

private:
    std::string id;
    Type type;
    double amount;
    std::string currency;
    std::string card_token;
    std::string merchant_id;
    Status status;
    std::chrono::system_clock::time_point created_at;
    std::chrono::system_clock::time_point processed_at;
    std::string response_code;
    std::string response_message;

    static std::string typeToString(Type type) {
        switch (type) {
            case Type::PAYMENT: return "payment";
            case Type::REFUND: return "refund";
            case Type::AUTHORIZATION: return "authorization";
            case Type::CAPTURE: return "capture";
            case Type::VOID: return "void";
            default: return "unknown";
        }
    }

    static std::string statusToString(Status status) {
        switch (status) {
            case Status::PENDING: return "pending";
            case Status::PROCESSING: return "processing";
            case Status::APPROVED: return "approved";
            case Status::DECLINED: return "declined";
            case Status::ERROR: return "error";
            case Status::TIMEOUT: return "timeout";
            default: return "unknown";
        }
    }

    static std::string timePointToString(const std::chrono::system_clock::time_point& tp) {
        auto time = std::chrono::system_clock::to_time_t(tp);
        std::stringstream ss;
        ss << std::put_time(std::localtime(&time), "%Y-%m-%dT%H:%M:%SZ");
        return ss.str();
    }
};

class TransactionQueue {
public:
    void enqueue(const Transaction& transaction) {
        std::lock_guard<std::mutex> lock(mutex);
        queue.push(transaction);
        condition.notify_one();
    }

    bool dequeue(Transaction& transaction, int timeout_ms = 1000) {
        std::unique_lock<std::mutex> lock(mutex);
        if (condition.wait_for(lock, std::chrono::milliseconds(timeout_ms), 
                              [this] { return !queue.empty(); })) {
            transaction = queue.front();
            queue.pop();
            return true;
        }
        return false;
    }

    size_t size() const {
        std::lock_guard<std::mutex> lock(mutex);
        return queue.size();
    }

    bool empty() const {
        std::lock_guard<std::mutex> lock(mutex);
        return queue.empty();
    }

private:
    std::queue<Transaction> queue;
    mutable std::mutex mutex;
    std::condition_variable condition;
};

class TransactionRouter {
public:
    TransactionRouter() {}

    void addRoute(const std::string& currency, const std::string& processorId) {
        std::lock_guard<std::mutex> lock(mutex);
        currencyRoutes[currency] = processorId;
    }

    void addCardBrandRoute(const std::string& cardBrand, const std::string& processorId) {
        std::lock_guard<std::mutex> lock(mutex);
        cardBrandRoutes[cardBrand] = processorId;
    }

    std::string getProcessorForTransaction(const Transaction& transaction) {
        std::lock_guard<std::mutex> lock(mutex);
        
        // First try to route by currency
        auto currencyIt = currencyRoutes.find(transaction.getCurrency());
        if (currencyIt != currencyRoutes.end()) {
            return currencyIt->second;
        }
        
        // Then try to route by card brand (would need to extract from token in real implementation)
        std::string cardBrand = extractCardBrand(transaction.getCardToken());
        auto brandIt = cardBrandRoutes.find(cardBrand);
        if (brandIt != cardBrandRoutes.end()) {
            return brandIt->second;
        }
        
        // Default processor
        return "default-processor";
    }

private:
    std::unordered_map<std::string, std::string> currencyRoutes;
    std::unordered_map<std::string, std::string> cardBrandRoutes;
    std::mutex mutex;

    std::string extractCardBrand(const std::string& cardToken) {
        // In a real implementation, this would decode the token or use a lookup
        // For this example, we'll just return a placeholder
        if (cardToken.find("visa") != std::string::npos) {
            return "visa";
        } else if (cardToken.find("mc") != std::string::npos) {
            return "mastercard";
        } else if (cardToken.find("amex") != std::string::npos) {
            return "amex";
        }
        return "unknown";
    }
};

class TransactionProcessor {
public:
    using ProcessorFunction = std::function<void(Transaction&)>;

    TransactionProcessor(int numWorkers = 4) 
        : running(false), numWorkers(numWorkers) {
        setupDefaultProcessors();
    }

    ~TransactionProcessor() {
        stop();
    }

    void registerProcessor(const std::string& processorId, ProcessorFunction processor) {
        std::lock_guard<std::mutex> lock(mutex);
        processors[processorId] = processor;
    }

    void start() {
        std::lock_guard<std::mutex> lock(mutex);
        if (running) return;
        
        running = true;
        for (int i = 0; i < numWorkers; ++i) {
            workers.push_back(std::thread(&TransactionProcessor::workerThread, this));
        }
    }

    void stop() {
        {
            std::lock_guard<std::mutex> lock(mutex);
            if (!running) return;
            running = false;
        }
        
        condition.notify_all();
        for (auto& worker : workers) {
            if (worker.joinable()) {
                worker.join();
            }
        }
        workers.clear();
    }

    void submitTransaction(const Transaction& transaction) {
        pendingQueue.enqueue(transaction);
    }

    Transaction::Status getTransactionStatus(const std::string& transactionId) {
        std::lock_guard<std::mutex> lock(mutex);
        auto it = transactionResults.find(transactionId);
        if (it != transactionResults.end()) {
            return it->second.getStatus();
        }
        return Transaction::Status::PENDING;
    }

    Transaction getTransactionResult(const std::string& transactionId) {
        std::lock_guard<std::mutex> lock(mutex);
        auto it = transactionResults.find(transactionId);
        if (it != transactionResults.end()) {
            return it->second;
        }
        
        // Return an empty transaction if not found
        return Transaction("", Transaction::Type::PAYMENT, 0.0, "", "", "");
    }

private:
    TransactionQueue pendingQueue;
    std::atomic<bool> running;
    std::vector<std::thread> workers;
    int numWorkers;
    std::mutex mutex;
    std::condition_variable condition;
    std::unordered_map<std::string, ProcessorFunction> processors;
    std::unordered_map<std::string, Transaction> transactionResults;
    TransactionRouter router;

    void setupDefaultProcessors() {
        // Default processor
        registerProcessor("default-processor", [this](Transaction& tx) {
            processDefaultTransaction(tx);
        });
        
        // Visa processor
        registerProcessor("visa-processor", [this](Transaction& tx) {
            processVisaTransaction(tx);
        });
        
        // Mastercard processor
        registerProcessor("mastercard-processor", [this](Transaction& tx) {
            processMastercardTransaction(tx);
        });
        
        // Set up routing
        router.addCardBrandRoute("visa", "visa-processor");
        router.addCardBrandRoute("mastercard", "mastercard-processor");
        router.addCurrencyRoute("EUR", "european-processor");
        router.addCurrencyRoute("GBP", "european-processor");
    }

    void workerThread() {
        while (running) {
            Transaction transaction;
            if (pendingQueue.dequeue(transaction, 100)) {
                processTransaction(transaction);
            }
        }
    }

    void processTransaction(Transaction& transaction) {
        transaction.setStatus(Transaction::Status::PROCESSING);
        
        std::string processorId = router.getProcessorForTransaction(transaction);
        
        std::lock_guard<std::mutex> lock(mutex);
        auto processorIt = processors.find(processorId);
        if (processorIt != processors.end()) {
            processorIt->second(transaction);
        } else {
            // Fall back to default processor
            processors["default-processor"](transaction);
        }
        
        // Store the result
        transaction.setProcessedAt(std::chrono::system_clock::now());
        transactionResults[transaction.getId()] = transaction;
    }

    // Sample processor implementations
    void processDefaultTransaction(Transaction& tx) {
        // Simulate processing time
        std::this_thread::sleep_for(std::chrono::milliseconds(50 + rand() % 200));
        
        // Simple approval logic based on amount
        if (tx.getAmount() < 10000.0) {
            tx.setStatus(Transaction::Status::APPROVED);
            tx.setResponseCode("00");
            tx.setResponseMessage("Approved");
        } else {
            tx.setStatus(Transaction::Status::DECLINED);
            tx.setResponseCode("51");
            tx.setResponseMessage("Insufficient funds");
        }
    }

    void processVisaTransaction(Transaction& tx) {
        // Simulate Visa specific processing
        std::this_thread::sleep_for(std::chrono::milliseconds(30 + rand() % 100));
        
        // Approve most transactions
        if (rand() % 100 < 95) {
            tx.setStatus(Transaction::Status::APPROVED);
            tx.setResponseCode("00");
            tx.setResponseMessage("Approved by Visa");
        } else {
            tx.setStatus(Transaction::Status::DECLINED);
            tx.setResponseCode("05");
            tx.setResponseMessage("Do not honor");
        }
    }

    void processMastercardTransaction(Transaction& tx) {
        // Simulate Mastercard specific processing
        std::this_thread::sleep_for(std::chrono::milliseconds(40 + rand() % 150));
        
        // Approve most transactions
        if (rand() % 100 < 92) {
            tx.setStatus(Transaction::Status::APPROVED);
            tx.setResponseCode("00");
            tx.setResponseMessage("Approved by Mastercard");
        } else {
            tx.setStatus(Transaction::Status::DECLINED);
            tx.setResponseCode("54");
            tx.setResponseMessage("Expired card");
        }
    }
};

class BatchProcessor {
public:
    BatchProcessor(TransactionProcessor& processor) 
        : transactionProcessor(processor), running(false) {}

    ~BatchProcessor() {
        stop();
    }

    void start() {
        std::lock_guard<std::mutex> lock(mutex);
        if (running) return;
        
        running = true;
        batchThread = std::thread(&BatchProcessor::batchProcessingThread, this);
    }

    void stop() {
        {
            std::lock_guard<std::mutex> lock(mutex);
            if (!running) return;
            running = false;
        }
        
        condition.notify_all();
        if (batchThread.joinable()) {
            batchThread.join();
        }
    }

    void addToBatch(const Transaction& transaction) {
        std::lock_guard<std::mutex> lock(mutex);
        batchQueue.push_back(transaction);
    }

    size_t getBatchSize() const {
        std::lock_guard<std::mutex> lock(mutex);
        return batchQueue.size();
    }

    void processBatchNow() {
        std::lock_guard<std::mutex> lock(mutex);
        processBatch();
    }

    void setAutoBatchInterval(int seconds) {
        std::lock_guard<std::mutex> lock(mutex);
        batchIntervalSeconds = seconds;
    }

private:
    TransactionProcessor& transactionProcessor;
    std::vector<Transaction> batchQueue;
    std::atomic<bool> running;
    std::thread batchThread;
    mutable std::mutex mutex;
    std::condition_variable condition;
    int batchIntervalSeconds = 60;  // Default to 60 seconds

    void batchProcessingThread() {
        while (running) {
            std::unique_lock<std::mutex> lock(mutex);
            if (condition.wait_for(lock, std::chrono::seconds(batchIntervalSeconds), 
                                  [this] { return !running; })) {
                // If we were woken up because we're stopping, exit
                break;
            }
            
            // Process the batch
            processBatch();
        }
    }

    void processBatch() {
        if (batchQueue.empty()) return;
        
        std::cout << "Processing batch of " << batchQueue.size() << " transactions" << std::endl;
        
        for (const auto& transaction : batchQueue) {
            transactionProcessor.submitTransaction(transaction);
        }
        
        batchQueue.clear();
    }
};

// Main function to demonstrate usage
int main() {
    // Create transaction processor with 4 worker threads
    TransactionProcessor processor(4);
    processor.start();
    
    // Create batch processor
    BatchProcessor batchProcessor(processor);
    batchProcessor.setAutoBatchInterval(30);  // Process batch every 30 seconds
    batchProcessor.start();
    
    // Create some sample transactions
    std::vector<Transaction> transactions;
    for (int i = 0; i < 10; ++i) {
        std::string id = "tx-" + std::to_string(i);
        double amount = 100.0 + (i * 50.0);
        std::string currency = (i % 2 == 0) ? "USD" : "EUR";
        std::string cardToken = (i % 3 == 0) ? "visa-token" : "mc-token";
        
        transactions.push_back(Transaction(
            id,
            Transaction::Type::PAYMENT,
            amount,
            currency,
            cardToken,
            "merchant-123"
        ));
    }
    
    // Submit transactions directly
    for (int i = 0; i < 5; ++i) {
        processor.submitTransaction(transactions[i]);
        std::cout << "Submitted transaction " << transactions[i].getId() << " for direct processing" << std::endl;
    }
    
    // Add transactions to batch
    for (int i = 5; i < 10; ++i) {
        batchProcessor.addToBatch(transactions[i]);
        std::cout << "Added transaction " << transactions[i].getId() << " to batch" << std::endl;
    }
    
    // Process the batch immediately instead of waiting
    std::cout << "Processing batch now..." << std::endl;
    batchProcessor.processBatchNow();
    
    // Wait for processing to complete
    std::this_thread::sleep_for(std::chrono::seconds(2));
    
    // Check results
    for (const auto& tx : transactions) {
        Transaction result = processor.getTransactionResult(tx.getId());
        std::cout << "Transaction " << tx.getId() << " status: " 
                  << static_cast<int>(result.getStatus()) << std::endl;
        std::cout << "JSON: " << result.toJson() << std::endl;
    }
    
    // Clean up
    batchProcessor.stop();
    processor.stop();
    
    return 0;
} 