"""
Developer Tools Integration for Beautiful Demos and Documentation
Integrates asciinema, gum, charm-freeze, and vhs for stunning presentations
"""

import subprocess
import json
import tempfile
import asyncio
from pathlib import Path
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

@dataclass
class RecordingConfig:
    """Configuration for terminal recordings"""
    title: str = "Luminous Nix Demo"
    idle_time_limit: float = 2.0  # Max idle time in recording
    theme: str = "monokai"  # Terminal theme
    font_size: int = 14
    width: int = 80
    height: int = 24
    

class AsciinemaRecorder:
    """Create terminal recordings with asciinema"""
    
    def __init__(self, config: Optional[RecordingConfig] = None):
        self.config = config or RecordingConfig()
        self.recording_path: Optional[Path] = None
        
    async def start_recording(self, output_path: Optional[Path] = None) -> Path:
        """Start recording terminal session"""
        self.recording_path = output_path or Path(tempfile.mktemp(suffix=".cast"))
        
        cmd = [
            "asciinema", "rec",
            "--title", self.config.title,
            "--idle-time-limit", str(self.config.idle_time_limit),
            str(self.recording_path)
        ]
        
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        logger.info(f"Recording started: {self.recording_path}")
        return self.recording_path
        
    async def stop_recording(self):
        """Stop current recording"""
        # Send Ctrl+D to stop
        # In practice, this would be handled by the terminal
        logger.info("Recording stopped")
        
    async def play_recording(self, cast_path: Path):
        """Play back a recording"""
        cmd = ["asciinema", "play", str(cast_path)]
        
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        await process.communicate()
        
    async def upload_recording(self, cast_path: Path) -> str:
        """Upload recording to asciinema.org"""
        cmd = ["asciinema", "upload", str(cast_path)]
        
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await process.communicate()
        
        # Parse URL from output
        output = stdout.decode()
        if "https://asciinema.org" in output:
            url = [line for line in output.split('\n') if "https://asciinema.org" in line][0]
            return url.strip()
        return ""
        

class GumInterface:
    """Beautiful CLI interactions with Charm's Gum"""
    
    @staticmethod
    async def choose(options: List[str], header: str = "Choose an option:") -> str:
        """Present a selection menu"""
        cmd = ["gum", "choose", "--header", header] + options
        
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, _ = await process.communicate()
        return stdout.decode().strip()
        
    @staticmethod
    async def input(prompt: str, placeholder: str = "") -> str:
        """Get user input with beautiful prompt"""
        cmd = ["gum", "input", "--prompt", prompt]
        if placeholder:
            cmd.extend(["--placeholder", placeholder])
            
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, _ = await process.communicate()
        return stdout.decode().strip()
        
    @staticmethod
    async def confirm(prompt: str) -> bool:
        """Get yes/no confirmation"""
        cmd = ["gum", "confirm", prompt]
        
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        await process.communicate()
        return process.returncode == 0
        
    @staticmethod
    async def spin(command: List[str], title: str = "Processing...") -> Tuple[str, int]:
        """Show spinner while running command"""
        cmd = ["gum", "spin", "--title", title, "--"] + command
        
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await process.communicate()
        return stdout.decode(), process.returncode
        
    @staticmethod
    async def style(text: str, **kwargs) -> str:
        """Style text with colors and formatting"""
        cmd = ["gum", "style"]
        
        # Add style flags
        if kwargs.get("bold"):
            cmd.append("--bold")
        if kwargs.get("italic"):
            cmd.append("--italic")
        if kwargs.get("underline"):
            cmd.append("--underline")
        if "foreground" in kwargs:
            cmd.extend(["--foreground", kwargs["foreground"]])
        if "background" in kwargs:
            cmd.extend(["--background", kwargs["background"]])
        if "border" in kwargs:
            cmd.extend(["--border", kwargs["border"]])
        if "padding" in kwargs:
            cmd.extend(["--padding", kwargs["padding"]])
            
        cmd.append(text)
        
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, _ = await process.communicate()
        return stdout.decode()
        

class CharmFreeze:
    """Generate beautiful code screenshots"""
    
    @staticmethod
    async def freeze_code(
        code_path: Path,
        output_path: Optional[Path] = None,
        language: Optional[str] = None,
        theme: str = "dracula"
    ) -> Path:
        """Generate PNG screenshot of code"""
        output = output_path or Path(tempfile.mktemp(suffix=".png"))
        
        cmd = [
            "freeze",
            str(code_path),
            "--output", str(output),
            "--theme", theme
        ]
        
        if language:
            cmd.extend(["--language", language])
            
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        await process.communicate()
        
        logger.info(f"Generated code screenshot: {output}")
        return output
        
    @staticmethod
    async def freeze_text(
        text: str,
        output_path: Optional[Path] = None,
        language: str = "python"
    ) -> Path:
        """Generate screenshot from text"""
        # Write text to temp file
        temp_file = Path(tempfile.mktemp(suffix=f".{language}"))
        temp_file.write_text(text)
        
        try:
            output = await CharmFreeze.freeze_code(temp_file, output_path, language)
            return output
        finally:
            temp_file.unlink()
            

