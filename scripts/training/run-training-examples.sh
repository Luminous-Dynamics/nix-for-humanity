#!/usr/bin/env bash
# Example commands for running the NixOS documentation training pipeline

# Exit on error
set -e

echo "🎓 NixOS Documentation Training Pipeline - Example Commands"
echo "========================================================="
echo ""

# Color codes for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored headers
print_header() {
    echo -e "\n${BLUE}=== $1 ===${NC}\n"
}

# Function to print commands
print_command() {
    echo -e "${GREEN}$ $1${NC}"
}

# Check if in project directory
if [[ ! -f "train-nixos-expert.py" ]]; then
    echo -e "${YELLOW}Warning: Not in scripts directory. Please cd to the scripts directory first.${NC}"
    echo "cd /srv/luminous-dynamics/11-meta-consciousness/nix-for-humanity/scripts"
    exit 1
fi

print_header "1. Setup Environment"
print_command "pip install -r requirements.txt"
echo "Installs all required Python packages"

print_header "2. Quick Test Run"
print_command "python3 train-nixos-expert.py --test-mode"
echo "Runs the pipeline with a small test dataset to verify everything works"

print_header "3. Full Training Pipeline"
print_command "python3 train-nixos-expert.py"
echo "Runs the complete pipeline: scrape → process → format → create model"

print_header "4. Skip Scraping (Use Existing Data)"
print_command "python3 train-nixos-expert.py --skip-scraping"
echo "Useful when you already have scraped data and want to reprocess"

print_header "5. Use Different Base Model"
print_command "python3 train-nixos-expert.py --base-model codellama:13b --model-name nixos-coder"
echo "Uses CodeLlama 13B instead of Mistral 7B for code-focused training"

print_header "6. Individual Steps"
echo "You can also run each step separately:"
echo ""

print_command "# Step 1: Scrape documentation"
print_command "python3 scrape-nixos-docs.py --max-pages 50"
echo ""

print_command "# Step 2: Process into Q&A pairs"
print_command "python3 process-training-data.py --quality high"
echo ""

print_command "# Step 3: Format for training"
print_command "python3 format-for-training.py --formats alpaca,sharegpt"
echo ""

print_command "# Step 4: Create Ollama model"
print_command "ollama create nixos-expert -f training-data/formatted/nixos_expert.modelfile"

print_header "7. Test the Trained Model"
print_command "ollama run nixos-expert"
echo "Then ask questions like:"
echo "  - How do I install packages in NixOS?"
echo "  - What is a flake?"
echo "  - How do I update my system?"

print_header "8. Run Test Suite"
print_command "python3 test-training-pipeline.py -v"
echo "Runs all tests with verbose output"

print_header "9. Clean Up Training Data"
print_command "rm -rf training-data/"
echo "Removes all scraped and processed data (be careful!)"

print_header "10. Advanced: Custom Sources"
echo "Edit scrape-nixos-docs.py to add custom documentation sources:"
echo ""
cat << 'EOF'
SOURCES = {
    'custom': {
        'base_url': 'https://your-site.com',
        'paths': ['/docs/'],
        'selector': 'article.content'
    }
}
EOF

print_header "Tips"
echo "• Start with --test-mode to verify setup"
echo "• Use --skip-scraping to save time during development"
echo "• Monitor training-data/ directory size"
echo "• Check ollama list to see your models"
echo "• Use ollama rm model-name to remove models"

echo -e "\n${YELLOW}Ready to train your NixOS expert model? Start with example #2 (Quick Test Run)!${NC}\n"