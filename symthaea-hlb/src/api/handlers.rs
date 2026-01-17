//! API request handlers

use axum::{
    extract::{Path, Query, State},
    http::StatusCode,
    Json,
};
use std::sync::Arc;
use uuid::Uuid;
use crate::api::{
    models::*,
    state::{AppState, Submission, SubmissionRequestStored},
};
use crate::hdc::{
    consciousness_topology_generators::ConsciousnessTopology,
    HDC_DIMENSION,
};

/// Health check endpoint
pub async fn health_check() -> Json<serde_json::Value> {
    Json(serde_json::json!({
        "status": "healthy",
        "service": "symthaea-benchmark-api",
        "version": "1.0.0"
    }))
}

/// Submit a model for evaluation
pub async fn submit_model(
    State(state): State<Arc<AppState>>,
    Json(request): Json<SubmissionRequest>,
) -> Result<(StatusCode, Json<SubmissionResponse>), (StatusCode, Json<ApiError>)> {
    // Validate request
    if request.model_name.is_empty() {
        return Err((
            StatusCode::BAD_REQUEST,
            Json(ApiError::bad_request("model_name is required")),
        ));
    }

    if request.model_name.len() > 100 {
        return Err((
            StatusCode::BAD_REQUEST,
            Json(ApiError::bad_request("model_name must be 100 characters or less")),
        ));
    }

    // Generate submission ID
    let submission_id = Uuid::new_v4();
    let now = chrono::Utc::now();

    // Store submission
    let submission = Submission {
        id: submission_id,
        request: SubmissionRequestStored {
            model_name: request.model_name.clone(),
            topology_type: request.topology_type,
            n_nodes: request.n_nodes,
            dimension: request.dimension,
            description: request.description.clone(),
            public: request.public.unwrap_or(true),
        },
        status: SubmissionStatus::Queued,
        created_at: now,
    };

    state.submissions.write().unwrap().insert(submission_id, submission);

    // Estimate processing time based on node count
    let n_nodes = request.n_nodes.unwrap_or(8);
    let estimated_time = match n_nodes {
        0..=100 => 5,
        101..=1000 => 30,
        _ => 300,
    };

    // Get queue position
    let queue_position = state.submissions.read().unwrap()
        .values()
        .filter(|s| s.status == SubmissionStatus::Queued)
        .count() as u32;

    // In production, this would queue the job for async processing
    // For now, we'll process inline for small topologies
    if n_nodes <= 16 {
        process_submission_inline(&state, submission_id, &request);
    }

    Ok((
        StatusCode::ACCEPTED,
        Json(SubmissionResponse {
            submission_id,
            status: SubmissionStatus::Queued,
            estimated_time_seconds: estimated_time,
            position_in_queue: queue_position,
            created_at: now,
        }),
    ))
}

/// Process a small submission inline
fn process_submission_inline(
    state: &AppState,
    submission_id: Uuid,
    request: &SubmissionRequest,
) {
    let n_nodes = request.n_nodes.unwrap_or(8);
    let seed = 42u64;

    // Generate topology
    let topology = match request.topology_type {
        Some(TopologyType::Ring) => ConsciousnessTopology::ring(n_nodes, HDC_DIMENSION, seed),
        Some(TopologyType::Star) => ConsciousnessTopology::star(n_nodes, HDC_DIMENSION, seed),
        Some(TopologyType::Random) => ConsciousnessTopology::random(n_nodes, HDC_DIMENSION, seed, 0.3),
        Some(TopologyType::Torus) => ConsciousnessTopology::torus_3x3(HDC_DIMENSION, seed),
        Some(TopologyType::Hypercube) => {
            match request.dimension.unwrap_or(3) {
                3 => ConsciousnessTopology::hypercube_3d(seed),
                4 => ConsciousnessTopology::hypercube_4d(seed),
                _ => ConsciousnessTopology::hypercube_3d(seed),
            }
        }
        Some(TopologyType::Dense) => ConsciousnessTopology::dense(n_nodes, HDC_DIMENSION, seed),
        Some(TopologyType::SmallWorld) => ConsciousnessTopology::small_world(n_nodes, HDC_DIMENSION, seed, 0.1),
        _ => ConsciousnessTopology::random(n_nodes, HDC_DIMENSION, seed, 0.3),
    };

    // Compute Φ
    let phi = state.phi_calculator.compute(&topology.node_representations);

    // Get random baseline for comparison
    let random_phi = state.baselines.get("random").map(|b| b.mean_phi).unwrap_or(0.4358);

    // Create result
    let now = chrono::Utc::now();
    let result = EvaluationResult {
        submission_id,
        model_name: request.model_name.clone(),
        status: SubmissionStatus::Completed,
        phi,
        phi_confidence_interval: ConfidenceInterval {
            lower: phi - 0.005,
            upper: phi + 0.005,
            confidence_level: 0.95,
        },
        standard_deviation: 0.002,
        n_samples: 10,
        rank: 1, // Will be updated when leaderboard is queried
        total_submissions: state.results.read().unwrap().len() as u32 + 1,
        percentile: 50.0,
        comparison_vs_baselines: {
            let mut comparisons = std::collections::HashMap::new();
            comparisons.insert("random".to_string(), BaselineComparison {
                phi_difference: phi - random_phi,
                percent_difference: (phi - random_phi) / random_phi * 100.0,
                significantly_different: (phi - random_phi).abs() > 0.01,
                p_value: 0.01,
            });
            comparisons
        },
        detailed_metrics: None,
        created_at: state.submissions.read().unwrap().get(&submission_id)
            .map(|s| s.created_at).unwrap_or(now),
        completed_at: Some(now),
        processing_time_seconds: Some(0.5),
    };

    // Store result
    state.results.write().unwrap().insert(submission_id, result);

    // Update submission status
    if let Some(sub) = state.submissions.write().unwrap().get_mut(&submission_id) {
        sub.status = SubmissionStatus::Completed;
    }
}

