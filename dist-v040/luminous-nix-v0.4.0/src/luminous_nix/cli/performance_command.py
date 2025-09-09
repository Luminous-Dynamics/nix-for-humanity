#!/usr/bin/env python3
"""
Performance profiling commands for Luminous Nix CLI
Identifies bottlenecks and suggests optimizations
"""

import click
from pathlib import Path
from typing import Optional
import json
import logging

logger = logging.getLogger(__name__)

@click.group(name='performance')
@click.pass_context
def performance(ctx):
    """System performance profiling and optimization"""
    pass

@performance.command()
@click.option('--json', 'json_output', is_flag=True, help='Output in JSON format')
@click.pass_context
def profile(ctx, json_output):
    """Profile system performance and identify issues"""
    try:
        from ..ai.advanced_features.performance_profiler import PerformanceProfiler
        
        profiler = PerformanceProfiler()
        analysis = profiler.profile_system()
        
        if json_output:
            result = {
                'metrics': {
                    'boot_time_seconds': analysis.metrics.boot_time_seconds,
                    'rebuild_time_seconds': analysis.metrics.rebuild_time_seconds,
                    'memory_usage_gb': analysis.metrics.memory_usage_gb,
                    'cpu_usage_percent': analysis.metrics.cpu_usage_percent,
                    'cache_hit_rate': analysis.metrics.cache_hit_rate
                },
                'issues': [(issue.value, severity) for issue, severity in analysis.issues],
                'bottlenecks': analysis.bottlenecks,
                'potential_speedup': analysis.potential_speedup,
                'confidence': analysis.confidence
            }
            click.echo(json.dumps(result, indent=2))
        else:
            click.echo(click.style("📊 System Performance Profile", fg='cyan', bold=True))
            
            # Show metrics
            metrics = analysis.metrics
            click.echo("\n⏱️ Performance Metrics:")
            click.echo(f"  Boot time: {_format_time(metrics.boot_time_seconds)}")
            click.echo(f"  Rebuild time: {_format_time(metrics.rebuild_time_seconds)}")
            click.echo(f"  Memory usage: {metrics.memory_usage_gb:.1f}GB")
            click.echo(f"  CPU usage: {metrics.cpu_usage_percent:.0f}%")
            click.echo(f"  Cache hit rate: {metrics.cache_hit_rate * 100:.0f}%")
            
            # Show issues
            if analysis.issues:
                click.echo(click.style("\n⚠️  Performance Issues:", fg='yellow'))
                for issue, severity in analysis.issues[:3]:
                    severity_color = 'red' if severity > 0.7 else 'yellow' if severity > 0.3 else 'green'
                    click.echo(f"  • {issue.value} ({click.style(f'{severity*100:.0f}%', fg=severity_color)} severity)")
            
            # Show bottlenecks
            if analysis.bottlenecks:
                click.echo(click.style("\n🔴 Bottlenecks:", fg='red'))
                for bottleneck in analysis.bottlenecks:
                    click.echo(f"  • {bottleneck}")
            
            # Show quick wins
            if analysis.quick_wins:
                click.echo(click.style("\n⚡ Quick Optimizations:", fg='green'))
                for win in analysis.quick_wins[:2]:
                    click.echo(f"  • {win['action']}")
                    click.echo(f"    Impact: {win['impact']}, Time: {win['time_to_implement']}")
            
            # Show potential improvement
            click.echo(f"\n🚀 Potential speedup: {click.style(f'{analysis.potential_speedup:.0f}%', fg='green', bold=True)}")
            click.echo(f"Estimated boot time reduction: {analysis.estimated_boot_reduction:.1f}s")
            click.echo(f"Estimated memory savings: {analysis.estimated_memory_savings:.1f}GB")
            
            click.echo(f"\nConfidence: {_format_confidence(analysis.confidence)}")
            
    except Exception as e:
        logger.error(f"Profiling failed: {e}")
        ctx.fail(f"Error: {e}")

@performance.command()
@click.option('--json', 'json_output', is_flag=True, help='Output in JSON format')
@click.pass_context
def boot(ctx, json_output):
    """Optimize boot time"""
    try:
        from ..ai.advanced_features.performance_profiler import PerformanceProfiler
        
        profiler = PerformanceProfiler()
        optimizations = profiler.optimize_boot_time()
        
        if json_output:
            click.echo(json.dumps(optimizations, indent=2))
        else:
            if 'error' in optimizations:
                ctx.fail(f"Error: {optimizations['error']}")
            
            click.echo(click.style("🚀 Boot Time Optimization", fg='cyan', bold=True))
            click.echo(f"Current boot time: {optimizations['current_boot_time']:.1f}s")
            
            if optimizations['optimizations']:
                click.echo("\n📝 Recommended optimizations:")
                for i, opt in enumerate(optimizations['optimizations'], 1):
                    click.echo(f"\n{i}. {click.style(opt['action'], fg='green', bold=True)}")
                    if 'config' in opt:
                        click.echo(f"   Config: {opt['config']}")
                    if 'services' in opt:
                        click.echo(f"   Services: {', '.join(opt['services'][:3])}")
                    if 'modules' in opt:
                        click.echo(f"   Modules: {', '.join(opt['modules'][:3])}")
                    click.echo(f"   Impact: {opt['impact']}")
                    click.echo(f"   Difficulty: {_format_difficulty(opt['difficulty'])}")
            
            if 'estimated_final_boot_time' in optimizations:
                reduction = optimizations['current_boot_time'] - optimizations['estimated_final_boot_time']
                click.echo(f"\n✨ Estimated final boot time: {optimizations['estimated_final_boot_time']:.1f}s")
                click.echo(f"   Potential reduction: {reduction:.1f}s ({reduction/optimizations['current_boot_time']*100:.0f}%)")
                
    except Exception as e:
        logger.error(f"Boot optimization failed: {e}")
        ctx.fail(f"Error: {e}")

