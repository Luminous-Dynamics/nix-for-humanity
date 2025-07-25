// Prevents additional console window on Windows in release, DO NOT REMOVE!!
#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

use tauri::{CustomMenuItem, Manager, SystemTray, SystemTrayEvent, SystemTrayMenu};
use tracing::{info, warn};
use tracing_subscriber;

mod commands;
mod config;
mod nixos;
mod security;
mod state;

use state::AppState;

fn main() {
    // Initialize logging with consciousness-first formatting
    tracing_subscriber::fmt()
        .with_env_filter("nixos_gui=debug,tauri=info")
        .with_target(false)
        .with_thread_ids(false)
        .with_file(true)
        .with_line_number(true)
        .init();

    info!("🌟 NixOS GUI starting with sacred intention...");
    
    // Create system tray with mindful options
    let tray = create_system_tray();
    
    tauri::Builder::default()
        .setup(|app| {
            info!("🧘 Setting up consciousness-first environment...");
            
            // Initialize app state
            let state = AppState::new()?;
            app.manage(state);
            
            // Set sacred window properties
            let window = app.get_window("main").unwrap();
            window.set_title("NixOS Configuration - Sacred Space")?;
            
            // Show sacred greeting
            info!("✨ May your configuration bring clarity and purpose");
            
            Ok(())
        })
        .system_tray(tray)
        .on_system_tray_event(handle_tray_event)
        .invoke_handler(tauri::generate_handler![
            // Configuration commands
            commands::get_configuration,
            commands::validate_configuration,
            commands::save_configuration,
            commands::rebuild_system,
            
            // Package management
            commands::search_packages,
            commands::install_package,
            commands::remove_package,
            commands::list_installed_packages,
            
            // Service management
            commands::list_services,
            commands::get_service_status,
            commands::start_service,
            commands::stop_service,
            commands::enable_service,
            commands::disable_service,
            
            // System monitoring
            commands::get_system_stats,
            commands::get_system_info,
            
            // Sacred features
            commands::set_intention,
            commands::take_sacred_pause,
            commands::get_coherence_level,
            
            // Security
            commands::authenticate,
            commands::check_permissions,
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}

/// Create system tray with consciousness-first options
fn create_system_tray() -> SystemTray {
    let show = CustomMenuItem::new("show".to_string(), "Open Sacred Space");
    let intention = CustomMenuItem::new("intention".to_string(), "Set Intention");
    let pause = CustomMenuItem::new("pause".to_string(), "Take Sacred Pause");
    let quit = CustomMenuItem::new("quit".to_string(), "Complete Session");
    
    let tray_menu = SystemTrayMenu::new()
        .add_item(show)
        .add_separator()
        .add_item(intention)
        .add_item(pause)
        .add_separator()
        .add_item(quit);
    
    SystemTray::new().with_menu(tray_menu)
}

/// Handle system tray events mindfully
fn handle_tray_event(app: &tauri::AppHandle, event: SystemTrayEvent) {
    match event {
        SystemTrayEvent::LeftClick { .. } => {
            let window = app.get_window("main").unwrap();
            window.show().unwrap();
            window.set_focus().unwrap();
        }
        SystemTrayEvent::MenuItemClick { id, .. } => {
            match id.as_str() {
                "show" => {
                    let window = app.get_window("main").unwrap();
                    window.show().unwrap();
                    window.set_focus().unwrap();
                }
                "intention" => {
                    info!("🎯 Opening intention setting dialog...");
                    app.emit_all("set-intention", ()).unwrap();
                }
                "pause" => {
                    info!("⏸️ Initiating sacred pause...");
                    app.emit_all("sacred-pause", ()).unwrap();
                }
                "quit" => {
                    info!("🙏 Completing session with gratitude...");
                    app.exit(0);
                }
                _ => {}
            }
        }
        _ => {}
    }
}