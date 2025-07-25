# NixOS GUI Makefile
# Simplifies common development tasks

.PHONY: help dev test build clean install shell ssl-cert python-server all-tests security-test

# Default target
help:
	@echo "NixOS GUI Development Commands"
	@echo "=============================="
	@echo "make install      - Install dependencies"
	@echo "make dev          - Start development server"
	@echo "make test         - Run test suite"
	@echo "make build        - Build for production"
	@echo "make clean        - Clean build artifacts"
	@echo "make shell        - Enter Nix development shell"
	@echo "make ssl-cert     - Generate SSL certificates"
	@echo "make python-server - Start Python test server"
	@echo "make all-tests    - Run complete test suite"
	@echo "make security-test - Run security audit"

# Enter Nix shell
shell:
	nix-shell

# Install dependencies
install:
	@if command -v npm >/dev/null 2>&1; then \
		echo "Installing Node.js dependencies..."; \
		npm install; \
	else \
		echo "npm not found. Installing Python dependencies..."; \
		pip install -r requirements.txt; \
	fi

# Generate SSL certificates
ssl-cert:
	@mkdir -p ssl
	@if [ ! -f ssl/cert.pem ] || [ ! -f ssl/key.pem ]; then \
		echo "Generating SSL certificates..."; \
		openssl req -x509 -newkey rsa:2048 -keyout ssl/key.pem -out ssl/cert.pem \
			-days 365 -nodes -subj "/CN=localhost"; \
	else \
		echo "SSL certificates already exist"; \
	fi

# Start development server
dev: ssl-cert
	@if command -v npm >/dev/null 2>&1; then \
		echo "Starting Node.js development server..."; \
		npm start; \
	else \
		echo "Node.js not found. Starting Python server..."; \
		$(MAKE) python-server; \
	fi

# Start Python test server
python-server: ssl-cert
	@echo "Starting Python test server..."
	@chmod +x test/python-test-server.py
	@python3 test/python-test-server.py

# Run tests
test:
	@echo "Running test suite..."
	@if [ -x test/run-basic-tests.sh ]; then \
		cd test && ./run-basic-tests.sh; \
	else \
		echo "Test script not found"; \
		exit 1; \
	fi

# Run all tests
all-tests:
	@echo "Running complete test suite..."
	@if [ -x test/run-all-tests.sh ]; then \
		cd test && ./run-all-tests.sh; \
	else \
		$(MAKE) test; \
	fi

# Run security audit
security-test:
	@echo "Running security audit..."
	@if [ -x test/security-audit.sh ]; then \
		cd test && ./security-audit.sh; \
	else \
		echo "Security audit script not found"; \
		exit 1; \
	fi

# Build for production
build:
	@if command -v npm >/dev/null 2>&1; then \
		echo "Building with npm..."; \
		npm run build; \
	else \
		echo "Creating production bundle..."; \
		mkdir -p dist; \
		cp -r frontend/* dist/; \
		echo "Static files copied to dist/"; \
	fi

# Clean build artifacts
clean:
	@echo "Cleaning build artifacts..."
	@rm -rf dist/ coverage/ test-results-* *.log
	@rm -rf node_modules/ .npm-global/
	@rm -rf __pycache__/ .pytest_cache/
	@rm -rf ssl/*.pem
	@echo "Clean complete"

# Docker build
docker-build:
	@echo "Building Docker image..."
	@docker build -t nixos-gui:latest .

# Docker run
docker-run: docker-build
	@echo "Running Docker container..."
	@docker run -p 8080:8080 -p 8443:8443 nixos-gui:latest

# Check environment
check-env:
	@echo "Environment Check"
	@echo "================="
	@echo -n "Node.js: "; node --version 2>/dev/null || echo "Not installed"
	@echo -n "npm: "; npm --version 2>/dev/null || echo "Not installed"
	@echo -n "Python: "; python3 --version 2>/dev/null || echo "Not installed"
	@echo -n "OpenSSL: "; openssl version 2>/dev/null || echo "Not installed"
	@echo -n "Nix: "; nix --version 2>/dev/null || echo "Not installed"
	@echo -n "Git: "; git --version 2>/dev/null || echo "Not installed"

# Development setup
setup: check-env ssl-cert
	@echo "Setting up development environment..."
	@mkdir -p logs data test/results
	@if [ ! -f .env ]; then \
		echo "Creating .env file..."; \
		echo "NODE_ENV=development" > .env; \
		echo "JWT_SECRET=$$(openssl rand -hex 32)" >> .env; \
		echo "SESSION_SECRET=$$(openssl rand -hex 32)" >> .env; \
		echo "PORT=8080" >> .env; \
		echo "HTTPS_PORT=8443" >> .env; \
	fi
	@echo "Setup complete!"

# Watch for changes (requires entr)
watch:
	@if command -v entr >/dev/null 2>&1; then \
		find . -name "*.js" -o -name "*.html" -o -name "*.css" | entr -r make dev; \
	else \
		echo "entr not installed. Install with: nix-env -iA nixpkgs.entr"; \
		exit 1; \
	fi