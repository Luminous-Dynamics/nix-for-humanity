#!/usr/bin/env python3
"""
CLI commands for Predictive System Health
"""

import click
import json
from datetime import datetime, timedelta
from typing import Optional

from ..ai.advanced_features.predictive_health import (
    PredictiveHealthMonitor,
    HealthMetric,
    HealthStatus,
)


@click.group()
def health():
    """Predictive system health commands"""
    pass


@health.command()
@click.option("--json", "output_json", is_flag=True, help="Output as JSON")
def check(output_json: bool):
    """Perform complete system health check with predictions"""
    try:
        monitor = PredictiveHealthMonitor()
        report = monitor.analyze_health()

        if output_json:
            result = {
                "timestamp": report.timestamp.isoformat(),
                "overall_status": report.overall_status.value,
                "health_score": report.health_score,
                "current_metrics": {
                    k.value: v for k, v in report.current_metrics.items()
                },
                "immediate_issues": report.immediate_issues,
                "predicted_issues": [
                    {"issue": issue, "time": time.isoformat()}
                    for issue, time in report.predicted_issues
                ],
                "preventive_actions": report.preventive_actions,
                "risk_factors": report.risk_factors,
                "confidence": report.confidence,
            }
            click.echo(json.dumps(result, indent=2))
        else:
            # Status color based on health
            status_color = {
                HealthStatus.EXCELLENT: "green",
                HealthStatus.GOOD: "green",
                HealthStatus.WARNING: "yellow",
                HealthStatus.CRITICAL: "red",
                HealthStatus.FAILING: "red",
            }.get(report.overall_status, "white")

            status_icon = {
                HealthStatus.EXCELLENT: "✨",
                HealthStatus.GOOD: "✅",
                HealthStatus.WARNING: "⚠️",
                HealthStatus.CRITICAL: "🚨",
                HealthStatus.FAILING: "❌",
            }.get(report.overall_status, "📊")

            click.echo(
                click.style(
                    f"{status_icon} System Health: {report.overall_status.value.upper()}",
                    fg=status_color,
                    bold=True,
                )
            )
            click.echo(f"📊 Health Score: {report.health_score:.0f}/100")
            click.echo()

            # Current metrics
            click.echo(click.style("📈 Current Metrics:", fg="cyan"))
            for metric, value in list(report.current_metrics.items())[:5]:
                unit = {
                    HealthMetric.DISK_USAGE: "%",
                    HealthMetric.MEMORY_PRESSURE: "%",
                    HealthMetric.CPU_TEMPERATURE: "°C",
                    HealthMetric.BOOT_TIME: "s",
                    HealthMetric.SWAP_USAGE: "%",
                }.get(metric, "")
                click.echo(f"  • {metric.value}: {value:.1f}{unit}")

            # Immediate issues
            if report.immediate_issues:
                click.echo()
                click.echo(click.style("⚠️ Immediate Issues:", fg="red"))
                for issue in report.immediate_issues[:3]:
                    click.echo(f"  • {issue}")

            # Predicted issues
            if report.predicted_issues:
                click.echo()
                click.echo(click.style("🔮 Predicted Issues:", fg="yellow"))
                for issue, time in report.predicted_issues[:3]:
                    days_ahead = (time - datetime.now()).days
                    click.echo(f"  • {issue} (in {days_ahead} days)")

            # Preventive actions
            if report.preventive_actions:
                click.echo()
                click.echo(click.style("💡 Preventive Actions:", fg="green"))
                for action in report.preventive_actions[:3]:
                    click.echo(f"  • {action}")

            # Time to failure
            if report.estimated_time_to_failure:
                click.echo()
                days = report.estimated_time_to_failure.days
                click.echo(
                    click.style(
                        f"⏰ Estimated time to critical issue: {days} days",
                        fg="red" if days < 7 else "yellow",
                    )
                )

            click.echo()
            click.echo(f"Confidence: {report.confidence:.0%}")

    except Exception as e:
        click.echo(click.style(f"Error: {str(e)}", fg="red"), err=True)
        raise click.ClickException(str(e))


@health.command()
@click.argument("metric", type=click.Choice([m.value for m in HealthMetric]))
@click.option("--days", default=7, help="Days to predict ahead")
@click.option("--json", "output_json", is_flag=True, help="Output as JSON")
def predict(metric: str, days: int, output_json: bool):
    """Predict future value of specific health metric"""
    try:
        monitor = PredictiveHealthMonitor()
        health_metric = HealthMetric(metric)
        prediction = monitor.predict_metric(health_metric, days)

        if output_json:
            result = {
                "metric": prediction.metric.value,
                "current_value": prediction.current_value,
                "predicted_value": prediction.predicted_value,
                "days_ahead": days,
                "trend": prediction.trend,
                "risk_level": prediction.risk_level,
                "confidence": prediction.confidence,
                "recommendation": prediction.recommendation,
            }
            click.echo(json.dumps(result, indent=2))
        else:
            # Trend icon
            trend_icon = {"rising": "📈", "falling": "📉", "stable": "➡️"}.get(
                prediction.trend, "❓"
            )

            # Risk color
            risk_color = {"low": "green", "medium": "yellow", "high": "red"}.get(
                prediction.risk_level, "white"
            )

            click.echo(
                click.style(f"🔮 Prediction: {metric.upper()}", fg="cyan", bold=True)
            )
            click.echo()
            click.echo(f"Current: {prediction.current_value:.1f}")
            click.echo(f"Predicted ({days} days): {prediction.predicted_value:.1f}")
            click.echo(f"{trend_icon} Trend: {prediction.trend}")
            click.echo(click.style(f"⚠️ Risk: {prediction.risk_level}", fg=risk_color))
            click.echo()
            click.echo(f"💡 {prediction.recommendation}")
            click.echo()
            click.echo(f"Confidence: {prediction.confidence:.0%}")

    except Exception as e:
        click.echo(click.style(f"Error: {str(e)}", fg="red"), err=True)
        raise click.ClickException(str(e))


