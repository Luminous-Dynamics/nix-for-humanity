#!/usr/bin/env python3
"""
Secure Voice Interface - Production-Safe Voice Control
Integrates all security components for safe deployment
"""

import json
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any

from luminous_nix.voice.production_voice_interface import ProductionVoiceInterface
from luminous_nix.voice.secret_redactor import SecretRedactor
from luminous_nix.voice.tier_policy import TierPolicyChecker
from luminous_nix.voice.startup_posture import print_startup_banner
from luminous_nix.voice.posture_stamp import write_posture_stamp
from luminous_nix.voice.dry_run_mode import is_dry_run_enabled, simulate_tier2_approval


class SecureVoiceInterface(ProductionVoiceInterface):
    """
    Production-safe voice interface with security gates

    Security Features:
    - Tier 0-1 only via voice (search, list, help, status)
    - Tier 2+ require typed modal approval
    - Secrets redacted before TTS
    - Audit logging of all interactions
    - Rate limiting and replay protection
    """

    def __init__(self, *args, audit_file: Optional[Path] = None, **kwargs):
        super().__init__(*args, **kwargs)

        # Security components
        self.redactor = SecretRedactor(enabled=True)
        self.policy_checker = TierPolicyChecker()

        # Audit logging
        self.audit_file = audit_file or Path("voice-audit.jsonl")
        self.session_id = hashlib.sha256(
            f"{datetime.now().isoformat()}".encode()
        ).hexdigest()[:12]

        # Rate limiting
        self.command_times = []
        self.max_commands_per_minute = 20

    def speak(self, text: str, wait: bool = True):
        """TTS with automatic secret redaction"""
        # CRITICAL: Redact secrets before speaking
        result = self.redactor.redact(text)

        if result.was_redacted:
            # Log redaction event
            self._audit_log(
                {
                    "event": "secret_redacted",
                    "secret_types": result.secret_types,
                    "original_length": len(text),
                }
            )

            # Speak generic refusal
            super().speak(result.text, wait)
        else:
            # Safe to speak
            super().speak(text, wait)

    def execute_command(self, command_text: str) -> tuple[str, bool]:
        """Execute with tier checking and approval flow"""

        # Rate limiting check
        if not self._check_rate_limit():
            self.speak("Too many requests. Please wait a moment.")
            return "", False

        # CRITICAL: Check tier policy
        decision = self.policy_checker.check_policy(command_text)

        # Audit the attempt
        self._audit_log(
            {
                "event": "command_attempt",
                "command": command_text,
                "tier": decision.tier,
                "allowed": decision.allowed,
                "reason": decision.reason,
            }
        )

        if not decision.allowed:
            # Tier 2+ requires approval
            if decision.tier >= 2:
                # NEW: Check if dry-run mode enabled
                if is_dry_run_enabled():
                    self.speak("Dry-run mode: Simulating approval flow.")
                    result = simulate_tier2_approval(
                        command=command_text,
                        tier=decision.tier,
                        capability=getattr(decision, "capability", "unknown"),
                        diff_id="dry-run-"
                        + hashlib.sha256(command_text.encode()).hexdigest()[:8],
                        policy_hash="dry-run-policy",
                        nonce=decision.approval_code,
                        recovery_command="<dry-run-no-undo>",
                        user_approved=True,
                    )
                    self.speak(result["message"])
                    return result["message"], result["success"]

                # IMPORTANT: Never speak the approval code
                self.speak("That needs a confirmation in the window.")

                print(f"\n⚠️  Tier {decision.tier} Operation Requires Approval")
                print(f"📝 Confirmation code: {decision.approval_code}")
                print(f"⏱️  Code expires in 30 seconds")
                print(f"💡 Type the code in the modal to proceed")

                # Log approval request
                self._audit_log(
                    {
                        "event": "approval_required",
                        "tier": decision.tier,
                        "approval_code_issued": decision.approval_code,
                    }
                )

                # Return blocked
                return "", False

            # Other blocking reason
            self.speak(decision.reason or "Command not allowed.")
            return "", False

        # Tier 0-1: Execute directly
        result_text, success = super().execute_command(command_text)

        # Log execution
        self._audit_log(
            {
                "event": "command_executed",
                "command": command_text,
                "tier": decision.tier,
                "success": success,
            }
        )

        return result_text, success

    def handle_approval(self, typed_code: str, command_text: str) -> tuple[str, bool]:
        """Handle typed approval code from modal"""

        # Check approval code
        intent = self.policy_checker.check_approval_code(typed_code)

        if not intent:
            self.speak("Invalid or expired code. Command cancelled.")
            self._audit_log(
                {
                    "event": "approval_denied",
                    "reason": "invalid_or_expired_code",
                }
            )
            return "", False

        # Code valid - execute command
        self.speak("Code confirmed. Executing command.")
        self._audit_log(
            {
                "event": "approval_granted",
                "code_used": typed_code,
            }
        )

        # Execute with bypassed tier check (already approved)
        result_text, success = super().execute_command(command_text)

        self._audit_log(
            {
                "event": "approved_command_executed",
                "command": command_text,
                "success": success,
            }
        )

        return result_text, success

    def _check_rate_limit(self) -> bool:
        """Check if under rate limit (20 commands/minute)"""
        now = datetime.now().timestamp()

        # Remove commands older than 1 minute
        self.command_times = [t for t in self.command_times if now - t < 60]

        # Check limit
        if len(self.command_times) >= self.max_commands_per_minute:
            self._audit_log({"event": "rate_limit_exceeded"})
            return False

        # Add current command
        self.command_times.append(now)
        return True

    def _audit_log(self, event_data: Dict[str, Any]):
        """Append event to audit log (JSON Lines format)"""
        entry = {
            "ts": datetime.now().isoformat(),
            "session_id": self.session_id,
            "source": "voice",
            **event_data,
        }

        try:
            with open(self.audit_file, "a") as f:
                f.write(json.dumps(entry) + "\n")
        except Exception as e:
            print(f"⚠️  Audit logging error: {e}")


def main():
    """Launch secure voice interface"""
    print("=" * 70)
    print("🔒 Secure Voice Interface - Production Mode")
    print("=" * 70)

    # NEW: Display security posture banner
    print_startup_banner()
    print("=" * 70)

    # NEW: Write posture stamp to file for audit trail
    try:
        stamp_path = write_posture_stamp()
        print(f"📋 Posture stamp written: {stamp_path}")
    except Exception as e:
        print(f"⚠️  Could not write posture stamp: {e}")

    # Check if dry-run mode
    if is_dry_run_enabled():
        print("🔵 DRY-RUN MODE ACTIVE - Commands will be simulated")

    print()
    print("Security Features:")
    print("  • Tier 0-1 only via voice")
    print("  • Secret redaction active")
    print("  • Audit logging enabled")
    print("  • Rate limiting: 20/minute")
    print("=" * 70)

    interface = SecureVoiceInterface(audit_file=Path("voice-audit.jsonl"))

    interface.interactive_mode()


if __name__ == "__main__":
    main()
