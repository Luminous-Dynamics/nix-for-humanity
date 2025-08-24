# 🔄 Luminous Nix Dual-Boot Guide: Keep Windows While Exploring NixOS

> *"You don't have to burn the bridge to cross it. Keep Windows as your safety net while discovering the magic of NixOS."*

## 🌟 Why Dual-Boot is Perfect for New NixOS Users

- **Zero Risk**: Keep all your Windows apps and games
- **Gradual Transition**: Learn NixOS at your own pace
- **Best of Both Worlds**: Windows for compatibility, NixOS for development
- **Easy Rollback**: If NixOS isn't for you, Windows is still there

## 📋 Prerequisites

- **UEFI System** (most computers from 2012+)
- **50GB+ free space** for NixOS (100GB+ recommended)
- **Windows already installed** (easier to add NixOS than vice versa)
- **Backup your data** (always, just in case)

## 🛠️ Installation Options

### Option 1: Side-by-Side on Same Drive (Easiest)
Perfect for laptops or single-drive systems

### Option 2: Separate Drives (Cleanest)
Best for desktops with multiple drives

### Option 3: External USB/SSD (Portable)
Try NixOS without touching your internal drive

---

## 📦 Method 1: Side-by-Side Installation (Most Common)

### Step 1: Prepare Windows
```powershell
# In Windows (as Administrator):

# 1. Disable Fast Startup (IMPORTANT!)
powercfg /h off

# 2. Disable BitLocker if enabled
manage-bde -off C:

# 3. Shrink Windows partition
# Open Disk Management (Win+X, K)
# Right-click C: → Shrink Volume
# Shrink by at least 50GB (50000 MB)
```

### Step 2: Create NixOS Installer
```bash
# Download NixOS ISO with Luminous Nix pre-configured
# (We'll create this custom ISO)

# Or use standard NixOS and add Luminous Nix later:
# https://nixos.org/download.html#nixos-iso
```

