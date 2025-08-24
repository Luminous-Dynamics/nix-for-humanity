# 🪟➡️🐧 Windows Apps on NixOS: Complete Compatibility Guide

> *"You don't have to leave your favorite apps behind. Most work great on NixOS!"*

## 📊 Quick Compatibility Overview

| Compatibility Level | What It Means | Examples |
|-------------------|---------------|----------|
| ⭐⭐⭐⭐⭐ **Native** | Perfect Linux version exists | VS Code, Discord, Steam |
| ⭐⭐⭐⭐ **Excellent** | Great alternative available | LibreOffice for MS Office |
| ⭐⭐⭐ **Good** | Works via Wine/Bottles | Many Windows games |
| ⭐⭐ **Possible** | Requires effort but works | Some Adobe apps |
| ⭐ **Difficult** | Better to dual-boot | Anti-cheat games |

---

## 🎯 Common Windows Software & Solutions

### 🏢 Office & Productivity

| Windows App | Linux Solution | Compatibility | How to Install |
|------------|---------------|--------------|----------------|
| **MS Office** | LibreOffice | ⭐⭐⭐⭐ | `ask-nix "install libreoffice"` |
| | OnlyOffice | ⭐⭐⭐⭐⭐ | `ask-nix "install onlyoffice"` |
| | Office 365 Web | ⭐⭐⭐⭐⭐ | Use any browser |
| **Outlook** | Thunderbird | ⭐⭐⭐⭐ | `ask-nix "install thunderbird"` |
| | Evolution | ⭐⭐⭐⭐⭐ | `ask-nix "install evolution"` |
| **OneNote** | Obsidian | ⭐⭐⭐⭐⭐ | `ask-nix "install obsidian"` |
| | Joplin | ⭐⭐⭐⭐ | `ask-nix "install joplin"` |
| **MS Teams** | Teams for Linux | ⭐⭐⭐⭐⭐ | `ask-nix "install teams"` |
| **Visio** | Draw.io | ⭐⭐⭐⭐ | `ask-nix "install drawio"` |
| | Dia | ⭐⭐⭐ | `ask-nix "install dia"` |

### 💻 Development Tools

| Windows App | Linux Solution | Compatibility | How to Install |
|------------|---------------|--------------|----------------|
| **Visual Studio** | VS Code | ⭐⭐⭐⭐⭐ | `ask-nix "install vscode"` |
| | JetBrains IDEs | ⭐⭐⭐⭐⭐ | `ask-nix "install intellij"` |
| **Visual Studio (Full)** | Rider (.NET) | ⭐⭐⭐⭐ | `ask-nix "install rider"` |
| **SQL Server Mgmt** | DBeaver | ⭐⭐⭐⭐⭐ | `ask-nix "install dbeaver"` |
| | Azure Data Studio | ⭐⭐⭐⭐⭐ | `ask-nix "install azure-data-studio"` |
| **Notepad++** | VS Code | ⭐⭐⭐⭐⭐ | Already mentioned |
| | Sublime Text | ⭐⭐⭐⭐⭐ | `ask-nix "install sublime"` |
| **PuTTY** | Built-in SSH | ⭐⭐⭐⭐⭐ | Already included! |
| **Windows Terminal** | Alacritty | ⭐⭐⭐⭐⭐ | You have it! |
| | Kitty | ⭐⭐⭐⭐⭐ | You have it! |

### 🎨 Creative Software

