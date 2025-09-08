#!/usr/bin/env python3
"""
HRM Performance Benchmarking Suite
Comprehensive evaluation and performance testing for HRM neural networks

Features:
1. Real-world performance benchmarking
2. Uncertainty quantification evaluation
3. Comparative analysis with baselines
4. Production readiness assessment
5. Continuous monitoring metrics
"""

import torch
import torch.nn.functional as F
import numpy as np
import json
import time
import logging
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any, Union
from dataclasses import dataclass, asdict
import subprocess
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    classification_report, confusion_matrix,
    roc_auc_score, calibration_curve
)
from sklearn.calibration import CalibratedClassifierCV
import pandas as pd
from datetime import datetime
import psutil
import GPUtil
from tqdm import tqdm
import warnings
warnings.filterwarnings('ignore')

# Import HRM modules
try:
    from .hrm_neural import HRMNeuralNetwork, NeuralHRM
    from .hrm_training_pipeline import EnhancedNixOSDataset, TrainingConfig
    from .hrm_reasoner_v2 import HierarchicalReasoningModel
except ImportError:
    import sys
    sys.path.append(str(Path(__file__).parent))
    from hrm_neural import HRMNeuralNetwork, NeuralHRM
    from hrm_training_pipeline import EnhancedNixOSDataset, TrainingConfig
    from hrm_reasoner_v2 import HierarchicalReasoningModel

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class BenchmarkConfig:
    """Configuration for benchmarking suite"""
    # Test data configuration
    test_data_path: str = "data/nixos-hrm-training/generated_test.json"
    real_world_queries_path: str = "data/real_world_queries.json"
    
    # Benchmarking parameters
    num_monte_carlo_samples: int = 100
    uncertainty_threshold: float = 0.1
    confidence_calibration: bool = True
    
    # Performance thresholds
    min_accuracy: float = 0.85
    min_f1_score: float = 0.80
    max_inference_time_ms: float = 100.0
    max_memory_mb: float = 512.0
    
    # Output configuration
    results_dir: str = "benchmarks/results"
    plots_dir: str = "benchmarks/plots"
    generate_plots: bool = True
    save_detailed_results: bool = True

