#!/usr/bin/env python3
"""
Security Auditor CLI Commands
Proactive security scanning using HRM
"""

import click
import json
from datetime import datetime
from luminous_nix.ai.advanced_features.security_auditor import SecurityAuditor, Severity


def format_severity(severity: Severity) -> str:
    """Format severity with color"""
    colors = {
        Severity.CRITICAL: 'red',
        Severity.HIGH: 'yellow',
        Severity.MEDIUM: 'blue',
        Severity.LOW: 'green',
    }
    return click.style(severity.value.upper(), fg=colors.get(severity, 'white'), bold=True)


@click.group()
@click.pass_context
def security(ctx):
    """🔐 Security auditing and hardening
    
    Uses AI to scan for vulnerabilities, check CVEs, and suggest hardening configs.
    Proactive security monitoring for your NixOS system.
    """
    ctx.ensure_object(dict)
    ctx.obj['security'] = SecurityAuditor()


@security.command()
@click.option('--deep', is_flag=True, help='Perform deep security scan')
@click.option('--json', 'json_output', is_flag=True, help='Output in JSON format')
@click.pass_context
def audit(ctx, deep, json_output):
    """Run comprehensive security audit
    
    Examples:
        luminous-nix security audit
        luminous-nix security audit --deep
    """
    auditor = ctx.obj['security']
    
    scan_type = "deep" if deep else "standard"
    if not json_output:
        click.secho(f"🔐 Running Security Audit ({scan_type})...", fg='cyan', bold=True)
    
    audit_result = auditor.audit_system(deep_scan=deep)
    
    if json_output:
        output = {
            'scan_date': audit_result.scan_date.isoformat(),
            'packages_scanned': audit_result.total_packages_scanned,
            'critical': audit_result.critical_count,
            'high': audit_result.high_count,
            'medium': audit_result.medium_count,
            'low': audit_result.low_count,
            'security_score': audit_result.security_score,
            'risk_level': audit_result.risk_level
        }
        click.echo(json.dumps(output, indent=2))
    else:
        click.echo()
        
        # Score color based on level
        score = audit_result.security_score
        if score >= 80:
            score_color = 'green'
        elif score >= 60:
            score_color = 'yellow'
        else:
            score_color = 'red'
        
        click.echo("Security Score: ", nl=False)
        click.secho(f"{score:.0f}/100", fg=score_color, bold=True)
        click.echo(f"Risk Level: {audit_result.risk_level.upper()}")
        click.echo(f"Packages Scanned: {audit_result.total_packages_scanned}")
        
        # Vulnerability summary
        total_vulns = (audit_result.critical_count + audit_result.high_count + 
                      audit_result.medium_count + audit_result.low_count)
        
        if total_vulns > 0:
            click.echo()
            click.secho(f"Vulnerabilities Found ({total_vulns}):", bold=True)
            
            if audit_result.critical_count > 0:
                click.echo("  • ", nl=False)
                click.secho(f"Critical: {audit_result.critical_count}", fg='red', bold=True)
            
            if audit_result.high_count > 0:
                click.echo("  • ", nl=False)
                click.secho(f"High: {audit_result.high_count}", fg='yellow', bold=True)
            
            if audit_result.medium_count > 0:
                click.echo("  • ", nl=False)
                click.secho(f"Medium: {audit_result.medium_count}", fg='blue', bold=True)
            
            if audit_result.low_count > 0:
                click.echo("  • ", nl=False)
                click.secho(f"Low: {audit_result.low_count}", fg='green', bold=True)
            
            # Show top vulnerabilities
            if audit_result.vulnerabilities_found:
                click.echo()
                click.secho("Top Issues:", bold=True)
                for vuln in audit_result.vulnerabilities_found[:5]:
                    click.echo(f"  • {vuln.cve_id}: {vuln.package} (", nl=False)
                    click.echo(format_severity(vuln.severity), nl=False)
                    click.echo(")")
                    click.echo(f"    {vuln.description}")
        else:
            click.echo()
            click.secho("✅ No vulnerabilities found!", fg='green', bold=True)
        
        # Configuration status
        click.echo()
        click.secho("Security Configuration:", bold=True)
        
        configs = [
            ("Firewall", audit_result.firewall_enabled),
            ("Auto-Updates", audit_result.auto_updates_enabled),
            ("Secure Boot", audit_result.secure_boot),
            ("Disk Encryption", audit_result.encrypted_root)
        ]
        
        for name, enabled in configs:
            if enabled:
                click.echo(f"  • {name}: ", nl=False)
                click.secho("✅", fg='green')
            else:
                click.echo(f"  • {name}: ", nl=False)
                click.secho("❌", fg='red')
        
        # Immediate actions
        if audit_result.immediate_actions:
            click.echo()
            click.secho("Immediate Actions Required:", fg='red', bold=True)
            for action in audit_result.immediate_actions[:5]:
                click.echo(f"  ! {action}")
        
        # Configuration fixes
        if audit_result.configuration_fixes:
            click.echo()
            click.secho("Recommended Configuration:", fg='yellow')
            click.echo("```nix")
            for fix in audit_result.configuration_fixes[:5]:
                click.echo(f"  {fix}")
            click.echo("```")


