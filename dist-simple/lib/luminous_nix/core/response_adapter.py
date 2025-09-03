"""
from typing import Dict, List, Optional
Response adapter to bridge between simple and enhanced response types
"""

from typing import Any

from ..api.schema import Response as SimpleResponse
from .intents import Intent


def create_simple_response(
    intent: Intent,
    success: bool = True,
    text: str | None = None,
    commands: list[dict[str, Any]] | None = None,
    data: dict[str, Any] | None = None,
    error: str | None = None,
    suggestions: list[str] | None = None,
) -> SimpleResponse:
    """
    Create a simple Response from backend components

    This adapter helps transition from the complex Response structure
    to the simple api.schema.Response that frontends expect.
    """
    # Build response text
    if text:
        response_text = text
    elif error:
        response_text = f"Error: {error}"
        if suggestions:
            response_text += "\n\nSuggestions:\n" + "\n".join(
                f"- {s}" for s in suggestions
            )
    else:
        response_text = f"Recognized intent: {intent.type.value}"

    # Build data dictionary
    response_data = data or {}
    response_data.update(
        {
            "intent_type": intent.type.value,
            "intent_confidence": intent.confidence,
            "intent_entities": intent.entities,
        }
    )

    if error:
        response_data["error"] = error
    if suggestions:
        response_data["suggestions"] = suggestions

    return SimpleResponse(
        success=success, text=response_text, commands=commands or [], data=response_data
    )


def adapt_enhanced_response(enhanced_response) -> SimpleResponse:
    """
    Adapt an enhanced Response to simple Response format

    This handles the enhanced Response from ResponseGenerator
    """
    if hasattr(enhanced_response, "format_for_cli"):
        # This is an enhanced Response with paths
        text = enhanced_response.format_for_cli()

        # Extract commands from all paths
        commands = []
        for path in getattr(enhanced_response, "paths", []):
            for cmd in path.commands:
                if not cmd.startswith("#"):  # Skip comments
                    commands.append({"command": cmd, "description": path.title})

        return SimpleResponse(
            success=True,
            text=text,
            commands=commands,
            data={
                "intent": enhanced_response.intent,
                "has_education": enhanced_response.education is not None,
                "warnings": len(enhanced_response.warnings),
                "paths_count": len(enhanced_response.paths),
            },
        )
    # Unknown response type, do our best
    return SimpleResponse(
        success=True, text=str(enhanced_response), commands=[], data={}
    )