| Windows App | Linux Solution | Compatibility | How to Install |
|------------|---------------|--------------|----------------|
| **Photoshop** | GIMP | ⭐⭐⭐⭐ | `ask-nix "install gimp"` |
| | Krita | ⭐⭐⭐⭐⭐ | `ask-nix "install krita"` |
| | Photoshop via Wine | ⭐⭐⭐ | See Wine section |
| **Premiere Pro** | DaVinci Resolve | ⭐⭐⭐⭐⭐ | `ask-nix "install davinci-resolve"` |
| | Kdenlive | ⭐⭐⭐⭐ | `ask-nix "install kdenlive"` |
| **After Effects** | Blender | ⭐⭐⭐⭐ | `ask-nix "install blender"` |
| | Natron | ⭐⭐⭐ | `ask-nix "install natron"` |
| **Illustrator** | Inkscape | ⭐⭐⭐⭐ | `ask-nix "install inkscape"` |
| **Audition** | Audacity | ⭐⭐⭐⭐ | `ask-nix "install audacity"` |
| | Ardour | ⭐⭐⭐⭐⭐ | `ask-nix "install ardour"` |
| **FL Studio** | FL Studio (Wine) | ⭐⭐⭐⭐ | Works great in Wine! |
| | Bitwig Studio | ⭐⭐⭐⭐⭐ | `ask-nix "install bitwig-studio"` |

### 🎮 Gaming

| Platform/Game | Linux Solution | Compatibility | How to Install |
|------------|---------------|--------------|----------------|
| **Steam** | Steam Native | ⭐⭐⭐⭐⭐ | `ask-nix "install steam"` |
| **Epic Games** | Heroic Launcher | ⭐⭐⭐⭐ | `ask-nix "install heroic"` |
| **GOG** | Heroic/Lutris | ⭐⭐⭐⭐⭐ | `ask-nix "install lutris"` |
| **Battle.net** | Lutris | ⭐⭐⭐⭐ | Lutris handles it |
| **Game Pass** | Dual boot only | ⭐ | Not available |
| **Minecraft** | Minecraft Native | ⭐⭐⭐⭐⭐ | `ask-nix "install minecraft"` |

### 🌐 Web Browsers

| Windows Browser | Linux Version | Compatibility | How to Install |
|------------|---------------|--------------|----------------|
| **Chrome** | Chrome | ⭐⭐⭐⭐⭐ | `ask-nix "install google-chrome"` |
| **Edge** | Edge | ⭐⭐⭐⭐⭐ | `ask-nix "install microsoft-edge"` |
| **Firefox** | Firefox | ⭐⭐⭐⭐⭐ | `ask-nix "install firefox"` |
| **Brave** | Brave | ⭐⭐⭐⭐⭐ | You have it! |

### 💬 Communication

| Windows App | Linux Solution | Compatibility | How to Install |
|------------|---------------|--------------|----------------|
| **Discord** | Discord | ⭐⭐⭐⭐⭐ | `ask-nix "install discord"` |
| **Slack** | Slack | ⭐⭐⭐⭐⭐ | `ask-nix "install slack"` |
| **Zoom** | Zoom | ⭐⭐⭐⭐⭐ | `ask-nix "install zoom"` |
| **Skype** | Skype | ⭐⭐⭐⭐⭐ | `ask-nix "install skype"` |
| **WhatsApp** | WhatsApp Web | ⭐⭐⭐⭐⭐ | Web app |
| | WhatsDesk | ⭐⭐⭐⭐ | `ask-nix "install whatsdesk"` |

### 🔧 System Utilities

| Windows Tool | Linux Alternative | Compatibility | How to Install |
|------------|---------------|--------------|----------------|
| **Task Manager** | htop/btop | ⭐⭐⭐⭐⭐ | `ask-nix "install btop"` |
| **File Explorer** | Dolphin (KDE) | ⭐⭐⭐⭐⭐ | Already have it! |
| **7-Zip** | Ark (KDE) | ⭐⭐⭐⭐⭐ | Already have it! |
| **WinRAR** | unrar/p7zip | ⭐⭐⭐⭐⭐ | `ask-nix "install p7zip"` |
| **CCleaner** | BleachBit | ⭐⭐⭐⭐ | `ask-nix "install bleachbit"` |
| **Rufus** | Balena Etcher | ⭐⭐⭐⭐⭐ | `ask-nix "install etcher"` |

---

## 🍷 Running Windows Apps with Wine/Bottles