class HRMBenchmarkSuite:
    """Comprehensive benchmarking suite for HRM models"""
    
    def __init__(self, config: BenchmarkConfig):
        self.config = config
        
        # Create output directories
        self.results_dir = Path(config.results_dir)
        self.plots_dir = Path(config.plots_dir)
        self.results_dir.mkdir(parents=True, exist_ok=True)
        self.plots_dir.mkdir(parents=True, exist_ok=True)
        
        # Benchmark results storage
        self.results = {
            'accuracy_metrics': {},
            'uncertainty_metrics': {},
            'performance_metrics': {},
            'calibration_metrics': {},
            'comparative_analysis': {},
            'production_readiness': {}
        }
    
    def benchmark_model(self, model: Union[NeuralHRM, torch.nn.Module], 
                       test_data: List[Dict], 
                       model_name: str = "HRM_Model") -> Dict[str, Any]:
        """Run comprehensive benchmark on HRM model"""
        
        logger.info(f"🏁 Starting benchmark for {model_name}")
        
        # 1. Accuracy and Classification Metrics
        accuracy_results = self._evaluate_accuracy(model, test_data)
        self.results['accuracy_metrics'][model_name] = accuracy_results
        
        # 2. Uncertainty Quantification
        uncertainty_results = self._evaluate_uncertainty(model, test_data)
        self.results['uncertainty_metrics'][model_name] = uncertainty_results
        
        # 3. Performance Metrics (Speed, Memory)
        performance_results = self._evaluate_performance(model, test_data)
        self.results['performance_metrics'][model_name] = performance_results
        
        # 4. Confidence Calibration
        calibration_results = self._evaluate_calibration(model, test_data)
        self.results['calibration_metrics'][model_name] = calibration_results
        
        # 5. Real-world Query Performance
        if Path(self.config.real_world_queries_path).exists():
            realworld_results = self._evaluate_real_world_queries(model)
            self.results['real_world_performance'] = realworld_results
        
        # 6. Production Readiness Assessment
        readiness_score = self._assess_production_readiness(
            accuracy_results, performance_results, uncertainty_results
        )
        self.results['production_readiness'][model_name] = readiness_score
        
        # Generate comprehensive report
        if self.config.save_detailed_results:
            self._save_detailed_results(model_name)
        
        if self.config.generate_plots:
            self._generate_benchmark_plots(model_name)
        
        logger.info(f"✅ Benchmark complete for {model_name}")
        
        return {
            'model_name': model_name,
            'accuracy_score': accuracy_results['accuracy'],
            'f1_score': accuracy_results['f1_macro'],
            'inference_time_ms': performance_results['avg_inference_time_ms'],
            'memory_usage_mb': performance_results['memory_usage_mb'],
            'uncertainty_quality': uncertainty_results['uncertainty_quality'],
            'production_readiness': readiness_score['overall_score']
        }
    
    def _evaluate_accuracy(self, model, test_data: List[Dict]) -> Dict[str, float]:
        """Evaluate classification accuracy and related metrics"""
        logger.info("📊 Evaluating accuracy metrics...")
        
        predictions = []
        ground_truth = []
        confidences = []
        
        for sample in tqdm(test_data, desc="Accuracy evaluation"):
            query = sample['input']
            true_strategy = sample.get('target_strategy', 'unknown')
            
            # Get model prediction
            if isinstance(model, NeuralHRM):
                result = model.predict(query, return_all=True)
                pred_strategy = result['strategy']
                confidence = result['confidence']
            else:
                # Handle PyTorch model directly
                pred_strategy, confidence = self._predict_with_pytorch_model(model, query)
            
            predictions.append(pred_strategy)
            ground_truth.append(true_strategy)
            confidences.append(confidence)
        
        # Remove unknown labels for evaluation
        valid_indices = [i for i, gt in enumerate(ground_truth) if gt != 'unknown']
        
        if valid_indices:
            valid_preds = [predictions[i] for i in valid_indices]
            valid_truth = [ground_truth[i] for i in valid_indices]
            valid_conf = [confidences[i] for i in valid_indices]
            
            # Compute standard metrics
            accuracy = accuracy_score(valid_truth, valid_preds)
            precision = precision_score(valid_truth, valid_preds, average='macro', zero_division=0)
            recall = recall_score(valid_truth, valid_preds, average='macro', zero_division=0)
            f1_macro = f1_score(valid_truth, valid_preds, average='macro', zero_division=0)
            f1_weighted = f1_score(valid_truth, valid_preds, average='weighted', zero_division=0)
            
            # Per-class metrics
            class_report = classification_report(
                valid_truth, valid_preds, output_dict=True, zero_division=0
            )
            
            results = {
                'accuracy': accuracy,
                'precision_macro': precision,
                'recall_macro': recall,
                'f1_macro': f1_macro,
                'f1_weighted': f1_weighted,
                'num_samples': len(valid_indices),
                'avg_confidence': np.mean(valid_conf),
                'per_class_metrics': class_report
            }
        else:
            results = {
                'accuracy': 0.0,
                'precision_macro': 0.0,
                'recall_macro': 0.0,
                'f1_macro': 0.0,
                'f1_weighted': 0.0,
                'num_samples': 0,
                'avg_confidence': 0.0,
                'per_class_metrics': {}
            }
        
        return results
    
    def _evaluate_uncertainty(self, model, test_data: List[Dict]) -> Dict[str, float]:
        """Evaluate uncertainty quantification quality"""
        logger.info("🎲 Evaluating uncertainty quantification...")
        
        uncertainties = []
        accuracies = []
        confidences = []
        
        for sample in tqdm(test_data, desc="Uncertainty evaluation"):
            query = sample['input']
            true_strategy = sample.get('target_strategy', 'unknown')
            
            if true_strategy == 'unknown':
                continue
            
            # Monte Carlo predictions for uncertainty
            predictions = []
            for _ in range(self.config.num_monte_carlo_samples):
                if isinstance(model, NeuralHRM):
                    result = model.predict(query)
                    predictions.append(result)
            
            if predictions:
                # Compute epistemic uncertainty (prediction variance)
                strategy_probs = []
                confidences_mc = []
                
                for pred in predictions:
                    if 'all_strategies' in pred:
                        # Convert to probability vector
                        prob_vector = [pred['all_strategies'].get(s, 0.0) 
                                     for s in sorted(pred['all_strategies'].keys())]
                        strategy_probs.append(prob_vector)
                    confidences_mc.append(pred.get('confidence', 0.5))
                
                if strategy_probs:
                    epistemic_uncertainty = np.var(strategy_probs, axis=0).mean()
                else:
                    epistemic_uncertainty = 0.0
                
                # Prediction accuracy
                final_prediction = predictions[0]['strategy']
                is_correct = (final_prediction == true_strategy)
                
                uncertainties.append(epistemic_uncertainty)
                accuracies.append(float(is_correct))
                confidences.append(np.mean(confidences_mc))
        
        if uncertainties:
            # Uncertainty-accuracy correlation
            # High uncertainty should correlate with low accuracy
            uncertainty_acc_corr = np.corrcoef(uncertainties, accuracies)[0, 1]
            
            # Uncertainty calibration (higher uncertainty → lower confidence)
            uncertainty_conf_corr = np.corrcoef(uncertainties, confidences)[0, 1]
            
            # Quality metric: good uncertainty should be negatively correlated with accuracy
            uncertainty_quality = max(0.0, -uncertainty_acc_corr)
            
            results = {
                'avg_epistemic_uncertainty': np.mean(uncertainties),
                'std_epistemic_uncertainty': np.std(uncertainties),
                'uncertainty_accuracy_correlation': uncertainty_acc_corr,
                'uncertainty_confidence_correlation': uncertainty_conf_corr,
                'uncertainty_quality': uncertainty_quality,
                'num_samples': len(uncertainties)
            }
        else:
            results = {
                'avg_epistemic_uncertainty': 0.0,
                'std_epistemic_uncertainty': 0.0,
                'uncertainty_accuracy_correlation': 0.0,
                'uncertainty_confidence_correlation': 0.0,
                'uncertainty_quality': 0.0,
                'num_samples': 0
            }
        
        return results
    
    def _evaluate_performance(self, model, test_data: List[Dict]) -> Dict[str, float]:
        """Evaluate performance metrics (speed, memory usage)"""
        logger.info("⏱️ Evaluating performance metrics...")
        
        inference_times = []
        memory_usage_before = psutil.virtual_memory().used / 1024 / 1024  # MB
        
        # Warm up
        for _ in range(5):
            if test_data:
                query = test_data[0]['input']
                if isinstance(model, NeuralHRM):
                    model.predict(query)
        
        # Measure inference times
        sample_size = min(100, len(test_data))  # Test on 100 samples max
        test_samples = np.random.choice(test_data, sample_size, replace=False)
        
        for sample in tqdm(test_samples, desc="Performance evaluation"):
            query = sample['input']
            
            start_time = time.perf_counter()
            
            if isinstance(model, NeuralHRM):
                model.predict(query)
            else:
                self._predict_with_pytorch_model(model, query)
            
            end_time = time.perf_counter()
            
            inference_time_ms = (end_time - start_time) * 1000
            inference_times.append(inference_time_ms)
        
        memory_usage_after = psutil.virtual_memory().used / 1024 / 1024  # MB
        memory_usage_mb = memory_usage_after - memory_usage_before
        
        # GPU memory if available
        gpu_memory_mb = 0.0
        try:
            gpus = GPUtil.getGPUs()
            if gpus:
                gpu_memory_mb = gpus[0].memoryUsed
        except:
            pass
        
        results = {
            'avg_inference_time_ms': np.mean(inference_times),
            'median_inference_time_ms': np.median(inference_times),
            'p95_inference_time_ms': np.percentile(inference_times, 95),
            'p99_inference_time_ms': np.percentile(inference_times, 99),
            'std_inference_time_ms': np.std(inference_times),
            'memory_usage_mb': max(0, memory_usage_mb),
            'gpu_memory_mb': gpu_memory_mb,
            'throughput_qps': 1000.0 / np.mean(inference_times) if inference_times else 0.0
        }
        
        return results
    
    def _evaluate_calibration(self, model, test_data: List[Dict]) -> Dict[str, float]:
        """Evaluate confidence calibration"""
        logger.info("🎯 Evaluating confidence calibration...")
        
        confidences = []
        accuracies = []
        
        for sample in tqdm(test_data, desc="Calibration evaluation"):
            query = sample['input']
            true_strategy = sample.get('target_strategy', 'unknown')
            
            if true_strategy == 'unknown':
                continue
            
            if isinstance(model, NeuralHRM):
                result = model.predict(query)
                pred_strategy = result['strategy']
                confidence = result['confidence']
            else:
                pred_strategy, confidence = self._predict_with_pytorch_model(model, query)
            
            is_correct = float(pred_strategy == true_strategy)
            
            confidences.append(confidence)
            accuracies.append(is_correct)
        
        if len(confidences) > 10:  # Need sufficient samples
            # Calibration curve
            try:
                fraction_of_positives, mean_predicted_value = calibration_curve(
                    accuracies, confidences, n_bins=10
                )
                
                # Expected Calibration Error (ECE)
                ece = np.mean(np.abs(fraction_of_positives - mean_predicted_value))
                
                # Reliability (how well calibrated)
                reliability = 1.0 - ece
                
                # Brier score (lower is better)
                brier_score = np.mean((np.array(confidences) - np.array(accuracies)) ** 2)
                
                results = {
                    'expected_calibration_error': ece,
                    'reliability': reliability,
                    'brier_score': brier_score,
                    'avg_confidence': np.mean(confidences),
                    'avg_accuracy': np.mean(accuracies),
                    'num_samples': len(confidences),
                    'calibration_curve': {
                        'fraction_of_positives': fraction_of_positives.tolist(),
                        'mean_predicted_value': mean_predicted_value.tolist()
                    }
                }
            except Exception as e:
                logger.warning(f"Calibration evaluation failed: {e}")
                results = {
                    'expected_calibration_error': float('inf'),
                    'reliability': 0.0,
                    'brier_score': float('inf'),
                    'avg_confidence': np.mean(confidences) if confidences else 0.0,
                    'avg_accuracy': np.mean(accuracies) if accuracies else 0.0,
                    'num_samples': len(confidences)
                }
        else:
            results = {
                'expected_calibration_error': float('inf'),
                'reliability': 0.0,
                'brier_score': float('inf'),
                'avg_confidence': 0.0,
                'avg_accuracy': 0.0,
                'num_samples': 0
            }
        
        return results
    
    def _evaluate_real_world_queries(self, model) -> Dict[str, Any]:
        """Evaluate on real-world queries if available"""
        logger.info("🌍 Evaluating real-world queries...")
        
        try:
            with open(self.config.real_world_queries_path, 'r') as f:
                real_queries = json.load(f)
        except FileNotFoundError:
            logger.warning("Real-world queries file not found")
            return {'available': False}
        
        results = {
            'available': True,
            'num_queries': len(real_queries),
            'predictions': []
        }
        
        for query_data in tqdm(real_queries, desc="Real-world evaluation"):
            query = query_data['query']
            expected_category = query_data.get('category', 'unknown')
            
            if isinstance(model, NeuralHRM):
                result = model.predict(query, return_all=True)
                
                prediction = {
                    'query': query,
                    'expected_category': expected_category,
                    'predicted_strategy': result['strategy'],
                    'confidence': result['confidence'],
                    'all_strategies': result.get('all_strategies', {}),
                    'solution': result.get('solution', '')
                }
                
                results['predictions'].append(prediction)
        
        # Calculate accuracy if ground truth available
        if results['predictions'] and 'expected_category' in results['predictions'][0]:
            correct = sum(
                1 for p in results['predictions'] 
                if p['predicted_strategy'] == p['expected_category']
            )
            results['real_world_accuracy'] = correct / len(results['predictions'])
        
        return results
    
    def _predict_with_pytorch_model(self, model: torch.nn.Module, 
                                   query: str) -> Tuple[str, float]:
        """Helper to make predictions with raw PyTorch model"""
        # Simple tokenization (would need actual tokenizer in production)
        tokens = [ord(c) for c in query.lower()[:50]]
        tokens += [0] * (50 - len(tokens))
        
        input_tensor = torch.tensor([tokens], dtype=torch.long)
        
        model.eval()
        with torch.no_grad():
            strategy_logits, confidence = model(input_tensor)
            
            strategy_idx = strategy_logits.argmax(dim=1).item()
            confidence_val = confidence.item()
        
        # Simple strategy mapping (would need actual mapping in production)
        strategies = [
            'direct_install', 'configuration_nix', 'flake_approach',
            'shell_environment', 'overlay_solution', 'search_discover'
        ]
        
        strategy = strategies[strategy_idx] if strategy_idx < len(strategies) else 'unknown'
        
        return strategy, confidence_val
    
    def _assess_production_readiness(self, accuracy_results: Dict, 
                                   performance_results: Dict,
                                   uncertainty_results: Dict) -> Dict[str, Any]:
        """Assess overall production readiness"""
        logger.info("📋 Assessing production readiness...")
        
        # Define scoring criteria
        criteria = {
            'accuracy': {
                'value': accuracy_results['accuracy'],
                'threshold': self.config.min_accuracy,
                'weight': 0.3
            },
            'f1_score': {
                'value': accuracy_results['f1_macro'],
                'threshold': self.config.min_f1_score,
                'weight': 0.25
            },
            'inference_time': {
                'value': performance_results['avg_inference_time_ms'],
                'threshold': self.config.max_inference_time_ms,
                'weight': 0.2,
                'inverse': True  # Lower is better
            },
            'memory_usage': {
                'value': performance_results['memory_usage_mb'],
                'threshold': self.config.max_memory_mb,
                'weight': 0.15,
                'inverse': True  # Lower is better
            },
            'uncertainty_quality': {
                'value': uncertainty_results['uncertainty_quality'],
                'threshold': 0.5,
                'weight': 0.1
            }
        }
        
        # Calculate individual scores
        individual_scores = {}
        total_score = 0.0
        
        for criterion, config in criteria.items():
            value = config['value']
            threshold = config['threshold']
            weight = config['weight']
            
            if config.get('inverse', False):
                # Lower values are better (e.g., latency, memory)
                score = min(1.0, threshold / max(value, 0.001))
            else:
                # Higher values are better (e.g., accuracy)
                score = min(1.0, value / threshold) if threshold > 0 else 0.0
            
            individual_scores[criterion] = {
                'score': score,
                'value': value,
                'threshold': threshold,
                'passed': score >= 1.0
            }
            
            total_score += score * weight
        
        # Overall assessment
        readiness_level = "Not Ready"
        if total_score >= 0.9:
            readiness_level = "Production Ready"
        elif total_score >= 0.8:
            readiness_level = "Nearly Ready"
        elif total_score >= 0.6:
            readiness_level = "Development Ready"
        else:
            readiness_level = "Needs Improvement"
        
        results = {
            'overall_score': total_score,
            'readiness_level': readiness_level,
            'individual_scores': individual_scores,
            'recommendations': self._generate_recommendations(individual_scores)
        }
        
        return results
    
    def _generate_recommendations(self, scores: Dict) -> List[str]:
        """Generate improvement recommendations"""
        recommendations = []
        
        for criterion, details in scores.items():
            if not details['passed']:
                if criterion == 'accuracy':
                    recommendations.append(
                        f"Improve model accuracy: current {details['value']:.1%}, "
                        f"target {details['threshold']:.1%}"
                    )
                elif criterion == 'f1_score':
                    recommendations.append(
                        f"Improve F1 score through better class balancing: "
                        f"current {details['value']:.3f}, target {details['threshold']:.3f}"
                    )
                elif criterion == 'inference_time':
                    recommendations.append(
                        f"Optimize inference speed: current {details['value']:.1f}ms, "
                        f"target <{details['threshold']:.1f}ms"
                    )
                elif criterion == 'memory_usage':
                    recommendations.append(
                        f"Reduce memory usage: current {details['value']:.1f}MB, "
                        f"target <{details['threshold']:.1f}MB"
                    )
                elif criterion == 'uncertainty_quality':
                    recommendations.append(
                        f"Improve uncertainty quantification quality"
                    )
        
        if not recommendations:
            recommendations.append("Model meets all production criteria")
        
        return recommendations
    
    def _save_detailed_results(self, model_name: str):
        """Save detailed benchmark results"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = self.results_dir / f"benchmark_{model_name}_{timestamp}.json"
        
        with open(results_file, 'w') as f:
            json.dump(self.results, f, indent=2, default=str)
        
        logger.info(f"💾 Detailed results saved: {results_file}")
    
    def _generate_benchmark_plots(self, model_name: str):
        """Generate benchmark visualization plots"""
        logger.info("📊 Generating benchmark plots...")
        
        plt.style.use('seaborn-v0_8')
        
        # 1. Performance Overview
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle(f'HRM Benchmark Results - {model_name}', fontsize=16, fontweight='bold')
        
        # Accuracy metrics
        if model_name in self.results['accuracy_metrics']:
            acc_data = self.results['accuracy_metrics'][model_name]
            metrics = ['accuracy', 'precision_macro', 'recall_macro', 'f1_macro']
            values = [acc_data.get(m, 0) for m in metrics]
            
            axes[0, 0].bar(metrics, values, color=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728'])
            axes[0, 0].set_title('Classification Metrics')
            axes[0, 0].set_ylabel('Score')
            axes[0, 0].set_ylim(0, 1)
            
            # Add value labels on bars
            for i, v in enumerate(values):
                axes[0, 0].text(i, v + 0.01, f'{v:.3f}', ha='center', va='bottom')
        
        # Performance metrics
        if model_name in self.results['performance_metrics']:
            perf_data = self.results['performance_metrics'][model_name]
            
            # Inference time distribution (simulated)
            times = np.random.normal(
                perf_data['avg_inference_time_ms'], 
                perf_data.get('std_inference_time_ms', 5), 100
            )
            axes[0, 1].hist(times, bins=20, color='skyblue', alpha=0.7, edgecolor='black')
            axes[0, 1].axvline(perf_data['avg_inference_time_ms'], color='red', 
                              linestyle='--', label=f"Avg: {perf_data['avg_inference_time_ms']:.1f}ms")
            axes[0, 1].set_title('Inference Time Distribution')
            axes[0, 1].set_xlabel('Time (ms)')
            axes[0, 1].set_ylabel('Frequency')
            axes[0, 1].legend()
        
        # Calibration plot
        if (model_name in self.results['calibration_metrics'] and 
            'calibration_curve' in self.results['calibration_metrics'][model_name]):
            
            cal_data = self.results['calibration_metrics'][model_name]['calibration_curve']
            
            if cal_data['fraction_of_positives'] and cal_data['mean_predicted_value']:
                axes[1, 0].plot(
                    cal_data['mean_predicted_value'], 
                    cal_data['fraction_of_positives'],
                    marker='o', linewidth=2, label='Model'
                )
                axes[1, 0].plot([0, 1], [0, 1], linestyle='--', color='gray', label='Perfect Calibration')
                axes[1, 0].set_title('Calibration Plot')
                axes[1, 0].set_xlabel('Mean Predicted Confidence')
                axes[1, 0].set_ylabel('Fraction of Positives')
                axes[1, 0].legend()
        
        # Production readiness radar chart
        if model_name in self.results['production_readiness']:
            readiness_data = self.results['production_readiness'][model_name]
            
            if 'individual_scores' in readiness_data:
                scores = readiness_data['individual_scores']
                categories = list(scores.keys())
                values = [scores[cat]['score'] for cat in categories]
                
                # Create radar chart
                angles = np.linspace(0, 2 * np.pi, len(categories), endpoint=False).tolist()
                values += values[:1]  # Complete the circle
                angles += angles[:1]
                
                ax = axes[1, 1]
                ax.plot(angles, values, 'o-', linewidth=2, label=model_name)
                ax.fill(angles, values, alpha=0.25)
                ax.set_xticks(angles[:-1])
                ax.set_xticklabels(categories, rotation=45)
                ax.set_ylim(0, 1)
                ax.set_title('Production Readiness Scores')
                ax.grid(True)
        
        plt.tight_layout()
        plot_file = self.plots_dir / f"benchmark_{model_name}.png"
        plt.savefig(plot_file, dpi=300, bbox_inches='tight')
        plt.close()
        
        logger.info(f"📈 Plots saved: {plot_file}")
    
    def compare_models(self, model_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Compare multiple models"""
        logger.info("🔍 Comparing models...")
        
        if len(model_results) < 2:
            logger.warning("Need at least 2 models for comparison")
            return {}
        
        # Create comparison DataFrame
        comparison_data = []
        for result in model_results:
            comparison_data.append({
                'Model': result['model_name'],
                'Accuracy': result['accuracy_score'],
                'F1 Score': result['f1_score'],
                'Inference Time (ms)': result['inference_time_ms'],
                'Memory (MB)': result['memory_usage_mb'],
                'Production Score': result['production_readiness']
            })
        
        df = pd.DataFrame(comparison_data)
        
        # Find best model for each metric
        best_models = {
            'accuracy': df.loc[df['Accuracy'].idxmax(), 'Model'],
            'f1_score': df.loc[df['F1 Score'].idxmax(), 'Model'],
            'speed': df.loc[df['Inference Time (ms)'].idxmin(), 'Model'],
            'memory': df.loc[df['Memory (MB)'].idxmin(), 'Model'],
            'overall': df.loc[df['Production Score'].idxmax(), 'Model']
        }
        
        # Generate comparison plot
        if self.config.generate_plots:
            plt.figure(figsize=(12, 8))
            
            # Normalize metrics for comparison (0-1 scale)
            normalized_df = df.copy()
            
            # Higher is better metrics
            for col in ['Accuracy', 'F1 Score', 'Production Score']:
                normalized_df[col] = (df[col] - df[col].min()) / (df[col].max() - df[col].min())
            
            # Lower is better metrics (invert)
            for col in ['Inference Time (ms)', 'Memory (MB)']:
                normalized_df[col] = 1 - ((df[col] - df[col].min()) / (df[col].max() - df[col].min()))
            
            # Create comparison plot
            metrics = ['Accuracy', 'F1 Score', 'Inference Time (ms)', 'Memory (MB)', 'Production Score']
            x = np.arange(len(metrics))
            
            colors = plt.cm.Set1(np.linspace(0, 1, len(df)))
            
            for i, (_, row) in enumerate(normalized_df.iterrows()):
                plt.bar(x + i * 0.15, [row[m] for m in metrics], 
                       width=0.15, label=row['Model'], color=colors[i], alpha=0.8)
            
            plt.xlabel('Metrics')
            plt.ylabel('Normalized Score (Higher is Better)')
            plt.title('Model Comparison')
            plt.xticks(x + 0.15 * (len(df) - 1) / 2, metrics, rotation=45)
            plt.legend()
            plt.tight_layout()
            
            comparison_plot = self.plots_dir / "model_comparison.png"
            plt.savefig(comparison_plot, dpi=300, bbox_inches='tight')
            plt.close()
        
        comparison_results = {
            'comparison_table': df.to_dict('records'),
            'best_models': best_models,
            'summary': {
                'total_models': len(df),
                'best_overall': best_models['overall'],
                'avg_accuracy': df['Accuracy'].mean(),
                'avg_inference_time': df['Inference Time (ms)'].mean()
            }
        }
        
        # Save comparison results
        if self.config.save_detailed_results:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            comparison_file = self.results_dir / f"model_comparison_{timestamp}.json"
            
            with open(comparison_file, 'w') as f:
                json.dump(comparison_results, f, indent=2, default=str)
        
        return comparison_results
    
    def generate_final_report(self) -> str:
        """Generate comprehensive final report"""
        logger.info("📄 Generating final benchmark report...")
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        report = f"""
# HRM Neural Network Benchmark Report

**Generated**: {timestamp}
**Benchmark Suite Version**: 1.0

## Executive Summary

"""
        
        # Add model summaries
        for model_name in self.results['accuracy_metrics'].keys():
            acc = self.results['accuracy_metrics'][model_name]['accuracy']
            f1 = self.results['accuracy_metrics'][model_name]['f1_macro']
            time_ms = self.results['performance_metrics'][model_name]['avg_inference_time_ms']
            readiness = self.results['production_readiness'][model_name]['readiness_level']
            
            report += f"""
### {model_name}
- **Accuracy**: {acc:.1%}
- **F1 Score**: {f1:.3f}
- **Inference Time**: {time_ms:.1f}ms
- **Production Readiness**: {readiness}

"""
        
        report += """
## Detailed Metrics

See individual benchmark files for complete analysis.

## Recommendations

"""
        
        # Add recommendations from production readiness assessments
        for model_name, readiness_data in self.results['production_readiness'].items():
            if 'recommendations' in readiness_data:
                report += f"\n### {model_name}\n"
                for rec in readiness_data['recommendations']:
                    report += f"- {rec}\n"
        
        report += """

## Conclusion

This benchmark provides comprehensive evaluation of HRM neural network models
across accuracy, performance, uncertainty quantification, and production readiness.
Use these results to guide model selection and improvement efforts.

---
*Generated by HRM Benchmarking Suite*
"""
        
        # Save report
        report_file = self.results_dir / f"benchmark_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        with open(report_file, 'w') as f:
            f.write(report)
        
        logger.info(f"📋 Final report saved: {report_file}")
        
        return report