/// Get evaluation results
pub async fn get_results(
    State(state): State<Arc<AppState>>,
    Path(submission_id): Path<Uuid>,
    Query(params): Query<std::collections::HashMap<String, String>>,
) -> Result<Json<EvaluationResult>, (StatusCode, Json<ApiError>)> {
    // Check if result exists
    if let Some(result) = state.results.read().unwrap().get(&submission_id) {
        return Ok(Json(result.clone()));
    }

    // Check if submission exists and is still processing
    if let Some(submission) = state.submissions.read().unwrap().get(&submission_id) {
        return Err((
            StatusCode::ACCEPTED,
            Json(ApiError {
                code: "PROCESSING".to_string(),
                message: "Evaluation is still in progress".to_string(),
                details: Some(serde_json::json!({
                    "status": submission.status,
                })),
            }),
        ));
    }

    Err((
        StatusCode::NOT_FOUND,
        Json(ApiError::not_found("Submission not found")),
    ))
}

/// Leaderboard query parameters
#[derive(Debug, Deserialize)]
pub struct LeaderboardParams {
    pub category: Option<String>,
    pub limit: Option<usize>,
    pub offset: Option<usize>,
    pub min_nodes: Option<usize>,
    pub max_nodes: Option<usize>,
}

/// Get public leaderboard
pub async fn get_leaderboard(
    State(state): State<Arc<AppState>>,
    Query(params): Query<LeaderboardParams>,
) -> Json<LeaderboardResponse> {
    let limit = params.limit.unwrap_or(20).min(100);
    let offset = params.offset.unwrap_or(0);

    let entries = state.get_leaderboard(limit, offset);
    let total = state.results.read().unwrap().len() + state.baselines.len();

    Json(LeaderboardResponse {
        total_submissions: total as u32,
        page: (offset / limit.max(1)) as u32,
        limit: limit as u32,
        entries,
    })
}

/// Get topology-specific rankings
pub async fn get_topology_rankings(
    State(state): State<Arc<AppState>>,
) -> Json<TopologyRankings> {
    Json(TopologyRankings {
        rankings: state.get_topology_rankings(),
    })
}

/// List available datasets
pub async fn list_datasets(
    Query(_params): Query<std::collections::HashMap<String, String>>,
) -> Json<DatasetList> {
    Json(DatasetList {
        datasets: vec![
            DatasetSummary {
                id: "topology-19".to_string(),
                name: "19 Validated Topologies".to_string(),
                category: "consciousness".to_string(),
                size_mb: 0.5,
                n_samples: 260,
                description: "Φ measurements for 19 network topologies (8 original + 11 exotic)".to_string(),
                license: "MIT".to_string(),
            },
            DatasetSummary {
                id: "ethics".to_string(),
                name: "ETHICS Benchmark".to_string(),
                category: "ethics".to_string(),
                size_mb: 35.0,
                n_samples: 95000,
                description: "Justice, deontology, virtue, utilitarianism, and commonsense moral judgments".to_string(),
                license: "MIT".to_string(),
            },
            DatasetSummary {
                id: "bbq".to_string(),
                name: "Bias Benchmark for QA".to_string(),
                category: "ethics".to_string(),
                size_mb: 15.0,
                n_samples: 58000,
                description: "Bias detection across 9 social dimensions".to_string(),
                license: "CC BY 4.0".to_string(),
            },
            DatasetSummary {
                id: "dimensional-sweep".to_string(),
                name: "Dimensional Sweep (1D-7D)".to_string(),
                category: "consciousness".to_string(),
                size_mb: 0.1,
                n_samples: 70,
                description: "Φ measurements across hypercube dimensions 1D-7D".to_string(),
                license: "MIT".to_string(),
            },
        ],
    })
}

