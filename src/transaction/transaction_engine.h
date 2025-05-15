#pragma once

#include <string>
#include <vector>
#include <unordered_map>
#include <functional>
#include <chrono>

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
    );

    std::string getId() const;
    Type getType() const;
    double getAmount() const;
    std::string getCurrency() const;
    std::string getCardToken() const;
    std::string getMerchantId() const;
    Status getStatus() const;
    std::chrono::system_clock::time_point getCreatedAt() const;
    std::chrono::system_clock::time_point getProcessedAt() const;
    std::string getResponseCode() const;
    std::string getResponseMessage() const;

    void setStatus(Status newStatus);
    void setProcessedAt(std::chrono::system_clock::time_point time);
    void setResponseCode(const std::string& code);
    void setResponseMessage(const std::string& message);

    std::string toJson() const;

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

    static std::string typeToString(Type type);
    static std::string statusToString(Status status);
    static std::string timePointToString(const std::chrono::system_clock::time_point& tp);
};

class TransactionQueue {
public:
    void enqueue(const Transaction& transaction);
    bool dequeue(Transaction& transaction, int timeout_ms = 1000);
    size_t size() const;
    bool empty() const;

private:
    // Implementation details hidden
};

class TransactionRouter {
public:
    TransactionRouter();
    void addRoute(const std::string& currency, const std::string& processorId);
    void addCardBrandRoute(const std::string& cardBrand, const std::string& processorId);
    std::string getProcessorForTransaction(const Transaction& transaction);

private:
    // Implementation details hidden
    std::string extractCardBrand(const std::string& cardToken);
};

class TransactionProcessor {
public:
    using ProcessorFunction = std::function<void(Transaction&)>;

    TransactionProcessor(int numWorkers = 4);
    ~TransactionProcessor();

    void registerProcessor(const std::string& processorId, ProcessorFunction processor);
    void start();
    void stop();
    void submitTransaction(const Transaction& transaction);
    Transaction::Status getTransactionStatus(const std::string& transactionId);
    Transaction getTransactionResult(const std::string& transactionId);

private:
    // Implementation details hidden
};

class BatchProcessor {
public:
    BatchProcessor(TransactionProcessor& processor);
    ~BatchProcessor();

    void start();
    void stop();
    void addToBatch(const Transaction& transaction);
    size_t getBatchSize() const;
    void processBatchNow();
    void setAutoBatchInterval(int seconds);

private:
    // Implementation details hidden
};

// C-style interface for Python binding
extern "C" {
    void* createTransactionProcessor(int numWorkers);
    void startProcessor(void* processor);
    void stopProcessor(void* processor);
    void destroyProcessor(void* processor);
    
    char* submitTransaction(void* processor, 
                           const char* id, 
                           int type, 
                           double amount, 
                           const char* currency, 
                           const char* card_token, 
                           const char* merchant_id);
    
    char* getTransactionResult(void* processor, const char* transactionId);
    
    void* createBatchProcessor(void* processor);
    void startBatchProcessor(void* batchProcessor);
    void stopBatchProcessor(void* batchProcessor);
    void destroyBatchProcessor(void* batchProcessor);
    
    void addTransactionToBatch(void* batchProcessor, 
                              const char* id, 
                              int type, 
                              double amount, 
                              const char* currency, 
                              const char* card_token, 
                              const char* merchant_id);
    
    void processBatchNow(void* batchProcessor);
    void setBatchInterval(void* batchProcessor, int seconds);
} 