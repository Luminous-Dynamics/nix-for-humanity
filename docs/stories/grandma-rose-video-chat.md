# 👵 User Story: Grandma Rose Wants to Video Chat

**Persona**: Grandma Rose (75)
**Goal**: Video chat with grandchildren
**Technical Level**: Beginner
**Preferred Input**: Voice

## The Story

Rose's daughter just texted: "Mom, the kids want to video chat with you!"

Rose walks to her computer, a bit nervous. She's heard about Skype and Zoom but isn't sure which to use or how to install them.

## The Conversation

**Rose** (speaking to computer): "I need to video chat with my grandkids"

**Nix for Humanity**: "I'd be happy to help you video chat with your grandkids! There are a few good options. Zoom is very popular and what many families use. Would you like me to set up Zoom for you?"

**Rose**: "Is that the one everyone uses? Yes, that sounds good"

**Nix for Humanity**: "Perfect! I'll install Zoom for you. This will take about 2 minutes. Once it's ready, you'll see a new icon on your desktop called 'Zoom'."

*[Installation happens in background with progress indicator]*

**Nix for Humanity**: "Great news! Zoom is ready. Would you like me to help you start your first video call?"

**Rose**: "Yes please! My daughter sent me something about a meeting ID?"

**Nix for Humanity**: "That's exactly what you need! When you open Zoom, look for a button that says 'Join Meeting' and click it. Then you can type in that meeting ID your daughter sent. Shall I open Zoom for you now?"

**Rose**: "Yes, open it"

*[Zoom opens]*

**Nix for Humanity**: "Zoom is open! Click the blue 'Join Meeting' button, then type the meeting ID your daughter sent you. Make sure your camera and microphone are on - you'll see little icons at the bottom of the screen."

**Rose**: "Oh, I see it! Thank you so much!"

## What Happened Behind the Scenes

1. **Intent Recognition**: Understood "video chat with grandkids" as needing video conferencing software
2. **Context Awareness**: Recognized this is a family use case, suggested popular option
3. **Simplification**: Didn't overwhelm with multiple options or technical details
4. **Guidance**: Provided step-by-step help without being condescending
5. **Follow-through**: Offered to help with the actual call, not just installation

## Learning for Next Time

The system learned:
- Rose prefers voice interaction
- She responds well to simple, direct guidance
- She has family video chat needs
- She may need help with meeting IDs in the future

Next time Rose says "video chat," the system will:
- Remember she uses Zoom
- Offer to open it directly
- Maybe remind her about the meeting ID if it's been a while

## Technical Details (Hidden from Rose)

```bash
# What actually executed
nix-env -iA nixpkgs.zoom-us

# Or in configuration.nix (if that's her preference)
environment.systemPackages = with pkgs; [
  zoom-us
];
```

## Success Metrics

- ✅ Task completed successfully
- ✅ User confidence maintained
- ✅ No technical jargon used
- ✅ Emotional goal achieved (connecting with family)
- ✅ Learning captured for future interactions

## Key Takeaways

This story demonstrates:
1. **Natural language works** - Rose never needed to know package names
2. **Context matters** - Understanding the human goal (family connection)
3. **Progressive help** - Not just installing, but helping her succeed
4. **Appropriate complexity** - Technical details hidden but available
5. **Learning relationship** - Each interaction improves future ones

---

*"Technology should bring families together, not create barriers."*