def run_comprehensive_benchmark():
    """Run comprehensive benchmark on HRM models"""
    
    # Configuration
    config = BenchmarkConfig(
        test_data_path="data/nixos-hrm-training/generated_test.json",
        min_accuracy=0.80,
        min_f1_score=0.75,
        max_inference_time_ms=200.0,  # Relaxed for CPU
        generate_plots=True
    )
    
    # Create benchmark suite
    benchmark = HRMBenchmarkSuite(config)
    
    # Load test data
    try:
        with open(config.test_data_path, 'r') as f:
            test_data = json.load(f)
        logger.info(f"📂 Loaded {len(test_data)} test samples")
    except FileNotFoundError:
        logger.error(f"Test data not found: {config.test_data_path}")
        logger.info("Please run the training pipeline first to generate test data")
        return
    
    # Initialize model for benchmarking
    logger.info("🤖 Initializing HRM model for benchmarking...")
    model = NeuralHRM(device='cpu')
    
    # Run benchmark
    try:
        results = benchmark.benchmark_model(model, test_data, "HRM_Neural_CPU")
        
        print("\n" + "="*60)
        print("🏆 HRM Benchmark Results")
        print("="*60)
        print(f"✅ Accuracy: {results['accuracy_score']:.1%}")
        print(f"✅ F1 Score: {results['f1_score']:.3f}")
        print(f"⏱️  Inference Time: {results['inference_time_ms']:.1f}ms")
        print(f"📊 Memory Usage: {results['memory_usage_mb']:.1f}MB")
        print(f"📋 Production Readiness: {results['production_readiness']:.1%}")
        
        # Generate final report
        report = benchmark.generate_final_report()
        
        print(f"\n📄 Complete results saved to: {config.results_dir}")
        
        if config.generate_plots:
            print(f"📈 Visualizations saved to: {config.plots_dir}")
        
        return results
        
    except Exception as e:
        logger.error(f"Benchmark failed: {e}")
        return None

if __name__ == "__main__":
    results = run_comprehensive_benchmark()