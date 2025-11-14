"""
Posture Stamp - Record security configuration at service start

Writes startup security posture to file for audit trail and artifact attachment.
Critical for demonstrating what configuration was active during incidents.
"""

import os
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, Any

from .startup_posture import get_effective_config, determine_posture


def write_posture_stamp(
    output_path: Path = None, include_timestamp: bool = True
) -> Path:
    """
    Write security posture stamp file at service startup.

    Args:
        output_path: Where to write the posture stamp (default: logs/posture.txt or /var/log/luminous-voice/posture.txt if root)
        include_timestamp: Whether to include timestamp in filename

    Returns:
        Path to written file
    """
    # Determine default output path based on permissions
    if output_path is None:
        if os.getuid() == 0:  # Running as root
            output_path = Path("/var/log/luminous-voice/posture.txt")
        else:  # Running as normal user (dev/rc mode)
            output_path = Path("logs/posture.txt")

    # Ensure directory exists (with fallback for permission errors)
    try:
        output_path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    except PermissionError:
        # Fallback to local logs directory if system path fails
        output_path = Path("logs") / output_path.name
        output_path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)

    # Add timestamp to filename if requested
    if include_timestamp:
        ts = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
        stem = output_path.stem
        suffix = output_path.suffix
        output_path = output_path.parent / f"{stem}-{ts}{suffix}"

    config = get_effective_config()
    posture = determine_posture(config)

    # Build stamp content
    lines = [
        "=" * 70,
        "LUMINOUS VOICE - SECURITY POSTURE STAMP",
        "=" * 70,
        "",
        f"Timestamp (UTC): {datetime.now(timezone.utc).isoformat()}",
        f"Service Start: {datetime.now().isoformat()}",
        f"Hostname: {os.uname().nodename}",
        f"PID: {os.getpid()}",
        "",
        f"Overall Posture: {posture}",
        "",
        "CONFIGURATION",
        "-" * 70,
        f"Tier Max:            {config['tier_max']}",
        f"Allowed Tiers:       {config['allowed_tiers']}",
        f"PTT Required:        {'YES' if config['ptt_required'] else 'NO'}",
        f"Voice Approvals:     {'DISABLED' if config['approvals_disabled'] else 'ENABLED'}",
        f"Voice Disabled:      {'YES' if config['voice_disabled'] else 'NO'}",
        "",
        "QUALITY GATES",
        "-" * 70,
        f"ASR Confidence Min:  {config['min_asr_confidence']:.2f}",
        f"Max Noise Level:     {config['max_noise_level']:.2f}",
        f"Min VAD Score:       {config['min_vad_score']:.2f}",
        "",
        "PROTECTION",
        "-" * 70,
        f"Secret Redaction:    {'ENABLED' if config['redact_secrets'] else 'DISABLED'}",
        f"Wake During TTS:     {'DISABLED' if config['disable_wake_during_tts'] else 'ENABLED'}",
        "",
        "AUDIT",
        "-" * 70,
        f"Audit Logging:       {'ENABLED' if config['audit_enabled'] else 'DISABLED'}",
        f"Hash Chain:          {'ENABLED' if config['hash_chain'] else 'ENABLED'}",
        f"Audit Path:          {config['audit_path']}",
        "",
        "POLICY",
        "-" * 70,
        f"Policy Hash:         {config['policy_hash']}...",
        f"Manifest:            {config['manifest_path']}",
        "",
        "ENVIRONMENT OVERRIDES",
        "-" * 70,
    ]

    # Check which settings came from env vars
    env_overrides = []
    if os.getenv("VOICE_DISABLED"):
        env_overrides.append(f"VOICE_DISABLED={os.getenv('VOICE_DISABLED')}")
    if os.getenv("VOICE_TIER_MAX"):
        env_overrides.append(f"VOICE_TIER_MAX={os.getenv('VOICE_TIER_MAX')}")
    if os.getenv("VOICE_PTT_REQUIRED"):
        env_overrides.append(f"VOICE_PTT_REQUIRED={os.getenv('VOICE_PTT_REQUIRED')}")
    if os.getenv("VOICE_APPROVALS_DISABLED"):
        env_overrides.append(
            f"VOICE_APPROVALS_DISABLED={os.getenv('VOICE_APPROVALS_DISABLED')}"
        )
    if os.getenv("VOICE_MIN_ASR_CONF"):
        env_overrides.append(f"VOICE_MIN_ASR_CONF={os.getenv('VOICE_MIN_ASR_CONF')}")
    if os.getenv("VOICE_MAX_NOISE"):
        env_overrides.append(f"VOICE_MAX_NOISE={os.getenv('VOICE_MAX_NOISE')}")

    if env_overrides:
        lines.extend(env_overrides)
    else:
        lines.append("(none - using manifest defaults)")

    lines.extend(
        [
            "",
            "=" * 70,
            "",
            "This posture stamp provides immutable evidence of the security",
            "configuration active at service startup. Attach to incident reports",
            "and release artifacts for audit trail.",
            "",
            "Verification:",
            f"  Policy Hash: {config['policy_hash']}",
            f"  File: {output_path}",
            "",
            "=" * 70,
        ]
    )

    # Write stamp
    content = "\n".join(lines)
    with open(output_path, "w") as f:
        f.write(content)

    # Set restrictive permissions
    os.chmod(output_path, 0o600)

    return output_path


def get_latest_posture_stamp(directory: Path = None) -> Path | None:
    """Get the most recent posture stamp file"""
    if directory is None:
        # Check system log dir first, then local logs
        if os.getuid() == 0:
            directory = Path("/var/log/luminous-voice")
        else:
            directory = Path("logs")

    if not directory.exists():
        return None

    stamps = sorted(directory.glob("posture-*.txt"), reverse=True)
    return stamps[0] if stamps else None


if __name__ == "__main__":
    # CLI usage: python -m luminous_nix.voice.posture_stamp
    stamp_path = write_posture_stamp()
    print(f"✅ Posture stamp written to: {stamp_path}")
    print()
    print("Contents:")
    print("-" * 70)
    with open(stamp_path) as f:
        print(f.read())
