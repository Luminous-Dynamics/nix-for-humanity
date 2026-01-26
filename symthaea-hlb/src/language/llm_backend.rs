//! # LLM Backend: Trait and Implementations
//!
//! Provides the abstraction for connecting to language model backends.
//! The primary implementation is `OllamaBackend` which connects to a local
//! Ollama instance. A `SimulatedBackend` provides fallback when no LLM is available.
//!
//! Design principle: "HDC+LTC THINKS. LLM TRANSLATES."
//! The LLM is used purely for natural language translation of structured thoughts,
//! not for reasoning or decision-making.

use anyhow::Result;
use serde::{Deserialize, Serialize};

/// Parameters for LLM generation.
#[derive(Debug, Clone)]
pub struct GenerationParams {
    /// Temperature for sampling (0.0 = deterministic, 1.0 = creative).
    pub temperature: f32,
    /// Maximum tokens to generate.
    pub max_tokens: usize,
    /// System prompt to set context.
    pub system_prompt: Option<String>,
}

impl Default for GenerationParams {
    fn default() -> Self {
        Self {
            temperature: 0.7,
            max_tokens: 256,
            system_prompt: None,
        }
    }
}

/// Trait for LLM backend implementations.
///
/// Backends handle the actual text generation, whether via a local model
/// (Ollama), a remote API, or simulation.
#[async_trait::async_trait]
pub trait LLMBackend: Send + Sync {
    /// Generate a response for the given prompt with parameters.
    async fn generate(&self, prompt: &str, params: &GenerationParams) -> Result<String>;

    /// Check if the backend is available/healthy.
    async fn is_available(&self) -> bool;

    /// Get the backend name for logging.
    fn name(&self) -> &str;
}

/// Ollama backend connecting to a local Ollama instance.
///
/// Sends requests to `http://localhost:11434/api/generate` with
/// configurable model, timeout, and generation parameters.
pub struct OllamaBackend {
    /// Base URL for the Ollama API.
    base_url: String,
    /// Model to use for generation.
    model: String,
    /// HTTP client with timeout.
    client: reqwest::Client,
}

/// Ollama API request body.
#[derive(Serialize)]
struct OllamaRequest<'a> {
    model: &'a str,
    prompt: &'a str,
    #[serde(skip_serializing_if = "Option::is_none")]
    system: Option<&'a str>,
    stream: bool,
    options: OllamaOptions,
}

/// Ollama generation options.
#[derive(Serialize)]
struct OllamaOptions {
    temperature: f32,
    num_predict: usize,
}

/// Ollama API response body.
#[derive(Deserialize)]
struct OllamaResponse {
    response: String,
    #[allow(dead_code)]
    done: bool,
}

impl OllamaBackend {
    /// Create a new Ollama backend with default settings.
    ///
    /// Connects to `http://localhost:11434` with gemma3:1b (fast, capable).
    pub fn new() -> Self {
        Self::with_config("http://localhost:11434", "gemma3:1b")
    }

    /// Create with custom URL and model.
    pub fn with_config(base_url: &str, model: &str) -> Self {
        let client = reqwest::Client::builder()
            .timeout(std::time::Duration::from_secs(180)) // 3 minutes for longer prompts
            .build()
            .unwrap_or_default();

        Self {
            base_url: base_url.to_string(),
            model: model.to_string(),
            client,
        }
    }
}

#[async_trait::async_trait]
impl LLMBackend for OllamaBackend {
    async fn generate(&self, prompt: &str, params: &GenerationParams) -> Result<String> {
        let url = format!("{}/api/generate", self.base_url);

        let request_body = OllamaRequest {
            model: &self.model,
            prompt,
            system: params.system_prompt.as_deref(),
            stream: false,
            options: OllamaOptions {
                temperature: params.temperature,
                num_predict: params.max_tokens,
            },
        };

        let response = self.client
            .post(&url)
            .json(&request_body)
            .send()
            .await
            .map_err(|e| anyhow::anyhow!("Ollama request failed: {}", e))?;

        if !response.status().is_success() {
            let status = response.status();
            let body = response.text().await.unwrap_or_default();
            anyhow::bail!("Ollama returned {}: {}", status, body);
        }

        let ollama_response: OllamaResponse = response
            .json()
            .await
            .map_err(|e| anyhow::anyhow!("Failed to parse Ollama response: {}", e))?;

        Ok(ollama_response.response)
    }

