use anyhow::Result;
use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Intent {
    pub action: Action,
    pub entities: Vec<Entity>,
    pub confidence: f32,
    pub raw_input: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(tag = "type")]
pub enum Action {
    InstallPackage { package: String },
    RemovePackage { package: String },
    UpdateSystem,
    SearchPackages { query: String },
    GetHelp { topic: Option<String> },
    Unknown,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Entity {
    pub entity_type: String,
    pub value: String,
    pub confidence: f32,
}

pub struct NLPEngine {
    // This will communicate with the TypeScript NLP engine
    // For now, it's a placeholder
}

impl NLPEngine {
    pub fn new() -> Result<Self> {
        Ok(Self {})
    }

    pub async fn process(&self, input: &str) -> Result<Intent> {
        // TODO: This will call the TypeScript NLP engine
        // For now, return a simple parsed intent
        
        let intent = if input.contains("install") {
            let package = input.split_whitespace()
                .skip_while(|&w| w != "install")
                .nth(1)
                .unwrap_or("unknown")
                .to_string();
                
            Intent {
                action: Action::InstallPackage { package: package.clone() },
                entities: vec![Entity {
                    entity_type: "package".to_string(),
                    value: package,
                    confidence: 0.95,
                }],
                confidence: 0.95,
                raw_input: input.to_string(),
            }
        } else {
            Intent {
                action: Action::Unknown,
                entities: vec![],
                confidence: 0.0,
                raw_input: input.to_string(),
            }
        };

        Ok(intent)
    }
}