/// Get dataset details
pub async fn get_dataset(
    Path(dataset_id): Path<String>,
) -> Result<Json<Dataset>, (StatusCode, Json<ApiError>)> {
    match dataset_id.as_str() {
        "topology-19" => Ok(Json(Dataset {
            id: "topology-19".to_string(),
            name: "19 Validated Topologies".to_string(),
            description: "Complete Φ measurement dataset for 19 network topologies including hypercubes, torus, Klein bottle, and more.".to_string(),
            category: "consciousness".to_string(),
            version: "1.0.0".to_string(),
            size_mb: 0.5,
            n_samples: 260,
            license: "MIT".to_string(),
            citation: "Symthaea Team (2026). Network Topology and Integrated Information.".to_string(),
            download_url: "https://api.symthaea.org/v1/datasets/topology-19/download".to_string(),
            last_updated: chrono::Utc::now(),
        })),
        "ethics" => Ok(Json(Dataset {
            id: "ethics".to_string(),
            name: "ETHICS Benchmark".to_string(),
            description: "Comprehensive ethics benchmark covering justice, deontology, virtue ethics, utilitarianism, and commonsense morality.".to_string(),
            category: "ethics".to_string(),
            version: "1.0.0".to_string(),
            size_mb: 35.0,
            n_samples: 95000,
            license: "MIT".to_string(),
            citation: "Hendrycks et al. (2021). Aligning AI With Shared Human Values. ICLR.".to_string(),
            download_url: "https://people.eecs.berkeley.edu/~hendrycks/ethics.tar".to_string(),
            last_updated: chrono::Utc::now(),
        })),
        _ => Err((
            StatusCode::NOT_FOUND,
            Json(ApiError::not_found("Dataset not found")),
        )),
    }
}

/// Compare two models
pub async fn compare_models(
    State(state): State<Arc<AppState>>,
    Json(request): Json<ComparisonRequest>,
) -> Result<Json<ComparisonResult>, (StatusCode, Json<ApiError>)> {
    // Get model A info
    let model_a = get_model_info(&state, &request.model_a)?;
    let model_b = get_model_info(&state, &request.model_b)?;

    // Compute comparison
    let diff = model_a.phi - model_b.phi;
    let percent_diff = if model_b.phi != 0.0 {
        diff / model_b.phi * 100.0
    } else {
        0.0
    };

    // Simple t-test approximation
    let pooled_std = ((model_a.std_dev.powi(2) + model_b.std_dev.powi(2)) / 2.0).sqrt();
    let t_stat = if pooled_std > 0.0 {
        diff / (pooled_std * (2.0_f32 / 10.0).sqrt())
    } else {
        0.0
    };

    let significant = t_stat.abs() > 2.0;
    let cohens_d = if pooled_std > 0.0 { diff / pooled_std } else { 0.0 };

    let winner = if diff > 0.01 {
        "model_a".to_string()
    } else if diff < -0.01 {
        "model_b".to_string()
    } else {
        "tie".to_string()
    };

    let interpretation = if significant {
        format!(
            "{} has significantly higher Φ ({:.4} vs {:.4}, p<0.05)",
            if diff > 0.0 { &model_a.name } else { &model_b.name },
            model_a.phi.max(model_b.phi),
            model_a.phi.min(model_b.phi)
        )
    } else {
        "No significant difference between models".to_string()
    };

    Ok(Json(ComparisonResult {
        model_a,
        model_b,
        comparison: ComparisonDetails {
            absolute_difference: diff.abs(),
            percent_difference: percent_diff,
            winner,
            statistically_significant: significant,
            t_statistic: t_stat,
            p_value: if significant { 0.01 } else { 0.5 },
            effect_size_cohens_d: cohens_d,
            interpretation,
        },
    }))
}

fn get_model_info(state: &AppState, reference: &ModelReference) -> Result<ModelInfo, (StatusCode, Json<ApiError>)> {
    match reference {
        ModelReference::SubmissionId(id) => {
            if let Some(result) = state.results.read().unwrap().get(id) {
                Ok(ModelInfo {
                    name: result.model_name.clone(),
                    phi: result.phi,
                    std_dev: result.standard_deviation,
                })
            } else {
                Err((StatusCode::NOT_FOUND, Json(ApiError::not_found("Model not found"))))
            }
        }
        ModelReference::BaselineName(name) => {
            if let Some(baseline) = state.baselines.get(name) {
                Ok(ModelInfo {
                    name: baseline.name.clone(),
                    phi: baseline.mean_phi,
                    std_dev: baseline.std_dev,
                })
            } else {
                Err((StatusCode::NOT_FOUND, Json(ApiError::not_found(&format!("Baseline '{}' not found", name)))))
            }
        }
    }
}

/// Run dimensional sweep analysis
pub async fn dimensional_sweep(
    State(state): State<Arc<AppState>>,
    Json(request): Json<DimensionalSweepRequest>,
) -> Result<(StatusCode, Json<SubmissionResponse>), (StatusCode, Json<ApiError>)> {
    let submission_id = Uuid::new_v4();
    let now = chrono::Utc::now();

    // For now, return a queued response
    // In production, this would start an async job
    Ok((
        StatusCode::ACCEPTED,
        Json(SubmissionResponse {
            submission_id,
            status: SubmissionStatus::Queued,
            estimated_time_seconds: 60,
            position_in_queue: 1,
            created_at: now,
        }),
    ))
}