class VHSRecorder:
    """Programmatic terminal recordings with VHS"""
    
    @staticmethod
    async def create_tape(commands: List[str], output_path: Optional[Path] = None) -> Path:
        """Create VHS tape file for recording"""
        tape_path = output_path or Path(tempfile.mktemp(suffix=".tape"))
        
        # VHS tape format
        tape_content = """
Output demo.gif

Set FontSize 14
Set Width 1200
Set Height 600
Set Theme "Dracula"

"""
        
        for cmd in commands:
            if cmd.startswith("Type"):
                tape_content += f'{cmd}\n'
            elif cmd.startswith("Sleep"):
                tape_content += f'{cmd}\n'
            elif cmd.startswith("Enter"):
                tape_content += 'Enter\n'
            else:
                tape_content += f'Type "{cmd}"\n'
                tape_content += 'Enter\n'
                tape_content += 'Sleep 1s\n'
                
        tape_path.write_text(tape_content)
        return tape_path
        
    @staticmethod
    async def record_from_tape(tape_path: Path) -> Path:
        """Record GIF from VHS tape"""
        cmd = ["vhs", str(tape_path)]
        
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await process.communicate()
        
        # VHS outputs to demo.gif by default
        output_path = Path("demo.gif")
        if output_path.exists():
            logger.info(f"Generated recording: {output_path}")
            return output_path
        else:
            logger.error(f"VHS recording failed: {stderr.decode()}")
            raise RuntimeError("VHS recording failed")
            

class DemoOrchestrator:
    """Orchestrate beautiful demos using all tools"""
    
    def __init__(self):
        self.asciinema = AsciinemaRecorder()
        self.gum = GumInterface()
        self.freeze = CharmFreeze
        self.vhs = VHSRecorder
        
    async def create_interactive_demo(self):
        """Create an interactive demo session"""
        
        # Welcome message
        welcome = await self.gum.style(
            "Welcome to Luminous Nix Demo!",
            bold=True,
            foreground="212",
            border="rounded",
            padding="1 4"
        )
        print(welcome)
        
        # Choose demo type
        demo_type = await self.gum.choose(
            ["Installation Demo", "Configuration Demo", "Voice Demo", "TUI Demo"],
            "What would you like to see?"
        )
        
        # Start recording
        if await self.gum.confirm("Would you like to record this demo?"):
            recording = await self.asciinema.start_recording()
            print(f"📹 Recording to {recording}")
            
        # Run chosen demo
        if demo_type == "Installation Demo":
            await self._run_installation_demo()
        elif demo_type == "Configuration Demo":
            await self._run_configuration_demo()
        elif demo_type == "Voice Demo":
            await self._run_voice_demo()
        elif demo_type == "TUI Demo":
            await self._run_tui_demo()
            
        # Stop recording and offer upload
        if recording:
            await self.asciinema.stop_recording()
            if await self.gum.confirm("Upload recording to asciinema.org?"):
                url = await self.asciinema.upload_recording(recording)
                print(f"🌐 Recording available at: {url}")
                
    async def _run_installation_demo(self):
        """Demo package installation"""
        package = await self.gum.input(
            "Enter package name:",
            placeholder="firefox"
        )
        
        # Show processing
        output, _ = await self.gum.spin(
            ["./bin/ask-nix", f"install {package}"],
            f"Installing {package}..."
        )
        
        print(output)
        
    async def _run_configuration_demo(self):
        """Demo configuration generation"""
        config_type = await self.gum.choose(
            ["Web Server", "Development Environment", "Desktop Setup"],
            "Choose configuration type:"
        )
        
        # Generate config
        output, _ = await self.gum.spin(
            ["./bin/ask-nix", f"generate {config_type} config"],
            f"Generating {config_type} configuration..."
        )
        
        # Take screenshot of generated config
        if output:
            screenshot = await self.freeze.freeze_text(output, language="nix")
            print(f"📸 Screenshot saved: {screenshot}")
            
    async def _run_voice_demo(self):
        """Demo voice interaction"""
        print("🎤 Voice demo would run here (requires microphone)")
        # In real implementation, would use voice_engine
        
    async def _run_tui_demo(self):
        """Demo TUI interface"""
        # Create VHS tape for TUI demo
        commands = [
            "./bin/nix-tui",
            "Sleep 2s",
            "Type /search firefox",
            "Enter",
            "Sleep 2s",
            "Type q"
        ]
        
        tape = await self.vhs.create_tape(commands)
        gif = await self.vhs.record_from_tape(tape)
        print(f"🎬 TUI demo saved: {gif}")
        

# Integration script for demos
async def create_luminous_nix_demo():
    """Create a complete demo of Luminous Nix capabilities"""
    
    orchestrator = DemoOrchestrator()
    await orchestrator.create_interactive_demo()
    

if __name__ == "__main__":
    # Run demo when called directly
    asyncio.run(create_luminous_nix_demo())