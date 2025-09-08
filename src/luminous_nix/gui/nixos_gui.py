#!/usr/bin/env python3
"""
Luminous Nix GUI - Visual NixOS Management Interface
A comprehensive GUI for package management and system configuration
"""

import sys
import os
import json
import time
import threading
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from datetime import datetime

# Try multiple GUI frameworks with fallbacks
GUI_AVAILABLE = False
GUI_FRAMEWORK = None

# Try PyQt6 first (most feature-rich)
try:
    from PyQt6.QtWidgets import *
    from PyQt6.QtCore import *
    from PyQt6.QtGui import *
    GUI_AVAILABLE = True
    GUI_FRAMEWORK = "PyQt6"
except ImportError:
    # Try tkinter (usually available)
    try:
        import tkinter as tk
        from tkinter import ttk, messagebox, scrolledtext
        import tkinter.font as tkfont
        GUI_AVAILABLE = True
        GUI_FRAMEWORK = "tkinter"
    except ImportError:
        pass

# For web-based alternative
try:
    import streamlit as st
    WEB_GUI_AVAILABLE = True
except ImportError:
    WEB_GUI_AVAILABLE = False

# Import our components
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from luminous_nix.frontends.cli import UnifiedNixAssistant
from luminous_nix.memory.conversation_manager import ConversationMemory
from luminous_nix.execution.safe_executor import SafeExecutor, ExecutionMode, RiskLevel
from luminous_nix.package_aliases import EXTENDED_PACKAGE_ALIASES, get_package_name, suggest_similar

@dataclass
class Package:
    """Package information"""
    name: str
    version: str
    description: str
    installed: bool = False
    size: Optional[str] = None
    homepage: Optional[str] = None

