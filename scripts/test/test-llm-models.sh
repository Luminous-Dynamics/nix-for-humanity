#!/usr/bin/env bash

# Test different LLM models for Nix for Humanity
# Helps find the best model for your system

set -euo pipefail

echo "🧪 Nix for Humanity - LLM Model Tester"
echo "======================================"
echo

# Test question for NixOS expertise
TEST_QUESTION="How do I create a declarative systemd service in NixOS that runs a Python script at startup?"

# Models to test (in order of size)
MODELS=(
    "mistral:7b"
    "deepseek-coder:6.7b"
    "codellama:7b-instruct"
    "wizardcoder:7b"
    "llama2:13b"
    "codellama:13b-instruct"
    "mixtral:8x7b-instruct"
)

# Function to test a model
test_model() {
    local model=$1
    echo "📊 Testing model: $model"
    echo "------------------------"
    
    # Check if model exists
    if ! ollama list | grep -q "$model"; then
        echo "⚠️  Model not installed. Pulling $model..."
        if ! ollama pull "$model"; then
            echo "❌ Failed to pull $model. Skipping."
            echo
            return 1
        fi
    fi
    
    # Measure response time
    local start_time=$(date +%s.%N)
    
    # Run the test
    echo "🤔 Asking: $TEST_QUESTION"
    echo
    
    response=$(ollama run "$model" "$TEST_QUESTION" 2>/dev/null || echo "Error getting response")
    
    local end_time=$(date +%s.%N)
    local duration=$(echo "$end_time - $start_time" | bc)
    
    echo "📝 Response:"
    echo "$response" | head -20
    echo "..."
    echo
    echo "⏱️  Response time: ${duration}s"
    echo
    
    # Save results
    mkdir -p test-results
    {
        echo "Model: $model"
        echo "Question: $TEST_QUESTION"
        echo "Response time: ${duration}s"
        echo "---"
        echo "$response"
        echo
    } > "test-results/${model//://}.txt"
    
    # Ask for quality rating
    read -p "Rate response quality (1-5, 5 being best): " rating
    echo "Rating: $rating/5" >> "test-results/${model//://}.txt"
    echo
    
    return 0
}

# Main menu
show_menu() {
    echo "Choose testing mode:"
    echo "1. Quick test (small models only)"
    echo "2. Full test (all models)"
    echo "3. Test specific model"
    echo "4. Compare results"
    echo "5. Exit"
    echo
}

# Quick test function
quick_test() {
    echo "🚀 Running quick test with small models..."
    for model in "mistral:7b" "deepseek-coder:6.7b" "codellama:7b-instruct"; do
        if test_model "$model"; then
            echo "✅ Completed: $model"
        fi
        echo "Press Enter to continue to next model..."
        read
    done
}

# Full test function
full_test() {
    echo "🔬 Running full test with all models..."
    echo "⚠️  This may take a while and require significant disk space."
    read -p "Continue? (y/n): " confirm
    
    if [[ "$confirm" == "y" ]]; then
        for model in "${MODELS[@]}"; do
            if test_model "$model"; then
                echo "✅ Completed: $model"
            fi
            echo "Press Enter to continue to next model..."
            read
        done
    fi
}

# Test specific model
test_specific() {
    echo "Available models:"
    for i in "${!MODELS[@]}"; do
        echo "$((i+1)). ${MODELS[$i]}"
    done
    echo
    read -p "Select model number: " choice
    
    if [[ "$choice" -ge 1 && "$choice" -le "${#MODELS[@]}" ]]; then
        model="${MODELS[$((choice-1))]}"
        test_model "$model"
    else
        echo "Invalid choice"
    fi
}

# Compare results
compare_results() {
    echo "📊 Model Comparison Results"
    echo "=========================="
    echo
    
    if [ -d "test-results" ]; then
        for file in test-results/*.txt; do
            if [ -f "$file" ]; then
                echo "--- $(basename "$file" .txt) ---"
                grep -E "Response time:|Rating:" "$file" || echo "No data"
                echo
            fi
        done
    else
        echo "No test results found. Run some tests first!"
    fi
}

# Main loop
while true; do
    show_menu
    read -p "Choice: " choice
    
    case $choice in
        1) quick_test ;;
        2) full_test ;;
        3) test_specific ;;
        4) compare_results ;;
        5) 
            echo "👋 Goodbye!"
            exit 0
            ;;
        *)
            echo "Invalid choice. Please try again."
            ;;
    esac
    
    echo
    read -p "Press Enter to return to menu..."
    clear
done