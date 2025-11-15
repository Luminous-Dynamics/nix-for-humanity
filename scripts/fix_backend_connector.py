#!/usr/bin/env python3
"""
Fix all sacred/consciousness references in backend_connector.py
"""

from pathlib import Path

# Get the file
file_path = Path(__file__).parent.parent / "src/luminous_nix/ui/backend_connector.py"
content = file_path.read_text()

# Replace sacred timer
content = content.replace(
    "self.operation_timer = SacredTimer(KairosMode.FLOW)",
    "# self.operation_timer = SacredTimer(KairosMode.FLOW)  # ARCHIVED",
)

# Replace consciousness field calls
replacements = [
    (
        "field_state = consciousness_field.sense_field()",
        'field_state = "balanced"  # Default',
    ),
    ("coherence = consciousness_field.coherence_level", "coherence = 0.5  # Default"),
    (
        "consciousness_field.sacred_pause(2.0)",
        "# consciousness_field.sacred_pause(2.0)  # ARCHIVED",
    ),
    ('"coherence": consciousness_field.coherence_level', '"coherence": 0.5  # Default'),
    ('"state": consciousness_field.sense_field()', '"state": "balanced"  # Default'),
    (
        '"user_state": consciousness_field.user_state',
        '"user_state": "active"  # Default',
    ),
    (
        '"needs_pause": consciousness_field.needs_pause()',
        '"needs_pause": False  # Default',
    ),
    (
        '"time_since_pause": time.time() - consciousness_field.last_sacred_pause',
        '"time_since_pause": 0  # Default',
    ),
]

for old, new in replacements:
    content = content.replace(old, new)

# Write back
file_path.write_text(content)
print("✅ Fixed backend_connector.py - removed all sacred/consciousness references")
