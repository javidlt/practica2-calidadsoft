#!/usr/bin/env python3
"""
performance.py - Performance Monitoring and Metrics Module

This module handles performance monitoring and metrics collection
for Hugging Face models.
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import psutil

from models import ModelInfo


@dataclass
class PerformanceMetrics:
    """
    Data class for storing performance metrics.
    Demonstrates data encapsulation and type safety.
    """

    model_name: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    memory_usage_mb: float = 0.0
    cpu_usage_percent: float = 0.0
    inference_time_ms: float = 0.0
    throughput_tokens_per_sec: float = 0.0
    model_size_mb: float = 0.0
    gpu_usage_percent: Optional[float] = None
    error_rate: float = 0.0
    status: str = "healthy"

    def to_dict(self) -> Dict[str, Any]:
        """Convert metrics to dictionary format."""
        return {
            "model_name": self.model_name,
            "timestamp": self.timestamp,
            "memory_usage_mb": self.memory_usage_mb,
            "cpu_usage_percent": self.cpu_usage_percent,
            "inference_time_ms": self.inference_time_ms,
            "throughput_tokens_per_sec": self.throughput_tokens_per_sec,
            "model_size_mb": self.model_size_mb,
            "gpu_usage_percent": self.gpu_usage_percent,
            "error_rate": self.error_rate,
            "status": self.status,
        }


class MetricsCollector:
    """
    Collects various performance metrics from models and system.
    Demonstrates single responsibility principle - only collects metrics.
    """

    def __init__(self):
        """Initialize the metrics collector."""
        self.collection_history = []
        self.baseline_metrics = {}

    def collect_metrics(self, model: ModelInfo) -> PerformanceMetrics:
        """
        Collect performance metrics for a specific model.

        Args:
            model: ModelInfo object to collect metrics for

        Returns:
            PerformanceMetrics: Collected metrics
        """
        # Simulate metric collection
        metrics = PerformanceMetrics(
            model_name=model.name,
            memory_usage_mb=self._get_memory_usage(),
            cpu_usage_percent=self._get_cpu_usage(),
            inference_time_ms=self._simulate_inference_time(model),
            throughput_tokens_per_sec=self._simulate_throughput(model),
            model_size_mb=model.size_mb or self._estimate_model_size(model),
            gpu_usage_percent=self._get_gpu_usage(),
            error_rate=self._simulate_error_rate(),
            status=self._determine_status(model),
        )

        self.collection_history.append(metrics)
        return metrics

    def _get_memory_usage(self) -> float:
        """Get current memory usage in MB."""
        try:
            process = psutil.Process()
            memory_info = process.memory_info()
            return memory_info.rss / 1024 / 1024  # Convert to MB
        except Exception:
            return 512.0  # Default fallback

    def _get_cpu_usage(self) -> float:
        """Get current CPU usage percentage."""
        try:
            return psutil.cpu_percent(interval=0.1)
        except Exception:
            return 25.0  # Default fallback

    def _get_gpu_usage(self) -> Optional[float]:
        """Get GPU usage if available."""
        # Simulate GPU usage since we can't access actual GPU
        import secrets

        has_gpu = secrets.choice([True, False])
        return secrets.SystemRandom().uniform(20.0, 80.0) if has_gpu else None

    def _simulate_inference_time(self, model: ModelInfo) -> float:
        """Simulate inference time based on model characteristics."""
        base_time = 50.0  # Base time in ms

        # Adjust based on model size
        if model.size_mb:
            size_factor = model.size_mb / 1000  # Normalize
            base_time *= 1 + size_factor * 0.5

        # Adjust based on task complexity
        task_multipliers = {
            "text-generation": 2.0,
            "text-classification": 1.0,
            "question-answering": 1.5,
            "summarization": 1.8,
            "translation": 1.6,
        }

        multiplier = task_multipliers.get(model.task_type, 1.0)
        return base_time * multiplier

    def _simulate_throughput(self, model: ModelInfo) -> float:
        """Simulate throughput based on model characteristics."""
        base_throughput = 100.0  # tokens per second

        # Adjust based on model type
        task_throughputs = {
            "text-generation": 80.0,
            "text-classification": 200.0,
            "question-answering": 120.0,
            "summarization": 60.0,
            "translation": 90.0,
        }

        return task_throughputs.get(model.task_type, base_throughput)

    def _estimate_model_size(self, model: ModelInfo) -> float:
        """Estimate model size based on name and type."""
        # Size estimates based on common model patterns
        size_estimates = {
            "bert-base": 440.0,
            "bert-large": 1340.0,
            "gpt2": 548.0,
            "distilbert": 268.0,
            "roberta-base": 498.0,
            "t5-small": 242.0,
            "t5-base": 892.0,
        }

        for pattern, size in size_estimates.items():
            if pattern in model.name.lower():
                return size

        return 300.0  # Default estimate

    def _simulate_error_rate(self) -> float:
        """Simulate error rate (0-100%)."""
        import secrets

        return secrets.SystemRandom().uniform(0.0, 5.0)  # 0-5% error rate

    def _determine_status(self, model: ModelInfo) -> str:
        """Determine model status based on various factors."""
        import secrets

        # Base status determination logic with model-specific factors
        statuses = ["healthy", "warning", "degraded"]
        base_weights = [0.8, 0.15, 0.05]  # Default probability weights

        # Adjust weights based on model characteristics
        weights = base_weights.copy()

        # Larger models are more likely to have issues
        if model.size_mb and model.size_mb > 1000:
            weights[0] -= 0.1  # Less likely to be healthy
            weights[1] += 0.08  # More likely to have warnings
            weights[2] += 0.02  # Slightly more likely to be degraded

        # Complex tasks are more prone to issues
        complex_tasks = ["text-generation", "summarization"]
        if hasattr(model, "task_type") and model.task_type in complex_tasks:
            weights[0] -= 0.05
            weights[1] += 0.04
            weights[2] += 0.01

        # Ensure weights sum to 1.0
        total_weight = sum(weights)
        weights = [w / total_weight for w in weights]

        # Use secrets for cryptographically secure random selection
        random_value = secrets.SystemRandom().random()
        cumulative = 0
        for i, weight in enumerate(weights):
            cumulative += weight
            if random_value <= cumulative:
                return statuses[i]

        return statuses[0]  # Fallback to healthy

    def get_recent_metrics(
        self, model_name: str, hours: int = 24
    ) -> List[PerformanceMetrics]:
        """
        Get recent metrics for a specific model.

        Args:
            model_name: Name of the model
            hours: Number of hours to look back

        Returns:
            List[PerformanceMetrics]: Recent metrics
        """
        cutoff_time = datetime.now() - timedelta(hours=hours)

        recent_metrics = []
        for metric in self.collection_history:
            try:
                metric_time = datetime.fromisoformat(metric.timestamp)
                if metric_time >= cutoff_time and metric.model_name == model_name:
                    recent_metrics.append(metric)
            except ValueError:
                continue

        return recent_metrics


class PerformanceMonitor:
    """
    High-level performance monitoring system.
    Demonstrates composition and coordination of multiple components.
    """

    def __init__(self):
        """Initialize the performance monitor."""
        self.metrics_collector = MetricsCollector()
        self.performance_history = {}
        self.alerts = []
        self.thresholds = {
            "max_memory_mb": 2048,
            "max_cpu_percent": 80,
            "max_inference_time_ms": 1000,
            "min_throughput_tokens_per_sec": 50,
            "max_error_rate": 10,
        }

    def track_performance(
        self, model_name: str, metrics: PerformanceMetrics
    ) -> Dict[str, Any]:
        """
        Track performance for a model and generate alerts if needed.

        Args:
            model_name: Name of the model
            metrics: Performance metrics

        Returns:
            Dict: Performance tracking results
        """
        # Store metrics
        if model_name not in self.performance_history:
            self.performance_history[model_name] = []

        self.performance_history[model_name].append(metrics)

        # Check thresholds and generate alerts
        alerts = self._check_thresholds(metrics)
        self.alerts.extend(alerts)

        # Calculate trends
        trends = self._calculate_trends(model_name)

        return {
            "model_name": model_name,
            "current_metrics": metrics.to_dict(),
            "alerts": alerts,
            "trends": trends,
            "status": metrics.status,
        }

    def _check_thresholds(self, metrics: PerformanceMetrics) -> List[Dict[str, Any]]:
        """Check if metrics exceed defined thresholds."""
        alerts = []

        checks = [
            ("memory_usage_mb", metrics.memory_usage_mb, "max_memory_mb"),
            ("cpu_usage_percent", metrics.cpu_usage_percent, "max_cpu_percent"),
            ("inference_time_ms", metrics.inference_time_ms, "max_inference_time_ms"),
            ("error_rate", metrics.error_rate, "max_error_rate"),
        ]

        for metric_name, value, threshold_key in checks:
            threshold = self.thresholds.get(threshold_key)
            if threshold and value > threshold:
                alerts.append(
                    {
                        "type": "threshold_exceeded",
                        "metric": metric_name,
                        "value": value,
                        "threshold": threshold,
                        "model": metrics.model_name,
                        "timestamp": metrics.timestamp,
                        "severity": "high" if value > threshold * 1.5 else "medium",
                    }
                )

        # Check minimum throughput
        min_throughput = self.thresholds.get("min_throughput_tokens_per_sec")
        if min_throughput and metrics.throughput_tokens_per_sec < min_throughput:
            alerts.append(
                {
                    "type": "throughput_low",
                    "metric": "throughput_tokens_per_sec",
                    "value": metrics.throughput_tokens_per_sec,
                    "threshold": min_throughput,
                    "model": metrics.model_name,
                    "timestamp": metrics.timestamp,
                    "severity": "medium",
                }
            )

        return alerts

    def _calculate_trends(self, model_name: str) -> Dict[str, str]:
        """Calculate performance trends for a model."""
        history = self.performance_history.get(model_name, [])
        if len(history) < 2:
            return {"trend": "insufficient_data"}

        # Compare last two metrics
        recent = history[-1]
        previous = history[-2]

        trends = {}

        # Memory trend
        memory_change = recent.memory_usage_mb - previous.memory_usage_mb
        if memory_change > 10:
            trends["memory"] = "increasing"
        elif memory_change < -10:
            trends["memory"] = "decreasing"
        else:
            trends["memory"] = "stable"

        # CPU trend
        cpu_change = recent.cpu_usage_percent - previous.cpu_usage_percent
        if cpu_change > 5:
            trends["cpu"] = "increasing"
        elif cpu_change < -5:
            trends["cpu"] = "decreasing"
        else:
            trends["cpu"] = "stable"

        # Performance trend
        time_change = recent.inference_time_ms - previous.inference_time_ms
        if time_change > 50:
            trends["performance"] = "degrading"
        elif time_change < -50:
            trends["performance"] = "improving"
        else:
            trends["performance"] = "stable"

        return trends

    def get_model_summary(self, model_name: str) -> Dict[str, Any]:
        """
        Get a summary of model performance.

        Args:
            model_name: Name of the model

        Returns:
            Dict: Performance summary
        """
        history = self.performance_history.get(model_name, [])
        if not history:
            return {"error": "No performance data available"}

        latest = history[-1]

        # Calculate averages
        avg_memory = sum(m.memory_usage_mb for m in history) / len(history)
        avg_cpu = sum(m.cpu_usage_percent for m in history) / len(history)
        avg_inference = sum(m.inference_time_ms for m in history) / len(history)
        total_throughput = sum(m.throughput_tokens_per_sec for m in history)
        avg_throughput = total_throughput / len(history)

        # Count alerts
        model_alerts = [a for a in self.alerts if a.get("model") == model_name]

        return {
            "model_name": model_name,
            "latest_metrics": latest.to_dict(),
            "averages": {
                "memory_usage_mb": avg_memory,
                "cpu_usage_percent": avg_cpu,
                "inference_time_ms": avg_inference,
                "throughput_tokens_per_sec": avg_throughput,
            },
            "metrics_count": len(history),
            "alerts_count": len(model_alerts),
            "status": latest.status,
        }

    def get_system_overview(self) -> Dict[str, Any]:
        """Get an overview of the entire monitoring system."""
        total_models = len(self.performance_history)
        history_lengths = (
            len(history) for history in self.performance_history.values()
        )
        total_metrics = sum(history_lengths)
        total_alerts = len(self.alerts)

        # Status distribution
        status_counts = {}
        for history in self.performance_history.values():
            if history:
                status = history[-1].status
                status_counts[status] = status_counts.get(status, 0) + 1

        return {
            "total_models_monitored": total_models,
            "total_metrics_collected": total_metrics,
            "total_alerts": total_alerts,
            "status_distribution": status_counts,
            "monitoring_thresholds": self.thresholds,
        }


# Utility functions for monitoring operations
def generate_performance_report(monitor: PerformanceMonitor, models: List[str]) -> str:
    """
    Generate a text-based performance report.

    Args:
        monitor: PerformanceMonitor instance
        models: List of model names to include

    Returns:
        str: Formatted performance report
    """
    report_lines = ["=== Performance Report ===", ""]

    for model_name in models:
        summary = monitor.get_model_summary(model_name)
        if "error" not in summary:
            latest = summary["latest_metrics"]
            memory_mb = latest["memory_usage_mb"]
            cpu_pct = latest["cpu_usage_percent"]
            inference_ms = latest["inference_time_ms"]
            throughput_tps = latest["throughput_tokens_per_sec"]

            report_lines.extend(
                [
                    f"Model: {model_name}",
                    f"  Status: {summary['status']}",
                    f"  Memory Usage: {memory_mb:.1f} MB",
                    f"  CPU Usage: {cpu_pct:.1f}%",
                    f"  Inference Time: {inference_ms:.1f} ms",
                    f"  Throughput: {throughput_tps:.1f} tokens/sec",
                    f"  Alerts: {summary['alerts_count']}",
                    "",
                ]
            )

    system_overview = monitor.get_system_overview()
    report_lines.extend(
        [
            "=== System Overview ===",
            f"Total Models: {system_overview['total_models_monitored']}",
            f"Total Metrics: {system_overview['total_metrics_collected']}",
            f"Total Alerts: {system_overview['total_alerts']}",
            f"Status Distribution: {system_overview['status_distribution']}",
        ]
    )

    return "\n".join(report_lines)


class StatisticsCalculator:
    """
    Calculates various statistics from monitoring data.
    Demonstrates separation of concerns - only handles calculations.
    """

    @staticmethod
    def calculate_enrollment_stats(
        students: List[Any], courses: List[Any]
    ) -> Dict[str, Any]:
        """Calculate enrollment statistics (for compatibility with main)."""
        return {
            "total_students": len(students),
            "total_courses": len(courses),
            "avg_enrollments": 1.5,  # Mock value
        }

    @staticmethod
    def calculate_uptime_stats(
        metrics_history: List[PerformanceMetrics],
    ) -> Dict[str, float]:
        """Calculate uptime statistics from metrics history."""
        if not metrics_history:
            return {"uptime_percentage": 0.0}

        healthy_count = sum(1 for m in metrics_history if m.status == "healthy")
        uptime_percentage = (healthy_count / len(metrics_history)) * 100

        return {
            "uptime_percentage": uptime_percentage,
            "total_measurements": len(metrics_history),
            "healthy_measurements": healthy_count,
        }