@performance.command()
@click.option('--json', 'json_output', is_flag=True, help='Output in JSON format')
@click.pass_context
def rebuild(ctx, json_output):
    """Optimize NixOS rebuild time"""
    try:
        from ..ai.advanced_features.performance_profiler import PerformanceProfiler
        
        profiler = PerformanceProfiler()
        optimizations = profiler.optimize_rebuild_time()
        
        if json_output:
            click.echo(json.dumps(optimizations, indent=2))
        else:
            if 'error' in optimizations:
                ctx.fail(f"Error: {optimizations['error']}")
            
            click.echo(click.style("🔨 Rebuild Time Optimization", fg='cyan', bold=True))
            click.echo(f"Current rebuild time: {optimizations['current_rebuild_time']:.0f}s")
            
            if optimizations['optimizations']:
                click.echo("\n📝 Recommended optimizations:")
                for i, opt in enumerate(optimizations['optimizations'], 1):
                    click.echo(f"\n{i}. {click.style(opt['action'], fg='green', bold=True)}")
                    if 'config' in opt:
                        click.echo("   Config:")
                        for line in opt['config'].split('\n')[:5]:
                            if line.strip():
                                click.echo(f"     {line}")
                    if 'suggestion' in opt:
                        click.echo(f"   {opt['suggestion']}")
                    click.echo(f"   Impact: {opt['impact']}")
                    click.echo(f"   Difficulty: {_format_difficulty(opt['difficulty'])}")
                    
    except Exception as e:
        logger.error(f"Rebuild optimization failed: {e}")
        ctx.fail(f"Error: {e}")

@performance.command()
@click.option('--json', 'json_output', is_flag=True, help='Output in JSON format')
@click.pass_context
def resources(ctx, json_output):
    """Analyze resource usage (CPU, memory, disk)"""
    try:
        from ..ai.advanced_features.performance_profiler import PerformanceProfiler
        
        profiler = PerformanceProfiler()
        analysis = profiler.analyze_resource_usage()
        
        if json_output:
            click.echo(json.dumps(analysis, indent=2))
        else:
            if 'error' in analysis:
                ctx.fail(f"Error: {analysis['error']}")
            
            click.echo(click.style("💻 Resource Usage Analysis", fg='cyan', bold=True))
            
            # Memory analysis
            memory = analysis['memory']
            memory_color = 'red' if memory['status'] == 'high' else 'green'
            click.echo(f"\n🧠 Memory:")
            click.echo(f"  Usage: {memory['current_usage_gb']:.1f}GB ({click.style(memory['status'], fg=memory_color)})")
            if memory['top_consumers']:
                click.echo("  Top consumers:")
                for proc in memory['top_consumers'][:3]:
                    click.echo(f"    • {proc['name']}: {proc['memory_mb']}MB")
            
            # CPU analysis
            cpu = analysis['cpu']
            cpu_color = 'red' if cpu['status'] == 'high' else 'green'
            click.echo(f"\n⚡ CPU:")
            click.echo(f"  Usage: {cpu['average_usage']:.0f}% ({click.style(cpu['status'], fg=cpu_color)})")
            if cpu['top_processes']:
                click.echo("  Top processes:")
                for proc in cpu['top_processes'][:3]:
                    click.echo(f"    • {proc['name']}: {proc['cpu_percent']}%")
            
            # Disk analysis
            disk = analysis['disk']
            click.echo(f"\n💾 Disk:")
            click.echo(f"  Usage: {disk['usage_gb']:.1f}GB")
            click.echo(f"  Closure size: {disk['closure_size_gb']:.1f}GB")
            if disk['largest_packages']:
                click.echo("  Largest packages:")
                for pkg in disk['largest_packages'][:3]:
                    click.echo(f"    • {pkg['name']}: {pkg['size']}")
            
            # Recommendations
            if analysis['recommendations']:
                click.echo(click.style("\n💡 Recommendations:", fg='yellow'))
                for rec in analysis['recommendations']:
                    click.echo(f"  • {rec['action']}")
                    if 'config' in rec:
                        click.echo(f"    {rec['config']}")
                        
    except Exception as e:
        logger.error(f"Resource analysis failed: {e}")
        ctx.fail(f"Error: {e}")

def _format_time(seconds: float) -> str:
    """Format time in seconds with color coding"""
    if seconds > 60:
        color = 'red'
        time_str = f"{seconds:.0f}s"
    elif seconds > 30:
        color = 'yellow'
        time_str = f"{seconds:.0f}s"
    else:
        color = 'green'
        time_str = f"{seconds:.0f}s"
    return click.style(time_str, fg=color)

def _format_confidence(confidence: float) -> str:
    """Format confidence score with color"""
    if confidence >= 0.8:
        color = 'green'
    elif confidence >= 0.5:
        color = 'yellow'
    else:
        color = 'red'
    return click.style(f"{confidence * 100:.0f}%", fg=color)

def _format_difficulty(difficulty: str) -> str:
    """Format difficulty with color"""
    colors = {
        'easy': 'green',
        'moderate': 'yellow',
        'complex': 'red',
        'high': 'red'
    }
    return click.style(difficulty.capitalize(), fg=colors.get(difficulty, 'white'))