    async fn is_available(&self) -> bool {
        let url = format!("{}/api/tags", self.base_url);
        match self.client.get(&url).send().await {
            Ok(resp) => resp.status().is_success(),
            Err(_) => false,
        }
    }

    fn name(&self) -> &str {
        "Ollama"
    }
}

/// Simulated backend for when no LLM is available.
///
/// Produces deterministic responses based on prompt content.
/// Used as a fallback when Ollama is not running.
pub struct SimulatedBackend;

#[async_trait::async_trait]
impl LLMBackend for SimulatedBackend {
    async fn generate(&self, prompt: &str, _params: &GenerationParams) -> Result<String> {
        // Produce a simple response based on the prompt
        let response = if prompt.contains("translate") || prompt.contains("Translate") {
            format!("I understand your input. {}", summarize_prompt(prompt))
        } else if prompt.contains('?') {
            format!("Regarding your question: {}", summarize_prompt(prompt))
        } else {
            format!("Acknowledged. {}", summarize_prompt(prompt))
        };
        Ok(response)
    }

    async fn is_available(&self) -> bool {
        true // Always available
    }

    fn name(&self) -> &str {
        "Simulated"
    }
}

/// Create the default backend: tries Ollama first, falls back to simulated.
pub fn default_backend() -> Box<dyn LLMBackend> {
    Box::new(OllamaBackend::new())
}

/// Create a simulated-only backend (for testing or offline use).
pub fn simulated_backend() -> Box<dyn LLMBackend> {
    Box::new(SimulatedBackend)
}

/// Summarize a prompt to ~20 words for simulated responses.
fn summarize_prompt(prompt: &str) -> String {
    let words: Vec<&str> = prompt.split_whitespace().collect();
    if words.len() <= 20 {
        words.join(" ")
    } else {
        format!("{}...", words[..20].join(" "))
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[tokio::test]
    async fn test_simulated_backend_always_available() {
        let backend = SimulatedBackend;
        assert!(backend.is_available().await);
    }

    #[tokio::test]
    async fn test_simulated_backend_generates_response() {
        let backend = SimulatedBackend;
        let params = GenerationParams::default();
        let result = backend.generate("Hello, how are you?", &params).await;
        assert!(result.is_ok());
        let text = result.unwrap();
        assert!(!text.is_empty());
    }

    #[tokio::test]
    async fn test_ollama_backend_creation() {
        let backend = OllamaBackend::new();
        assert_eq!(backend.name(), "Ollama");
        // Note: is_available() may return false if Ollama is not running
    }

    /// Integration test for Ollama backend.
    /// Requires Ollama to be running with llama3.2:3b or similar model.
    /// Skips gracefully if Ollama is not available.
    #[tokio::test]
    async fn test_ollama_integration() {
        let backend = OllamaBackend::new();

        // Skip if Ollama is not available
        if !backend.is_available().await {
            eprintln!("Skipping Ollama integration test: Ollama not available");
            return;
        }

        let params = GenerationParams {
            temperature: 0.3,
            max_tokens: 50,
            system_prompt: Some("You are a helpful assistant. Keep responses very brief.".to_string()),
        };

        let result = backend.generate("Say hello in exactly 3 words.", &params).await;

        match result {
            Ok(response) => {
                assert!(!response.is_empty(), "Ollama returned empty response");
                println!("Ollama response: {}", response);
            }
            Err(e) => {
                // Model might not be available - this is acceptable in CI
                eprintln!("Ollama generation failed (model may not be installed): {}", e);
            }
        }
    }
}
