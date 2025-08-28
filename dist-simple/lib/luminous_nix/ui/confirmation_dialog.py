"""
Sacred confirmation dialogs for consciousness-first execution.

This module provides reusable GUI confirmation prompts that honor user agency
while ensuring mindful action before system modifications.
"""

import tkinter as tk
from tkinter import messagebox, ttk
from typing import Optional, Dict, Any
import subprocess
import sys
from dataclasses import dataclass


@dataclass
class ConfirmationResult:
    """Result of a confirmation dialog"""
    confirmed: bool
    remember_choice: bool = False
    additional_options: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.additional_options is None:
            self.additional_options = {}


class SacredConfirmationDialog:
    """
    A consciousness-first confirmation dialog that respects user agency.
    
    Philosophy:
    - Clear, non-technical language
    - Always show what will happen
    - Never pressure or manipulate
    - Honor the sacred pause before action
    - Accessibility-first design
    """
    
    def __init__(self):
        self.root = None
        self.result = ConfirmationResult(confirmed=False)
        
    def ask(
        self,
        title: str = "Confirmation Required",
        message: str = "Are you sure you want to proceed?",
        command: str = None,
        details: str = None,
        allow_remember: bool = False
    ) -> ConfirmationResult:
        """
        Show a confirmation dialog and return the result.
        
        Args:
            title: Dialog window title
            message: Main question to ask
            command: The actual command that will be executed
            details: Additional details or warnings
            allow_remember: Whether to show "remember my choice" option
            
        Returns:
            ConfirmationResult with user's choice
        """
        try:
            # Try to use tkinter for GUI
            return self._show_gui_dialog(title, message, command, details, allow_remember)
        except Exception:
            # Fallback to terminal prompt if GUI unavailable
            return self._show_terminal_prompt(title, message, command, details)
    
    def _show_gui_dialog(
        self,
        title: str,
        message: str,
        command: str,
        details: str,
        allow_remember: bool
    ) -> ConfirmationResult:
        """Show a graphical confirmation dialog"""
        self.root = tk.Tk()
        self.root.title(title)
        self.root.geometry("500x350")
        
        # Make it accessible - high contrast, clear fonts
        self.root.configure(bg='#f0f0f0')
        
        # Center the window
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
        
        # Main frame with padding
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Icon and message
        icon_label = ttk.Label(main_frame, text="⚠️", font=('Arial', 24))
        icon_label.grid(row=0, column=0, padx=(0, 10), sticky=tk.W)
        
        message_label = ttk.Label(
            main_frame,
            text=message,
            wraplength=400,
            font=('Arial', 12)
        )
        message_label.grid(row=0, column=1, pady=(0, 15), sticky=tk.W)
        
        # Command display (if provided)
        if command:
            cmd_frame = ttk.LabelFrame(main_frame, text="Command to execute:", padding="10")
            cmd_frame.grid(row=1, column=0, columnspan=2, pady=(0, 10), sticky=(tk.W, tk.E))
            
            cmd_text = tk.Text(
                cmd_frame,
                height=3,
                width=50,
                font=('Courier', 10),
                bg='#2b2b2b',
                fg='#10b981',  # Green text
                insertbackground='white'
            )
            cmd_text.insert('1.0', command)
            cmd_text.configure(state='disabled')  # Read-only
            cmd_text.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        # Details (if provided)
        if details:
            details_label = ttk.Label(
                main_frame,
                text=details,
                wraplength=400,
                font=('Arial', 10),
                foreground='#666666'
            )
            details_label.grid(row=2, column=0, columnspan=2, pady=(0, 10), sticky=tk.W)
        
        # Remember choice checkbox (if allowed)
        self.remember_var = tk.BooleanVar(value=False)
        if allow_remember:
            remember_check = ttk.Checkbutton(
                main_frame,
                text="Remember my choice for this session",
                variable=self.remember_var
            )
            remember_check.grid(row=3, column=0, columnspan=2, pady=(10, 0), sticky=tk.W)
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=4, column=0, columnspan=2, pady=(20, 0))
        
        # Cancel button (safe default)
        cancel_btn = ttk.Button(
            button_frame,
            text="Cancel (Esc)",
            command=self._on_cancel,
            width=15
        )
        cancel_btn.grid(row=0, column=0, padx=(0, 10))
        
        # Confirm button
        confirm_btn = ttk.Button(
            button_frame,
            text="Confirm (Enter)",
            command=self._on_confirm,
            width=15
        )
        confirm_btn.grid(row=0, column=1)
        
        # Keyboard bindings for accessibility
        self.root.bind('<Escape>', lambda e: self._on_cancel())
        self.root.bind('<Return>', lambda e: self._on_confirm())
        
        # Focus on cancel by default (safer)
        cancel_btn.focus()
        
        # Make it modal
        self.root.grab_set()
        self.root.mainloop()
        
        return self.result
    
    def _show_terminal_prompt(
        self,
        title: str,
        message: str,
        command: str,
        details: str
    ) -> ConfirmationResult:
        """Fallback to terminal prompt if GUI unavailable"""
        print(f"\n{'=' * 60}")
        print(f"⚠️  {title}")
        print(f"{'=' * 60}")
        print(f"\n{message}")
        
        if command:
            print(f"\n📋 Command to execute:")
            print(f"   {command}")
        
        if details:
            print(f"\n📝 {details}")
        
        print(f"\n{'=' * 60}")
        
        while True:
            response = input("\nDo you want to proceed? (yes/no): ").lower().strip()
            if response in ['yes', 'y']:
                return ConfirmationResult(confirmed=True)
            elif response in ['no', 'n']:
                return ConfirmationResult(confirmed=False)
            else:
                print("Please answer 'yes' or 'no'")
    
    def _on_confirm(self):
        """Handle confirmation"""
        self.result = ConfirmationResult(
            confirmed=True,
            remember_choice=self.remember_var.get() if hasattr(self, 'remember_var') else False
        )
        if self.root:
            self.root.quit()
            self.root.destroy()
    
    def _on_cancel(self):
        """Handle cancellation"""
        self.result = ConfirmationResult(
            confirmed=False,
            remember_choice=False
        )
        if self.root:
            self.root.quit()
            self.root.destroy()


