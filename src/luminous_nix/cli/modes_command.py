#!/usr/bin/env python3
"""
CLI commands for System Mode Transformations
"""

import asyncio
import json
from datetime import datetime, timedelta

import click

from ..ai.advanced_features.mode_wizard import SystemModeWizard, WizardQuestion
from ..ai.advanced_features.system_modes import SystemMode, SystemModeManager
from ..ui.mode_animator import AnimationType, ModeAnimator


@click.group()
def modes():
    """System mode transformation commands"""
    pass


@modes.command(name="list")
@click.option("--json", "output_json", is_flag=True, help="Output as JSON")
def list_modes(output_json: bool):
    """List available system modes"""
    try:
        manager = SystemModeManager()

        if output_json:
            modes_list = [
                {
                    "name": mode.value,
                    "description": profile.description,
                    "cpu_governor": profile.cpu_governor,
                    "gpu_profile": profile.gpu_profile,
                }
                for mode, profile in manager.profiles.items()
            ]
            click.echo(json.dumps(modes_list, indent=2))
        else:
            click.echo(click.style("🎭 Available System Modes", fg="cyan", bold=True))
            click.echo()

            for mode, profile in manager.profiles.items():
                icon = {
                    SystemMode.WORK: "💼",
                    SystemMode.GAMING: "🎮",
                    SystemMode.PRESENTATION: "📊",
                    SystemMode.FOCUS: "🎯",
                    SystemMode.BATTERY_SAVER: "🔋",
                    SystemMode.SECURE: "🔒",
                    SystemMode.STREAMING: "📹",
                    SystemMode.PERFORMANCE: "🚀",
                    SystemMode.QUIET: "🤫",
                    SystemMode.MINIMAL: "📦",
                }.get(mode, "⚡")

                click.echo(f"{icon} {mode.value.upper()}")
                click.echo(f"   {profile.description}")
                click.echo()

    except Exception as e:
        click.echo(click.style(f"Error: {str(e)}", fg="red"), err=True)
        raise click.ClickException(str(e))


@modes.command()
@click.argument("mode", type=click.Choice([m.value for m in SystemMode]))
@click.option("--dry-run", is_flag=True, help="Preview changes without applying")
@click.option("--json", "output_json", is_flag=True, help="Output as JSON")
@click.option("--animate", is_flag=True, help="Show transition animation")
@click.option(
    "--animation-type",
    type=click.Choice([a.value for a in AnimationType]),
    default="fade",
    help="Type of transition animation",
)
def switch(
    mode: str, dry_run: bool, output_json: bool, animate: bool, animation_type: str
):
    """Switch to specified system mode"""
    try:
        manager = SystemModeManager()
        target_mode = SystemMode(mode)

        # Show animation if requested
        if animate and not output_json and not dry_run:
            animator = ModeAnimator()
            current_mode = manager.current_mode.value

            # Run animation asynchronously
            async def run_animation():
                await animator.animate_transition(
                    from_mode=current_mode, to_mode=mode, duration=2.0
                )

            # Show animation first
            asyncio.run(run_animation())

            # Then show progress animation for actual changes
            steps = animator.get_transition_steps(current_mode, mode)
            animator.create_progress_animation(current_mode, mode, steps)

        transition = manager.switch_mode(target_mode, dry_run=dry_run)

        if output_json:
            result = {
                "from_mode": transition.from_mode.value,
                "to_mode": transition.to_mode.value,
                "success": transition.success,
                "duration": str(transition.duration),
                "changes": transition.changes_applied,
            }
            click.echo(json.dumps(result, indent=2))
        else:
            if dry_run:
                click.echo(click.style("🔍 Mode Switch Preview", fg="yellow", bold=True))
            else:
                click.echo(click.style("🎭 Switching System Mode", fg="cyan", bold=True))

            click.echo()
            click.echo(
                f"From: {transition.from_mode.value} → To: {transition.to_mode.value}"
            )
            click.echo()

            if transition.success:
                click.echo(click.style("✅ Changes applied:", fg="green"))
                for change in transition.changes_applied[:10]:
                    click.echo(f"  • {change}")
                if len(transition.changes_applied) > 10:
                    click.echo(f"  ... and {len(transition.changes_applied) - 10} more")

                if not dry_run:
                    click.echo()
                    click.echo(
                        click.style(
                            f"✨ {mode.upper()} mode activated!", fg="green", bold=True
                        )
                    )
            else:
                click.echo(click.style("❌ Mode switch failed", fg="red"))

    except Exception as e:
        click.echo(click.style(f"Error: {str(e)}", fg="red"), err=True)
        raise click.ClickException(str(e))


@modes.command()
@click.option("--json", "output_json", is_flag=True, help="Output as JSON")
def current(output_json: bool):
    """Show current system mode"""
    try:
        manager = SystemModeManager()
        current_mode = manager.current_mode
        profile = manager.profiles[current_mode]

        if output_json:
            result = {
                "mode": current_mode.value,
                "description": profile.description,
                "cpu_governor": profile.cpu_governor,
                "gpu_profile": profile.gpu_profile,
                "services_enabled": profile.enable_services,
                "services_disabled": profile.disable_services,
            }
            click.echo(json.dumps(result, indent=2))
        else:
            click.echo(
                click.style(
                    f"🎭 Current Mode: {current_mode.value.upper()}",
                    fg="cyan",
                    bold=True,
                )
            )
            click.echo()
            click.echo(f"📝 {profile.description}")
            click.echo()
            click.echo("⚙️ Settings:")
            click.echo(f"  CPU: {profile.cpu_governor}")
            click.echo(f"  GPU: {profile.gpu_profile}")
            click.echo(f"  Memory swappiness: {profile.memory_swappiness}")

            if profile.enable_services:
                click.echo()
                click.echo("✅ Enabled services:")
                for service in profile.enable_services[:3]:
                    click.echo(f"  • {service}")

    except Exception as e:
        click.echo(click.style(f"Error: {str(e)}", fg="red"), err=True)
        raise click.ClickException(str(e))