### Step 3: Install NixOS
1. Boot from USB
2. Choose "Install NixOS"
3. **IMPORTANT**: Select manual partitioning
4. Use the free space from Windows
5. Mount Windows EFI partition (don't format!)

### Step 4: Configure Dual-Boot
During installation, NixOS will auto-detect Windows!

---

## 🎮 Method 2: Separate Drives (Recommended for Desktops)

### Advantages:
- **Complete isolation** between OSes
- **No partition size regrets**
- **Can physically disconnect drives**
- **Easier troubleshooting**

### Setup:
1. Install Windows on Drive 1
2. Disconnect Drive 1 (optional safety)
3. Install NixOS on Drive 2
4. Reconnect and configure boot order

---

## 🚀 NixOS Configuration for Dual-Boot

### Create `/etc/nixos/dual-boot.nix`:
```nix
{ config, pkgs, lib, ... }:

{
  # Dual-Boot Configuration for Luminous Nix Users
  
  # Boot loader with Windows detection
  boot.loader = {
    systemd-boot.enable = true;
    systemd-boot.configurationLimit = 10;
    systemd-boot.consoleMode = "max";
    efi.canTouchEfiVariables = true;
    timeout = 5;  # Show menu for 5 seconds
  };

  # Fix Windows time conflict
  time.hardwareClockInLocalTime = true;
  
  # Auto-mount Windows partition (read-only by default for safety)
  fileSystems."/mnt/windows" = {
    device = "/dev/disk/by-label/Windows";  # Adjust to your setup
    fsType = "ntfs3";
    options = [ 
      "ro"           # Read-only for safety
      "uid=1000"     # Your user ID
      "gid=100"      # Users group
      "umask=0222"   # Prevent accidental writes
      "nofail"       # Don't fail boot if Windows drive missing
    ];
  };

  # Optional: Shared data partition (for documents, projects)
  fileSystems."/mnt/shared" = {
    device = "/dev/disk/by-label/Shared";
    fsType = "ntfs3";
    options = [ "rw" "uid=1000" "gid=100" "umask=0022" "nofail" ];
  };

  # Windows compatibility tools
  environment.systemPackages = with pkgs; [
    ntfs3g          # NTFS support
    exfatprogs      # exFAT support
    wine            # Run Windows apps
    winetricks      # Wine helper
    bottles         # Wine GUI manager
    
    # Windows app alternatives
    libreoffice     # MS Office alternative
    thunderbird     # Outlook alternative
    onlyoffice-bin  # Better MS Office compatibility
    
    # For Windows refugees
    firefox         # Familiar browser
    vlc            # Media player
    vscode         # If coming from Windows dev
  ];

  # Enable Windows app compatibility
  programs.steam.enable = true;  # For games
  virtualisation.virtualbox.host.enable = true;  # For Windows VMs if needed
}
```

---

## 🔄 Quick OS Switching Tools

### Install OS Switcher Script:
```bash
# Save as /usr/local/bin/luminous-boot-switch
#!/usr/bin/env bash

echo "🔄 Luminous OS Switcher"
echo "======================"
echo "1) Boot to NixOS (default)"
echo "2) Boot to Windows (once)"
echo "3) Boot to Windows (permanent)"
echo "4) Show boot menu on next restart"
echo "5) Cancel"

read -p "Choice: " choice

case $choice in
  1)
    sudo bootctl set-default "nixos-*"
    echo "✅ NixOS set as default"
    ;;
  2)
    sudo bootctl set-oneshot "auto-windows"
    read -p "Reboot now? (y/n): " reboot
    [[ $reboot == "y" ]] && sudo reboot
    ;;
  3)
    sudo bootctl set-default "auto-windows"
    echo "✅ Windows set as default"
    echo "Run this script again to switch back to NixOS"
    ;;
  4)
    sudo bootctl set-timeout 30
    echo "✅ Boot menu will show for 30 seconds"
    ;;
  *)
    echo "Cancelled"
    ;;
esac
```

---

## 📱 Windows Apps on NixOS

### Native Alternatives (Better Performance):
| Windows App | NixOS Alternative | Quality |
|------------|------------------|---------|
| MS Office | LibreOffice/OnlyOffice | ⭐⭐⭐⭐ |
| Photoshop | GIMP/Krita | ⭐⭐⭐⭐ |
| Premiere | Kdenlive/DaVinci Resolve | ⭐⭐⭐⭐⭐ |
| Visual Studio | VSCode/JetBrains | ⭐⭐⭐⭐⭐ |
| Outlook | Thunderbird/Evolution | ⭐⭐⭐⭐ |
| OneNote | Obsidian/Joplin | ⭐⭐⭐⭐⭐ |
| Teams | Teams for Linux | ⭐⭐⭐⭐ |

### Running Windows Apps via Wine/Bottles:
```nix
# Add to configuration.nix
programs.bottles.enable = true;  # GUI for Wine

# Install Windows app:
bottles  # Launch GUI
# Create new bottle → Install Windows software
```

### When You NEED Windows:
- Adobe Creative Cloud (no good Linux alternative)
- Certain games with anti-cheat
- Proprietary work software
- Some hardware-specific tools

---

## 🎮 Gaming Dual-Boot Strategy

### Share Steam Library:
```bash
# Mount Windows Steam folder
sudo mkdir -p /mnt/windows-steam
sudo mount -t ntfs3 /dev/nvme0n1p4 /mnt/windows-steam

# Link to Linux Steam
ln -s /mnt/windows-steam/SteamLibrary ~/.local/share/Steam/steamapps2

# Now Steam on Linux can see Windows games!
```

---

## 🛡️ Safety Features

### 1. Read-Only Windows Mount
Prevents accidental damage to Windows:
```nix
fileSystems."/mnt/windows" = {
  options = [ "ro" ];  # Read-only
};
```

### 2. Backup Boot Entries
Keep multiple NixOS generations:
```nix
boot.loader.systemd-boot.configurationLimit = 20;
```

### 3. Emergency Recovery
```bash
# If boot breaks, from NixOS USB:
mount /dev/nvme1n1p2 /mnt
mount /dev/nvme1n1p1 /mnt/boot
nixos-enter
nixos-rebuild boot
```

---

## 📊 Transition Timeline

### Week 1-2: Exploration
- Boot NixOS for learning
- Boot Windows for work/gaming
- Install Linux alternatives

### Week 3-4: Migration
- Move development to NixOS
- Configure your ideal environment
- Keep Windows for specific apps

### Month 2: Evaluation
- Track how often you boot Windows
- Many users find they rarely need it!
- Some keep it just for peace of mind

### Month 3+: Your Choice
- Keep dual-boot forever (totally fine!)
- Remove Windows (when ready)
- Or remove NixOS (no judgment!)

---

## 🚀 Quick Start Commands

```bash
# After installing NixOS with dual-boot:

# 1. Install Luminous Nix
cd ~
git clone https://github.com/Luminous-Dynamics/luminous-nix
cd luminous-nix
./install.sh

# 2. Try natural language commands
ask-nix "install firefox"
ask-nix "set up development environment"
ask-nix "configure gaming"

# 3. Switch to Windows when needed
luminous-boot-switch  # Our helper script
```

---

## ❓ FAQ

**Q: Will this slow down my computer?**
A: No! Each OS runs natively. Only uses disk space.

**Q: Can Windows updates break NixOS?**
A: Very rare with UEFI. NixOS manages its own bootloader.

**Q: Can I access Windows files from NixOS?**
A: Yes! Read-only by default, can enable writing.

**Q: What if I want to remove NixOS later?**
A: Boot Windows, delete NixOS partition, expand Windows. Easy!

**Q: Can I share documents between OSes?**
A: Yes! Use a shared NTFS partition or cloud storage.

---

## 🆘 Getting Help

- **Luminous Nix Discord**: [Join our community]
- **NixOS Forums**: discourse.nixos.org
- **Quick fix**: `ask-nix "fix dual boot"`

---

## 🎯 Remember

**Dual-boot is not a commitment to leave Windows!** It's a safe way to explore NixOS while keeping your familiar environment. Many users dual-boot forever, and that's perfectly fine!

The goal is to give you choice and freedom, not force a migration.

---

*"The best transition is the one that happens naturally, not forcefully."*