@health.command()
@click.option("--json", "output_json", is_flag=True, help="Output as JSON")
def risks(output_json: bool):
    """Show current system risk factors"""
    try:
        monitor = PredictiveHealthMonitor()
        report = monitor.analyze_health()

        if output_json:
            click.echo(json.dumps(report.risk_factors, indent=2))
        else:
            click.echo(click.style("⚠️ System Risk Assessment", fg="cyan", bold=True))
            click.echo()

            for factor, score in sorted(
                report.risk_factors.items(), key=lambda x: x[1], reverse=True
            ):
                # Color based on risk score
                if score > 70:
                    color = "red"
                    icon = "🔴"
                elif score > 40:
                    color = "yellow"
                    icon = "🟡"
                else:
                    color = "green"
                    icon = "🟢"

                click.echo(f"{icon} {factor.replace('_', ' ').title()}")

                # Risk bar
                bar_length = int(score / 5)
                bar = "█" * bar_length + "░" * (20 - bar_length)
                click.echo(click.style(f"   [{bar}] {score:.0f}%", fg=color))
                click.echo()

    except Exception as e:
        click.echo(click.style(f"Error: {str(e)}", fg="red"), err=True)
        raise click.ClickException(str(e))


@health.command()
@click.option("--all", "show_all", is_flag=True, help="Show all optimizations")
def optimize(show_all: bool):
    """Get system optimization suggestions"""
    try:
        monitor = PredictiveHealthMonitor()
        report = monitor.analyze_health()

        click.echo(
            click.style("🚀 System Optimization Suggestions", fg="cyan", bold=True)
        )
        click.echo()

        # Preventive actions (high priority)
        if report.preventive_actions:
            click.echo(click.style("🔥 High Priority (Prevent Issues):", fg="red"))
            for action in report.preventive_actions:
                click.echo(f"  • {action}")
            click.echo()

        # General optimizations
        if report.optimization_suggestions:
            click.echo(click.style("💡 Performance Optimizations:", fg="yellow"))
            limit = None if show_all else 5
            for suggestion in report.optimization_suggestions[:limit]:
                click.echo(f"  • {suggestion}")

            if not show_all and len(report.optimization_suggestions) > 5:
                remaining = len(report.optimization_suggestions) - 5
                click.echo(f"  ... and {remaining} more (use --all to see all)")

        if not report.preventive_actions and not report.optimization_suggestions:
            click.echo(click.style("✅ System is well-optimized!", fg="green"))

    except Exception as e:
        click.echo(click.style(f"Error: {str(e)}", fg="red"), err=True)
        raise click.ClickException(str(e))


@health.command()
def monitor():
    """Start continuous health monitoring (interactive)"""
    try:
        click.echo(click.style("🏥 Starting Health Monitor", fg="cyan", bold=True))
        click.echo("Press Ctrl+C to stop monitoring")
        click.echo()

        monitor = PredictiveHealthMonitor()

        import time

        while True:
            try:
                report = monitor.analyze_health()

                # Clear screen (simplified)
                click.clear()

                # Display status
                status_icon = {
                    HealthStatus.EXCELLENT: "✨",
                    HealthStatus.GOOD: "✅",
                    HealthStatus.WARNING: "⚠️",
                    HealthStatus.CRITICAL: "🚨",
                    HealthStatus.FAILING: "❌",
                }.get(report.overall_status, "📊")

                click.echo(
                    f"{status_icon} {report.overall_status.value.upper()} | Score: {report.health_score:.0f}/100"
                )
                click.echo(f"Last update: {datetime.now().strftime('%H:%M:%S')}")
                click.echo("-" * 40)

                # Show key metrics
                for metric, value in list(report.current_metrics.items())[:3]:
                    click.echo(f"{metric.value}: {value:.1f}")

                # Show any immediate issues
                if report.immediate_issues:
                    click.echo()
                    click.echo("⚠️ Issues:")
                    for issue in report.immediate_issues[:2]:
                        click.echo(f"  • {issue}")

                time.sleep(30)  # Update every 30 seconds

            except KeyboardInterrupt:
                click.echo("\n👋 Monitoring stopped")
                break

    except Exception as e:
        click.echo(click.style(f"Error: {str(e)}", fg="red"), err=True)
        raise click.ClickException(str(e))