@modes.command()
@click.option("--json", "output_json", is_flag=True, help="Output as JSON")
def recommend(output_json: bool):
    """Get mode recommendations based on context"""
    try:
        manager = SystemModeManager()
        recommendations = manager.get_mode_recommendations()

        if output_json:
            result = [
                {"mode": mode.value, "reason": reason}
                for mode, reason in recommendations
            ]
            click.echo(json.dumps(result, indent=2))
        else:
            click.echo(click.style("💡 Mode Recommendations", fg="cyan", bold=True))
            click.echo()

            if recommendations:
                for mode, reason in recommendations:
                    icon = {
                        SystemMode.WORK: "💼",
                        SystemMode.GAMING: "🎮",
                        SystemMode.BATTERY_SAVER: "🔋",
                        SystemMode.PRESENTATION: "📊",
                        SystemMode.QUIET: "🤫",
                    }.get(mode, "⚡")

                    click.echo(f"{icon} {mode.value.upper()}")
                    click.echo(f"   Reason: {reason}")
                    click.echo()
            else:
                click.echo("No specific recommendations at this time")

    except Exception as e:
        click.echo(click.style(f"Error: {str(e)}", fg="red"), err=True)
        raise click.ClickException(str(e))


@modes.command()
@click.argument("mode", type=click.Choice([m.value for m in SystemMode]))
@click.argument("time")
def schedule(mode: str, time: str):
    """Schedule a mode switch for specific time"""
    try:
        manager = SystemModeManager()
        target_mode = SystemMode(mode)

        # Parse time (simplified - would need better parsing)
        if ":" in time:
            hour, minute = map(int, time.split(":"))
            scheduled_time = datetime.now().replace(hour=hour, minute=minute)
            if scheduled_time < datetime.now():
                scheduled_time += timedelta(days=1)
        else:
            # Assume hours from now
            hours = int(time)
            scheduled_time = datetime.now() + timedelta(hours=hours)

        success = manager.schedule_mode_switch(target_mode, scheduled_time)

        if success:
            click.echo(click.style("⏰ Mode switch scheduled", fg="green"))
            click.echo(f"Mode: {mode}")
            click.echo(f"Time: {scheduled_time.strftime('%Y-%m-%d %H:%M')}")
        else:
            click.echo(click.style("Failed to schedule mode switch", fg="red"))

    except Exception as e:
        click.echo(click.style(f"Error: {str(e)}", fg="red"), err=True)
        raise click.ClickException(str(e))


@modes.command()
@click.option("--quick", is_flag=True, help="Quick mode with defaults")
@click.option("--export", "export_config", is_flag=True, help="Export as NixOS config")
def wizard(quick: bool, export_config: bool):
    """Interactive wizard to find your perfect mode"""
    try:
        wizard = SystemModeWizard()

        if quick:
            # Use defaults for quick mode
            click.echo(click.style("🧙 Quick Mode Wizard", fg="cyan", bold=True))
            click.echo("Using intelligent defaults...")
            click.echo()

            recommendation = wizard.run_wizard()
        else:
            # Interactive mode (simplified for now)
            click.echo(click.style("🧙 System Mode Wizard", fg="cyan", bold=True))
            click.echo("Let's find your perfect system mode...")
            click.echo()

            # For now, use some predefined answers
            answers = {
                WizardQuestion.WORK_TYPE: "developer",
                WizardQuestion.PRIORITIES: ["performance", "stability"],
                WizardQuestion.AUTOMATION: "guided",
            }
            recommendation = wizard.run_wizard(answers)

        # Display recommendation
        click.echo(
            click.style("✨ Your Perfect Mode Configuration", fg="green", bold=True)
        )
        click.echo()
        click.echo(f"🎯 Primary Mode: {recommendation.primary_mode.upper()}")
        click.echo(f"📊 Confidence: {recommendation.confidence:.0%}")
        click.echo()

        click.echo(click.style("💡 Reasoning:", fg="yellow"))
        click.echo(f"  {recommendation.reasoning}")
        click.echo()

        if recommendation.alternative_modes:
            click.echo(click.style("🔄 Alternative Modes:", fg="cyan"))
            for mode in recommendation.alternative_modes[:3]:
                click.echo(f"  • {mode}")
            click.echo()

        if recommendation.schedule:
            click.echo(click.style("⏰ Recommended Schedule:", fg="magenta"))
            for time, mode in list(recommendation.schedule.items())[:5]:
                click.echo(f"  {time} → {mode}")
            click.echo()

        if recommendation.customizations:
            click.echo(click.style("⚙️ Custom Settings:", fg="blue"))
            for key, value in list(recommendation.customizations.items())[:5]:
                click.echo(f"  • {key}: {value}")

        if export_config:
            click.echo()
            click.echo(click.style("📝 NixOS Configuration:", fg="white", bold=True))
            click.echo("-" * 40)
            config = wizard.export_configuration(recommendation)
            click.echo(config)

    except Exception as e:
        click.echo(click.style(f"Error: {str(e)}", fg="red"), err=True)
        raise click.ClickException(str(e))