### Easy Method: Bottles (GUI)
```bash
# Install Bottles
ask-nix "install bottles"

# Launch Bottles
bottles

# Steps:
1. Create new bottle
2. Choose environment (Gaming/Software)
3. Install Windows app
4. Run!
```

### Supported Windows Apps via Wine:
- ✅ **Office 2016/2019** (not 365)
- ✅ **Adobe Photoshop CS6**
- ✅ **Many older games**
- ✅ **Windows-only utilities**
- ✅ **Legacy business software**

### Apps That DON'T Work in Wine:
- ❌ **Adobe Creative Cloud** (latest versions)
- ❌ **Games with kernel anti-cheat**
- ❌ **Hardware-specific drivers**
- ❌ **Some DRM-protected software**

---

## 🎯 Decision Tree: When to Use What

```
Need Windows App?
├── Is there a Linux version?
│   └── Yes → Install native version ⭐⭐⭐⭐⭐
├── Is there a good alternative?
│   └── Yes → Use alternative ⭐⭐⭐⭐
├── Does it work in Wine/Bottles?
│   └── Yes → Use Wine/Bottles ⭐⭐⭐
├── Do you need it occasionally?
│   └── Yes → Dual boot to Windows ⭐⭐
└── Need it constantly?
    └── Consider Windows VM or stay on Windows ⭐
```

---

## 🚀 Quick Setup for Windows Refugees

```bash
# 1. Install essential Windows alternatives
ask-nix "install windows compatibility pack"

# This installs:
# - Wine & Bottles
# - LibreOffice
# - Common Windows fonts
# - NTFS support
# - Media codecs

# 2. Set up your workflow
ask-nix "migrate from windows"

# 3. Import Windows settings
ask-nix "import windows bookmarks"
ask-nix "import windows documents"
```

---

## 💡 Pro Tips for Smooth Transition

### 1. **Start with Web Apps**
Many Windows apps have web versions that work perfectly:
- Office 365 → office.com
- Adobe Express → express.adobe.com
- Canva → canva.com

### 2. **Use Flatpak for More Apps**
```bash
ask-nix "enable flatpak"
# Then browse flathub.org for thousands of apps
```

### 3. **Keep Windows for Specific Tasks**
It's OK to dual-boot and use Windows for:
- That one work app
- Specific games
- Hardware that needs Windows drivers

### 4. **Learn the Linux Way**
Sometimes the Linux alternative is actually better:
- Package managers > downloading installers
- Terminal > GUI for some tasks
- Open source > proprietary

---

## 🆘 Getting Help

### Check App Compatibility:
- **Wine:** [WineHQ AppDB](https://appdb.winehq.org/)
- **Games:** [ProtonDB](https://www.protondb.com/)
- **General:** [AlternativeTo](https://alternativeto.net/)

### Ask Luminous Nix:
```bash
ask-nix "run windows app [name]"
ask-nix "alternative to [windows app]"
ask-nix "install wine app [name]"
```

### Community:
- Luminous Nix Discord
- r/linux_gaming
- r/linuxquestions

---

## 🎉 Success Stories

> "I thought I needed Windows for Photoshop, but Krita is actually better for digital art!" - Artist

> "VS Code on Linux runs faster than on Windows. Never going back!" - Developer

> "90% of my Steam library just works. The 10% I don't miss." - Gamer

> "LibreOffice opens my old Word docs perfectly. Didn't expect that!" - Student

---

## 📝 Your Personal Migration Checklist

```markdown
□ Identify must-have Windows apps
□ Find Linux alternatives
□ Test alternatives in NixOS
□ Set up Wine/Bottles for stragglers
□ Configure dual-boot for emergencies
□ Gradually reduce Windows dependencies
□ Celebrate freedom! 🎉
```

---

*Remember: You don't have to switch everything at once. Take your time, and keep Windows as long as you need it. The goal is to make you comfortable, not to force a change.*