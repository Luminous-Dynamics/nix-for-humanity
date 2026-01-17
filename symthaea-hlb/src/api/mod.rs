//! # Symthaea Benchmark API
//!
//! RESTful API for consciousness measurement and benchmark submission.
//!
//! ## Endpoints
//! - POST /v1/submit - Submit model for Φ evaluation
//! - GET /v1/results/{id} - Get evaluation results
//! - GET /v1/leaderboard - Public leaderboard
//! - GET /v1/datasets - List available datasets
//! - POST /v1/compare - Compare two models
//!
//! ## Usage
//! ```rust
//! use symthaea::api::create_router;
//!
//! #[tokio::main]
//! async fn main() {
//!     let app = create_router();
//!     let listener = tokio::net::TcpListener::bind("0.0.0.0:8080").await.unwrap();
//!     axum::serve(listener, app).await.unwrap();
//! }
//! ```

pub mod handlers;
pub mod models;
pub mod state;

use axum::{
    routing::{get, post},
    Router,
    middleware,
};
use tower_http::cors::CorsLayer;
use std::sync::Arc;
use crate::api::state::AppState;

/// Create the API router with all endpoints
pub fn create_router() -> Router {
    let state = Arc::new(AppState::new());

    Router::new()
        // Core endpoints
        .route("/v1/submit", post(handlers::submit_model))
        .route("/v1/results/:submission_id", get(handlers::get_results))
        .route("/v1/leaderboard", get(handlers::get_leaderboard))
        .route("/v1/leaderboard/topologies", get(handlers::get_topology_rankings))
        .route("/v1/datasets", get(handlers::list_datasets))
        .route("/v1/datasets/:dataset_id", get(handlers::get_dataset))
        .route("/v1/compare", post(handlers::compare_models))
        .route("/v1/dimensional-sweep", post(handlers::dimensional_sweep))
        // Health check
        .route("/health", get(handlers::health_check))
        // Add CORS support
        .layer(CorsLayer::permissive())
        // Add shared state
        .with_state(state)
}

/// Start the API server
pub async fn serve(addr: &str) -> Result<(), Box<dyn std::error::Error>> {
    let app = create_router();
    let listener = tokio::net::TcpListener::bind(addr).await?;
    println!("🚀 Symthaea API listening on http://{}", addr);
    axum::serve(listener, app).await?;
    Ok(())
}