class QuickConfirm:
    """Quick confirmation methods for common scenarios"""
    
    @staticmethod
    def install_package(package_name: str, command: str) -> bool:
        """Confirm package installation"""
        dialog = SacredConfirmationDialog()
        result = dialog.ask(
            title="Install Package",
            message=f"Do you want to install {package_name}?",
            command=command,
            details="This will download and install new software on your system.",
            allow_remember=True
        )
        return result.confirmed
    
    @staticmethod
    def system_modification(description: str, command: str) -> bool:
        """Confirm system modification"""
        dialog = SacredConfirmationDialog()
        result = dialog.ask(
            title="System Modification",
            message=f"This will modify your system:\n{description}",
            command=command,
            details="⚠️ System changes may require a restart.",
            allow_remember=False
        )
        return result.confirmed
    
    @staticmethod
    def destructive_action(description: str, command: str) -> bool:
        """Confirm destructive action with extra warning"""
        dialog = SacredConfirmationDialog()
        result = dialog.ask(
            title="⚠️ Destructive Action",
            message=f"WARNING: {description}\n\nThis action cannot be undone!",
            command=command,
            details="Please make sure you have backups before proceeding.",
            allow_remember=False
        )
        return result.confirmed


# Export for easy access
confirm = QuickConfirm()


if __name__ == "__main__":
    # Test the dialog
    result = confirm.install_package(
        "firefox",
        "nix profile install nixpkgs#firefox"
    )
    print(f"User confirmed: {result}")