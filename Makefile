.PHONY: all clean build run test install

CXX = g++
CXXFLAGS = -std=c++17 -O2 -Wall -fPIC
LDFLAGS = -shared -pthread

# Directories
SRC_DIR = src/transaction
BUILD_DIR = build
LIB_DIR = lib

# Source files
CPP_SRCS = $(SRC_DIR)/transaction_engine.cpp
CPP_OBJS = $(patsubst $(SRC_DIR)/%.cpp,$(BUILD_DIR)/%.o,$(CPP_SRCS))
LIB_TARGET = $(LIB_DIR)/libtransaction_engine.so

# Python files
PY_SRCS = src/api/api_server.py src/payment/payment_processor.py src/transaction/transaction_engine_wrapper.py src/payment/payment_gateway.py

# Default target
all: build

# Create directories
$(BUILD_DIR):
	mkdir -p $(BUILD_DIR)

$(LIB_DIR):
	mkdir -p $(LIB_DIR)

# Compile C++ source files
$(BUILD_DIR)/%.o: $(SRC_DIR)/%.cpp | $(BUILD_DIR)
	$(CXX) $(CXXFLAGS) -c $< -o $@

# Link shared library
$(LIB_TARGET): $(CPP_OBJS) | $(LIB_DIR)
	$(CXX) $(LDFLAGS) -o $@ $^

# Build target
build: $(LIB_TARGET)

# Install Python dependencies
install:
	pip install -r requirements.txt

# Run the API server
run: build install
	PYTHONPATH=. python -m src.api.api_server

# Run tests
test: build install
	PYTHONPATH=. python -m unittest discover -s tests

# Clean build artifacts
clean:
	rm -rf $(BUILD_DIR) $(LIB_DIR)

# Generate requirements.txt
requirements:
	pip freeze > requirements.txt 