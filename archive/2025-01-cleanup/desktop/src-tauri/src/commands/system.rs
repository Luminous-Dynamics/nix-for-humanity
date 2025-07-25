use crate::state::AppState;
use serde::{Deserialize, Serialize};
use sysinfo::{System, SystemExt, CpuExt, DiskExt, NetworkExt};
use tauri::State;

#[derive(Debug, Serialize, Deserialize)]
pub struct SystemStats {
    pub cpu_usage: f32,
    pub memory_used: u64,
    pub memory_total: u64,
    pub disk_used: u64,
    pub disk_total: u64,
    pub network_rx: u64,
    pub network_tx: u64,
    pub load_average: [f64; 3],
}

#[derive(Debug, Serialize, Deserialize)]
pub struct SystemInfo {
    pub hostname: String,
    pub kernel_version: String,
    pub os_version: String,
    pub uptime: u64,
    pub cpu_count: usize,
    pub cpu_brand: String,
}

#[tauri::command]
pub async fn get_system_stats(
    state: State<'_, AppState>,
) -> Result<SystemStats, String> {
    let mut sys = System::new_all();
    sys.refresh_all();
    
    let cpu_usage = sys.global_cpu_info().cpu_usage();
    let memory_used = sys.used_memory();
    let memory_total = sys.total_memory();
    
    let (disk_used, disk_total) = sys.disks()
        .iter()
        .fold((0, 0), |(used, total), disk| {
            (used + disk.total_space() - disk.available_space(), 
             total + disk.total_space())
        });
    
    let (network_rx, network_tx) = sys.networks()
        .iter()
        .fold((0, 0), |(rx, tx), (_, network)| {
            (rx + network.received(), tx + network.transmitted())
        });
    
    let load_avg = sys.load_average();
    
    Ok(SystemStats {
        cpu_usage,
        memory_used,
        memory_total,
        disk_used,
        disk_total,
        network_rx,
        network_tx,
        load_average: [load_avg.one, load_avg.five, load_avg.fifteen],
    })
}

#[tauri::command]
pub async fn get_system_info(
    state: State<'_, AppState>,
) -> Result<SystemInfo, String> {
    let mut sys = System::new_all();
    sys.refresh_all();
    
    Ok(SystemInfo {
        hostname: sys.host_name().unwrap_or_else(|| "unknown".to_string()),
        kernel_version: sys.kernel_version().unwrap_or_else(|| "unknown".to_string()),
        os_version: sys.os_version().unwrap_or_else(|| "unknown".to_string()),
        uptime: sys.uptime(),
        cpu_count: sys.cpus().len(),
        cpu_brand: sys.cpus().first()
            .map(|cpu| cpu.brand().to_string())
            .unwrap_or_else(|| "unknown".to_string()),
    })
}