@security.command()
@click.argument('package')
@click.option('--json', 'json_output', is_flag=True, help='Output in JSON format')
@click.pass_context
def check(ctx, package, json_output):
    """Check specific package for known vulnerabilities
    
    Examples:
        luminous-nix security check openssl
        luminous-nix security check firefox
        luminous-nix security check kernel
    """
    auditor = ctx.obj['security']
    
    if not json_output:
        click.secho(f"🔍 Checking Security of '{package}'...", fg='cyan', bold=True)
    
    vulnerabilities = auditor.check_package_security(package)
    
    if json_output:
        output = [{
            'cve_id': v.cve_id,
            'severity': v.severity.value,
            'description': v.description,
            'fixed_version': v.fixed_version,
            'patch_available': v.patch_available
        } for v in vulnerabilities]
        click.echo(json.dumps(output, indent=2))
    else:
        click.echo()
        
        if vulnerabilities:
            click.secho(f"⚠️ {len(vulnerabilities)} vulnerabilities found:", fg='yellow', bold=True)
            
            for vuln in vulnerabilities:
                click.echo()
                click.echo(f"  {vuln.cve_id} (", nl=False)
                click.echo(format_severity(vuln.severity), nl=False)
                click.echo(")")
                click.echo(f"    {vuln.description}")
                
                if vuln.fixed_version:
                    click.echo("    ", nl=False)
                    click.secho(f"Fix: Update to {vuln.fixed_version}", fg='green')
                elif vuln.workaround:
                    click.echo("    ", nl=False)
                    click.secho(f"Workaround: {vuln.workaround}", fg='yellow')
        else:
            click.secho("✅ No known vulnerabilities", fg='green', bold=True)


@security.command()
@click.option('--json', 'json_output', is_flag=True, help='Output in JSON format')
@click.pass_context
def harden(ctx, json_output):
    """Generate system hardening configuration
    
    Example:
        luminous-nix security harden
    """
    auditor = ctx.obj['security']
    
    if not json_output:
        click.secho("🛡️ Generating Hardening Configuration...", fg='cyan', bold=True)
    
    hardening = auditor.suggest_hardening()
    
    if json_output:
        click.echo(json.dumps(hardening, indent=2))
    else:
        click.echo()
        click.secho("System Hardening Configuration:", bold=True)
        click.echo()
        click.echo("```nix")
        click.echo(hardening['configuration'])
        click.echo("```")
        
        if hardening.get('impact'):
            click.echo()
            click.secho("Impact Assessment:", bold=True)
            for aspect, impact in hardening['impact'].items():
                color = 'green' if impact == 'minimal' else 'yellow' if impact == 'moderate' else 'red'
                click.echo(f"  • {aspect.capitalize()}: ", nl=False)
                click.secho(impact, fg=color)
        
        if hardening.get('priority'):
            click.echo()
            click.secho("Priority Actions:", bold=True)
            for i, action in enumerate(hardening['priority'][:5], 1):
                click.echo(f"  {i}. {action}")


@security.command()
@click.option('--json', 'json_output', is_flag=True, help='Output in JSON format')
@click.pass_context
def updates(ctx, json_output):
    """Check for security updates
    
    Example:
        luminous-nix security updates
    """
    auditor = ctx.obj['security']
    
    if not json_output:
        click.secho("🔄 Checking for Security Updates...", fg='cyan', bold=True)
    
    updates_list = auditor.track_security_updates()
    
    if json_output:
        click.echo(json.dumps(updates_list, indent=2))
    else:
        click.echo()
        
        if updates_list:
            click.secho(f"⚠️ {len(updates_list)} security updates available:", fg='yellow', bold=True)
            
            for update in updates_list[:10]:
                click.echo(f"  • {update.get('package', 'Unknown')}: {update.get('version', 'N/A')}")
            
            click.echo()
            click.secho("Apply updates:", fg='green')
            click.echo("  sudo nixos-rebuild switch --upgrade")
        else:
            click.secho("✅ System appears up to date", fg='green', bold=True)