class NixOSGUI:
    """
    Main GUI application for NixOS management
    Features:
    - Package search and installation
    - System configuration editor
    - Generation management
    - System health monitoring
    - AI-powered assistance
    """
    
    def __init__(self):
        """Initialize the GUI application"""
        self.assistant = UnifiedNixAssistant()
        self.memory = ConversationMemory()
        self.executor = SafeExecutor(default_mode=ExecutionMode.CONFIRMED)
        
        # Package cache
        self.packages_cache = []
        self.installed_packages = []
        
        # System info
        self.system_info = self.get_system_info()
        
        # Create GUI based on available framework
        if GUI_FRAMEWORK == "PyQt6":
            self.create_qt_gui()
        elif GUI_FRAMEWORK == "tkinter":
            self.create_tk_gui()
        else:
            print("No GUI framework available. Install PyQt6 or tkinter.")
            self.create_web_gui()
    
    def get_system_info(self) -> Dict[str, Any]:
        """Get system information"""
        import subprocess
        import psutil
        
        info = {
            'nixos_version': 'Unknown',
            'kernel': 'Unknown',
            'cpu_usage': 0,
            'memory_usage': 0,
            'disk_usage': 0,
            'uptime': 'Unknown'
        }
        
        try:
            # NixOS version
            result = subprocess.run(['nixos-version'], capture_output=True, text=True)
            if result.returncode == 0:
                info['nixos_version'] = result.stdout.strip()
            
            # Kernel
            result = subprocess.run(['uname', '-r'], capture_output=True, text=True)
            if result.returncode == 0:
                info['kernel'] = result.stdout.strip()
            
            # System resources
            info['cpu_usage'] = psutil.cpu_percent(interval=1)
            info['memory_usage'] = psutil.virtual_memory().percent
            info['disk_usage'] = psutil.disk_usage('/').percent
            
            # Uptime
            boot_time = datetime.fromtimestamp(psutil.boot_time())
            uptime = datetime.now() - boot_time
            info['uptime'] = str(uptime).split('.')[0]
            
        except Exception as e:
            print(f"Error getting system info: {e}")
        
        return info
    
    def create_qt_gui(self):
        """Create PyQt6 GUI"""
        
        class MainWindow(QMainWindow):
            def __init__(gui_self, parent_gui):
                super().__init__()
                gui_self.parent_gui = parent_gui
                gui_self.setWindowTitle("Luminous Nix - NixOS Management")
                gui_self.setGeometry(100, 100, 1200, 800)
                
                # Set modern dark theme
                gui_self.setStyleSheet("""
                    QMainWindow {
                        background-color: #1e1e1e;
                    }
                    QTabWidget::pane {
                        background-color: #2d2d2d;
                        border: 1px solid #3d3d3d;
                    }
                    QTabBar::tab {
                        background-color: #2d2d2d;
                        color: #ffffff;
                        padding: 10px 20px;
                        margin-right: 2px;
                    }
                    QTabBar::tab:selected {
                        background-color: #0d7377;
                    }
                    QPushButton {
                        background-color: #0d7377;
                        color: white;
                        border: none;
                        padding: 8px 16px;
                        border-radius: 4px;
                        font-weight: bold;
                    }
                    QPushButton:hover {
                        background-color: #14a085;
                    }
                    QLineEdit, QTextEdit, QListWidget, QTreeWidget {
                        background-color: #2d2d2d;
                        color: #ffffff;
                        border: 1px solid #3d3d3d;
                        padding: 5px;
                    }
                    QLabel {
                        color: #ffffff;
                    }
                    QGroupBox {
                        color: #ffffff;
                        border: 2px solid #3d3d3d;
                        border-radius: 5px;
                        margin-top: 10px;
                        padding-top: 10px;
                    }
                    QGroupBox::title {
                        subcontrol-origin: margin;
                        left: 10px;
                        padding: 0 5px 0 5px;
                    }
                """)
                
                # Create central widget with tabs
                central_widget = QWidget()
                gui_self.setCentralWidget(central_widget)
                
                layout = QVBoxLayout()
                central_widget.setLayout(layout)
                
                # Create tab widget
                tabs = QTabWidget()
                layout.addWidget(tabs)
                
                # Add tabs
                tabs.addTab(gui_self.create_packages_tab(), "📦 Packages")
                tabs.addTab(gui_self.create_configuration_tab(), "⚙️ Configuration")
                tabs.addTab(gui_self.create_generations_tab(), "🔄 Generations")
                tabs.addTab(gui_self.create_health_tab(), "💚 System Health")
                tabs.addTab(gui_self.create_ai_assistant_tab(), "🤖 AI Assistant")
                
                # Status bar
                gui_self.status_bar = QStatusBar()
                gui_self.setStatusBar(gui_self.status_bar)
                gui_self.status_bar.showMessage("Ready")
                
                # Menu bar
                gui_self.create_menu_bar()
            
            def create_menu_bar(gui_self):
                """Create menu bar"""
                menubar = gui_self.menuBar()
                
                # File menu
                file_menu = menubar.addMenu("File")
                
                refresh_action = QAction("Refresh", gui_self)
                refresh_action.triggered.connect(gui_self.refresh_all)
                file_menu.addAction(refresh_action)
                
                file_menu.addSeparator()
                
                exit_action = QAction("Exit", gui_self)
                exit_action.triggered.connect(gui_self.close)
                file_menu.addAction(exit_action)
                
                # Tools menu
                tools_menu = menubar.addMenu("Tools")
                
                garbage_collect = QAction("Garbage Collection", gui_self)
                garbage_collect.triggered.connect(gui_self.run_garbage_collection)
                tools_menu.addAction(garbage_collect)
                
                optimize = QAction("Optimize Store", gui_self)
                optimize.triggered.connect(gui_self.optimize_store)
                tools_menu.addAction(optimize)
                
                # Help menu
                help_menu = menubar.addMenu("Help")
                
                about = QAction("About", gui_self)
                about.triggered.connect(gui_self.show_about)
                help_menu.addAction(about)
            
            def create_packages_tab(gui_self):
                """Create packages management tab"""
                widget = QWidget()
                layout = QVBoxLayout()
                
                # Search bar
                search_layout = QHBoxLayout()
                search_label = QLabel("Search:")
                gui_self.search_input = QLineEdit()
                gui_self.search_input.setPlaceholderText("Enter package name or description...")
                gui_self.search_input.returnPressed.connect(gui_self.search_packages)
                search_button = QPushButton("🔍 Search")
                search_button.clicked.connect(gui_self.search_packages)
                
                search_layout.addWidget(search_label)
                search_layout.addWidget(gui_self.search_input)
                search_layout.addWidget(search_button)
                layout.addLayout(search_layout)
                
                # Category buttons
                category_layout = QHBoxLayout()
                categories = ["Browsers", "Editors", "Development", "Media", "Security", "System"]
                for category in categories:
                    btn = QPushButton(category)
                    btn.clicked.connect(lambda checked, c=category: gui_self.browse_category(c))
                    category_layout.addWidget(btn)
                layout.addLayout(category_layout)
                
                # Package list
                gui_self.package_list = QTreeWidget()
                gui_self.package_list.setHeaderLabels(["Name", "Version", "Status", "Description"])
                gui_self.package_list.setColumnWidth(0, 200)
                gui_self.package_list.setColumnWidth(1, 100)
                gui_self.package_list.setColumnWidth(2, 100)
                layout.addWidget(gui_self.package_list)
                
                # Action buttons
                action_layout = QHBoxLayout()
                install_btn = QPushButton("📥 Install Selected")
                install_btn.clicked.connect(gui_self.install_selected)
                remove_btn = QPushButton("🗑️ Remove Selected")
                remove_btn.clicked.connect(gui_self.remove_selected)
                update_btn = QPushButton("🔄 Update Selected")
                update_btn.clicked.connect(gui_self.update_selected)
                
                action_layout.addWidget(install_btn)
                action_layout.addWidget(remove_btn)
                action_layout.addWidget(update_btn)
                action_layout.addStretch()
                layout.addLayout(action_layout)
                
                widget.setLayout(layout)
                return widget
            
            def create_configuration_tab(gui_self):
                """Create configuration editor tab"""
                widget = QWidget()
                layout = QVBoxLayout()
                
                # Configuration type selector
                config_layout = QHBoxLayout()
                config_label = QLabel("Configuration:")
                gui_self.config_selector = QComboBox()
                gui_self.config_selector.addItems([
                    "System (configuration.nix)",
                    "Hardware (hardware-configuration.nix)",
                    "Home Manager",
                    "Flake",
                    "Custom"
                ])
                gui_self.config_selector.currentTextChanged.connect(gui_self.load_configuration)
                
                config_layout.addWidget(config_label)
                config_layout.addWidget(gui_self.config_selector)
                config_layout.addStretch()
                layout.addLayout(config_layout)
                
                # Editor
                gui_self.config_editor = QTextEdit()
                gui_self.config_editor.setFont(QFont("Monospace", 10))
                layout.addWidget(gui_self.config_editor)
                
                # Action buttons
                action_layout = QHBoxLayout()
                save_btn = QPushButton("💾 Save")
                save_btn.clicked.connect(gui_self.save_configuration)
                test_btn = QPushButton("🧪 Test Configuration")
                test_btn.clicked.connect(gui_self.test_configuration)
                apply_btn = QPushButton("✅ Apply Configuration")
                apply_btn.clicked.connect(gui_self.apply_configuration)
                
                action_layout.addWidget(save_btn)
                action_layout.addWidget(test_btn)
                action_layout.addWidget(apply_btn)
                action_layout.addStretch()
                layout.addLayout(action_layout)
                
                widget.setLayout(layout)
                return widget
            
            def create_generations_tab(gui_self):
                """Create generations management tab"""
                widget = QWidget()
                layout = QVBoxLayout()
                
                # Generation list
                gui_self.generation_list = QTreeWidget()
                gui_self.generation_list.setHeaderLabels(["#", "Date", "Description", "Current"])
                layout.addWidget(gui_self.generation_list)
                
                # Action buttons
                action_layout = QHBoxLayout()
                switch_btn = QPushButton("🔄 Switch to Selected")
                switch_btn.clicked.connect(gui_self.switch_generation)
                delete_btn = QPushButton("🗑️ Delete Old Generations")
                delete_btn.clicked.connect(gui_self.delete_old_generations)
                diff_btn = QPushButton("📊 Show Diff")
                diff_btn.clicked.connect(gui_self.show_generation_diff)
                
                action_layout.addWidget(switch_btn)
                action_layout.addWidget(delete_btn)
                action_layout.addWidget(diff_btn)
                action_layout.addStretch()
                layout.addLayout(action_layout)
                
                widget.setLayout(layout)
                gui_self.load_generations()
                return widget
            
            def create_health_tab(gui_self):
                """Create system health monitoring tab"""
                widget = QWidget()
                layout = QVBoxLayout()
                
                # System info
                info_group = QGroupBox("System Information")
                info_layout = QGridLayout()
                
                gui_self.info_labels = {}
                info_items = [
                    ("NixOS Version:", "nixos_version"),
                    ("Kernel:", "kernel"),
                    ("Uptime:", "uptime"),
                    ("CPU Usage:", "cpu_usage"),
                    ("Memory Usage:", "memory_usage"),
                    ("Disk Usage:", "disk_usage")
                ]
                
                for i, (label, key) in enumerate(info_items):
                    info_layout.addWidget(QLabel(label), i, 0)
                    value_label = QLabel("Loading...")
                    gui_self.info_labels[key] = value_label
                    info_layout.addWidget(value_label, i, 1)
                
                info_group.setLayout(info_layout)
                layout.addWidget(info_group)
                
                # Health checks
                health_group = QGroupBox("Health Checks")
                health_layout = QVBoxLayout()
                
                gui_self.health_list = QListWidget()
                health_layout.addWidget(gui_self.health_list)
                
                check_btn = QPushButton("🔍 Run Health Check")
                check_btn.clicked.connect(gui_self.run_health_check)
                health_layout.addWidget(check_btn)
                
                health_group.setLayout(health_layout)
                layout.addWidget(health_group)
                
                # Recommendations
                rec_group = QGroupBox("Recommendations")
                rec_layout = QVBoxLayout()
                
                gui_self.recommendations_list = QListWidget()
                rec_layout.addWidget(gui_self.recommendations_list)
                
                rec_group.setLayout(rec_layout)
                layout.addWidget(rec_group)
                
                widget.setLayout(layout)
                gui_self.update_system_info()
                return widget
            
            def create_ai_assistant_tab(gui_self):
                """Create AI assistant tab"""
                widget = QWidget()
                layout = QVBoxLayout()
                
                # Chat history
                gui_self.chat_display = QTextEdit()
                gui_self.chat_display.setReadOnly(True)
                layout.addWidget(gui_self.chat_display)
                
                # Input area
                input_layout = QHBoxLayout()
                gui_self.chat_input = QLineEdit()
                gui_self.chat_input.setPlaceholderText("Ask me anything about NixOS...")
                gui_self.chat_input.returnPressed.connect(gui_self.send_ai_query)
                send_btn = QPushButton("📤 Send")
                send_btn.clicked.connect(gui_self.send_ai_query)
                
                input_layout.addWidget(gui_self.chat_input)
                input_layout.addWidget(send_btn)
                layout.addLayout(input_layout)
                
                # Quick actions
                quick_layout = QHBoxLayout()
                quick_label = QLabel("Quick:")
                quick_layout.addWidget(quick_label)
                
                quick_actions = [
                    "How do I install a package?",
                    "Explain generations",
                    "Fix broken packages",
                    "Optimize my system"
                ]
                
                for action in quick_actions:
                    btn = QPushButton(action)
                    btn.clicked.connect(lambda checked, a=action: gui_self.quick_ai_query(a))
                    quick_layout.addWidget(btn)
                
                layout.addLayout(quick_layout)
                
                widget.setLayout(layout)
                return widget
            
            # Implementation methods
            def search_packages(gui_self):
                """Search for packages"""
                query = gui_self.search_input.text()
                if not query:
                    return
                
                gui_self.status_bar.showMessage(f"Searching for '{query}'...")
                gui_self.package_list.clear()
                
                # Use assistant to search
                # This would normally query the NixOS package database
                # For now, use our aliases
                from luminous_nix.package_aliases import suggest_similar, EXTENDED_PACKAGE_ALIASES
                
                suggestions = suggest_similar(query, 10)
                for alias, package in suggestions:
                    item = QTreeWidgetItem([
                        package,
                        "latest",
                        "Available",
                        f"Alias: {alias}"
                    ])
                    gui_self.package_list.addTopLevelItem(item)
                
                gui_self.status_bar.showMessage(f"Found {len(suggestions)} packages")
            
            def browse_category(gui_self, category):
                """Browse packages by category"""
                from luminous_nix.package_aliases import get_category_packages
                
                gui_self.package_list.clear()
                packages = get_category_packages(category)
                
                for alias, package in packages.items():
                    item = QTreeWidgetItem([
                        package,
                        "latest",
                        "Available",
                        f"Category: {category}"
                    ])
                    gui_self.package_list.addTopLevelItem(item)
                
                gui_self.status_bar.showMessage(f"Showing {len(packages)} {category} packages")
            
            def install_selected(gui_self):
                """Install selected packages"""
                selected = gui_self.package_list.selectedItems()
                if not selected:
                    QMessageBox.warning(gui_self, "No Selection", "Please select packages to install")
                    return
                
                packages = [item.text(0) for item in selected]
                
                reply = QMessageBox.question(
                    gui_self, 
                    "Confirm Installation",
                    f"Install these packages?\n\n{', '.join(packages)}",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                
                if reply == QMessageBox.StandardButton.Yes:
                    for package in packages:
                        cmd = f"nix profile install nixpkgs#{package}"
                        result = gui_self.parent_gui.executor.execute(cmd, ExecutionMode.CONFIRMED)
                        if result.success:
                            gui_self.status_bar.showMessage(f"Installed {package}")
                        else:
                            QMessageBox.warning(gui_self, "Installation Failed", f"Failed to install {package}")
            
            def update_system_info(gui_self):
                """Update system information display"""
                info = gui_self.parent_gui.get_system_info()
                
                for key, label in gui_self.info_labels.items():
                    value = info.get(key, "Unknown")
                    if key.endswith('_usage'):
                        label.setText(f"{value:.1f}%")
                    else:
                        label.setText(str(value))
            
            def run_health_check(gui_self):
                """Run system health check"""
                gui_self.health_list.clear()
                gui_self.recommendations_list.clear()
                
                checks = [
                    ("Disk Space", gui_self.parent_gui.system_info['disk_usage'] < 90),
                    ("Memory Usage", gui_self.parent_gui.system_info['memory_usage'] < 80),
                    ("CPU Usage", gui_self.parent_gui.system_info['cpu_usage'] < 80),
                ]
                
                for check_name, is_healthy in checks:
                    status = "✅ Healthy" if is_healthy else "⚠️ Warning"
                    gui_self.health_list.addItem(f"{check_name}: {status}")
                    
                    if not is_healthy:
                        if "Disk" in check_name:
                            gui_self.recommendations_list.addItem("Consider running garbage collection")
                        elif "Memory" in check_name:
                            gui_self.recommendations_list.addItem("Close unnecessary applications")
                        elif "CPU" in check_name:
                            gui_self.recommendations_list.addItem("Check for resource-intensive processes")
            
            def send_ai_query(gui_self):
                """Send query to AI assistant"""
                query = gui_self.chat_input.text()
                if not query:
                    return
                
                gui_self.chat_input.clear()
                gui_self.chat_display.append(f"<b>You:</b> {query}")
                
                # Get AI response
                response = gui_self.parent_gui.assistant.answer(query)
                gui_self.chat_display.append(f"<b>Assistant:</b> {response}")
                gui_self.chat_display.append("")
                
                # Add to memory
                gui_self.parent_gui.memory.add_turn(query, response)
            
            def quick_ai_query(gui_self, query):
                """Send quick query to AI"""
                gui_self.chat_input.setText(query)
                gui_self.send_ai_query()
            
            def load_generations(gui_self):
                """Load system generations"""
                # This would normally query nixos-rebuild list-generations
                # For demo, show sample data
                gui_self.generation_list.clear()
                
                sample_generations = [
                    ("42", "2024-01-19 10:30", "Updated packages", "Yes"),
                    ("41", "2024-01-18 15:20", "Added development tools", "No"),
                    ("40", "2024-01-17 09:15", "System configuration update", "No"),
                ]
                
                for gen in sample_generations:
                    item = QTreeWidgetItem(list(gen))
                    if gen[3] == "Yes":
                        item.setBackground(0, QColor(13, 115, 119))
                    gui_self.generation_list.addTopLevelItem(item)
            
            def refresh_all(gui_self):
                """Refresh all data"""
                gui_self.update_system_info()
                gui_self.load_generations()
                gui_self.run_health_check()
                gui_self.status_bar.showMessage("Refreshed all data")
            
            def show_about(gui_self):
                """Show about dialog"""
                QMessageBox.about(
                    gui_self,
                    "About Luminous Nix",
                    "Luminous Nix GUI v1.0\n\n"
                    "A comprehensive visual interface for NixOS management\n\n"
                    "Features:\n"
                    "• Package management\n"
                    "• Configuration editing\n"
                    "• Generation control\n"
                    "• System health monitoring\n"
                    "• AI-powered assistance\n\n"
                    "Built with consciousness-first principles"
                )
            
            # Stub methods (would implement fully)
            def remove_selected(gui_self): pass
            def update_selected(gui_self): pass
            def load_configuration(gui_self): pass
            def save_configuration(gui_self): pass
            def test_configuration(gui_self): pass
            def apply_configuration(gui_self): pass
            def switch_generation(gui_self): pass
            def delete_old_generations(gui_self): pass
            def show_generation_diff(gui_self): pass
            def run_garbage_collection(gui_self): pass
            def optimize_store(gui_self): pass
        
        # Create and run the Qt application
        app = QApplication(sys.argv)
        window = MainWindow(self)
        window.show()
        sys.exit(app.exec())
    
    def create_tk_gui(self):
        """Create tkinter GUI (fallback)"""
        root = tk.Tk()
        root.title("Luminous Nix - NixOS Management")
        root.geometry("1000x700")
        
        # Create notebook for tabs
        notebook = ttk.Notebook(root)
        notebook.pack(fill="both", expand=True)
        
        # Create tabs
        package_frame = ttk.Frame(notebook)
        notebook.add(package_frame, text="📦 Packages")
        
        config_frame = ttk.Frame(notebook)
        notebook.add(config_frame, text="⚙️ Configuration")
        
        health_frame = ttk.Frame(notebook)
        notebook.add(health_frame, text="💚 System Health")
        
        ai_frame = ttk.Frame(notebook)
        notebook.add(ai_frame, text="🤖 AI Assistant")
        
        # Package tab
        self.create_tk_package_tab(package_frame)
        
        # AI Assistant tab
        self.create_tk_ai_tab(ai_frame)
        
        # Status bar
        status_bar = ttk.Label(root, text="Ready", relief=tk.SUNKEN)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        root.mainloop()
    
    def create_tk_package_tab(self, parent):
        """Create package tab for tkinter"""
        # Search frame
        search_frame = ttk.Frame(parent)
        search_frame.pack(fill="x", padx=5, pady=5)
        
        ttk.Label(search_frame, text="Search:").pack(side="left")
        search_entry = ttk.Entry(search_frame, width=50)
        search_entry.pack(side="left", padx=5)
        ttk.Button(search_frame, text="🔍 Search").pack(side="left")
        
        # Package list
        list_frame = ttk.Frame(parent)
        list_frame.pack(fill="both", expand=True, padx=5)
        
        # Treeview for packages
        columns = ("Version", "Status", "Description")
        tree = ttk.Treeview(list_frame, columns=columns, show="tree headings")
        tree.heading("#0", text="Package")
        tree.heading("Version", text="Version")
        tree.heading("Status", text="Status")
        tree.heading("Description", text="Description")
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Action buttons
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill="x", padx=5, pady=5)
        
        ttk.Button(button_frame, text="📥 Install").pack(side="left", padx=2)
        ttk.Button(button_frame, text="🗑️ Remove").pack(side="left", padx=2)
        ttk.Button(button_frame, text="🔄 Update").pack(side="left", padx=2)
    
    def create_tk_ai_tab(self, parent):
        """Create AI assistant tab for tkinter"""
        # Chat display
        chat_frame = ttk.Frame(parent)
        chat_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        chat_display = scrolledtext.ScrolledText(chat_frame, wrap=tk.WORD, height=20)
        chat_display.pack(fill="both", expand=True)
        
        # Input frame
        input_frame = ttk.Frame(parent)
        input_frame.pack(fill="x", padx=5, pady=5)
        
        chat_input = ttk.Entry(input_frame, width=80)
        chat_input.pack(side="left", padx=5)
        ttk.Button(input_frame, text="📤 Send").pack(side="left")
    
    def create_web_gui(self):
        """Create Streamlit web GUI"""
        if not WEB_GUI_AVAILABLE:
            print("Install streamlit for web GUI: pip install streamlit")
            return
        
        # This would be in a separate file normally
        st.set_page_config(
            page_title="Luminous Nix",
            page_icon="🌟",
            layout="wide"
        )
        
        st.title("🌟 Luminous Nix - NixOS Management")
        
        # Sidebar
        st.sidebar.title("Navigation")
        page = st.sidebar.radio("", ["Packages", "Configuration", "Health", "AI Assistant"])
        
        if page == "Packages":
            self.web_packages_page()
        elif page == "AI Assistant":
            self.web_ai_page()
    
    def web_packages_page(self):
        """Web GUI packages page"""
        st.header("📦 Package Management")
        
        # Search
        col1, col2 = st.columns([3, 1])
        with col1:
            search = st.text_input("Search packages", placeholder="Enter package name...")
        with col2:
            if st.button("🔍 Search"):
                st.write(f"Searching for {search}...")
        
        # Categories
        st.subheader("Browse by Category")
        categories = st.columns(6)
        for i, cat in enumerate(["Browsers", "Editors", "Development", "Media", "Security", "System"]):
            with categories[i]:
                if st.button(cat):
                    st.write(f"Loading {cat} packages...")
    
    def web_ai_page(self):
        """Web GUI AI assistant page"""
        st.header("🤖 AI Assistant")
        
        # Chat interface
        if "messages" not in st.session_state:
            st.session_state.messages = []
        
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.write(message["content"])
        
        if prompt := st.chat_input("Ask me anything about NixOS..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.write(prompt)
            
            # Get AI response
            response = "This is where the AI response would appear"
            st.session_state.messages.append({"role": "assistant", "content": response})
            with st.chat_message("assistant"):
                st.write(response)


def main():
    """Main entry point"""
    if not GUI_AVAILABLE and not WEB_GUI_AVAILABLE:
        print("❌ No GUI framework available!")
        print("\nInstall one of the following:")
        print("  • PyQt6: pip install PyQt6")
        print("  • tkinter: Usually included with Python")
        print("  • Streamlit: pip install streamlit")
        return
    
    print(f"🚀 Starting Luminous Nix GUI with {GUI_FRAMEWORK or 'Streamlit'}...")
    app = NixOSGUI()


if __name__ == "__main__":
    main()