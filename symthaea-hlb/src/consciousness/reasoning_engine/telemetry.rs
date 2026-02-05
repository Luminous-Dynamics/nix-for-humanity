//! Telemetry Export
//!
//! Provides persistence and export capabilities for ReasoningEvent telemetry.
//! Enables offline analysis, audit trails, and long-term calibration tracking.

use std::fs::{File, OpenOptions};
use std::io::{BufWriter, Write};
use std::path::PathBuf;
use std::sync::{Arc, Mutex};

use super::types::ReasoningEvent;

/// Telemetry sink trait - implement this for custom export destinations.
pub trait TelemetrySink: Send + Sync {
    /// Export a single event.
    fn export(&mut self, event: &ReasoningEvent) -> Result<(), TelemetryError>;

    /// Flush any buffered events.
    fn flush(&mut self) -> Result<(), TelemetryError>;

    /// Close the sink.
    fn close(&mut self) -> Result<(), TelemetryError>;
}

/// Telemetry error type.
#[derive(Debug)]
pub enum TelemetryError {
    Io(std::io::Error),
    Serialization(String),
    Database(String),
}

impl From<std::io::Error> for TelemetryError {
    fn from(e: std::io::Error) -> Self {
        TelemetryError::Io(e)
    }
}

impl From<serde_json::Error> for TelemetryError {
    fn from(e: serde_json::Error) -> Self {
        TelemetryError::Serialization(e.to_string())
    }
}

// ─────────────────────────────────────────────────────────────────────────────
// JSON Lines File Sink
// ─────────────────────────────────────────────────────────────────────────────

/// Exports telemetry to a JSON Lines file (one event per line).
///
/// This format is:
/// - Human-readable
/// - Append-friendly (no corruption on crash)
/// - Easy to parse with standard tools (jq, pandas)
pub struct JsonLinesSink {
    writer: BufWriter<File>,
    path: PathBuf,
    events_written: u64,
    auto_flush_interval: u64,
}

impl JsonLinesSink {
    /// Create a new JSON Lines sink at the given path.
    pub fn new(path: impl Into<PathBuf>) -> Result<Self, TelemetryError> {
        let path = path.into();
        let file = OpenOptions::new()
            .create(true)
            .append(true)
            .open(&path)?;

        Ok(Self {
            writer: BufWriter::new(file),
            path,
            events_written: 0,
            auto_flush_interval: 100, // flush every 100 events
        })
    }

    /// Set the auto-flush interval (0 = no auto-flush).
    pub fn with_auto_flush(mut self, interval: u64) -> Self {
        self.auto_flush_interval = interval;
        self
    }

    /// Get the number of events written.
    pub fn events_written(&self) -> u64 {
        self.events_written
    }

    /// Get the file path.
    pub fn path(&self) -> &PathBuf {
        &self.path
    }
}

impl TelemetrySink for JsonLinesSink {
    fn export(&mut self, event: &ReasoningEvent) -> Result<(), TelemetryError> {
        let json = serde_json::to_string(event)?;
        writeln!(self.writer, "{}", json)?;
        self.events_written += 1;

        // Auto-flush
        if self.auto_flush_interval > 0 && self.events_written % self.auto_flush_interval == 0 {
            self.flush()?;
        }

        Ok(())
    }

    fn flush(&mut self) -> Result<(), TelemetryError> {
        self.writer.flush()?;
        Ok(())
    }

    fn close(&mut self) -> Result<(), TelemetryError> {
        self.flush()
    }
}

// ─────────────────────────────────────────────────────────────────────────────
// CSV Sink
// ─────────────────────────────────────────────────────────────────────────────

/// Exports telemetry to a CSV file (for spreadsheet analysis).
pub struct CsvSink {
    writer: BufWriter<File>,
    path: PathBuf,
    events_written: u64,
    header_written: bool,
}

impl CsvSink {
    /// Create a new CSV sink at the given path.
    pub fn new(path: impl Into<PathBuf>) -> Result<Self, TelemetryError> {
        let path = path.into();
        let file = OpenOptions::new()
            .create(true)
            .append(true)
            .open(&path)?;

        let header_written = file.metadata()?.len() > 0;

        let mut sink = Self {
            writer: BufWriter::new(file),
            path,
            events_written: 0,
            header_written,
        };

        if !sink.header_written {
            sink.write_header()?;
        }

        Ok(sink)
    }

    fn write_header(&mut self) -> Result<(), TelemetryError> {
        writeln!(
            self.writer,
            "cycle_id,wall_time_us,budget_tier,phi_raw,reliability,phi_eff,gamma,\
             epistemic_entropy,evs,did_simulate,mcts_iterations,plan_confidence,\
             gate_decision,budget_exceeded"
        )?;
        self.header_written = true;
        Ok(())
    }
}

impl TelemetrySink for CsvSink {
    fn export(&mut self, event: &ReasoningEvent) -> Result<(), TelemetryError> {
        writeln!(
            self.writer,
            "{},{},{:?},{:.6},{:.6},{:.6},{:.2},{:.6},{:.6},{},{},{:.4},{},{}",
            event.cycle_id,
            event.wall_time_us,
            event.budget_tier,
            event.phi_raw,
            event.reliability,
            event.phi_eff,
            event.gamma,
            event.epistemic_entropy,
            event.evs,
            event.did_simulate,
            event.mcts_iterations,
            event.plan_confidence,
            event.gate_decision,
            event.budget_exceeded,
        )?;
        self.events_written += 1;
        Ok(())
    }

    fn flush(&mut self) -> Result<(), TelemetryError> {
        self.writer.flush()?;
        Ok(())
    }

    fn close(&mut self) -> Result<(), TelemetryError> {
        self.flush()
    }
}

// ─────────────────────────────────────────────────────────────────────────────
// Multi-Sink (fan-out to multiple destinations)
// ─────────────────────────────────────────────────────────────────────────────

/// Fan-out sink that writes to multiple destinations.
pub struct MultiSink {
    sinks: Vec<Box<dyn TelemetrySink>>,
}

impl MultiSink {
    /// Create a new multi-sink.
    pub fn new() -> Self {
        Self { sinks: Vec::new() }
    }

    /// Add a sink.
    pub fn add_sink(&mut self, sink: Box<dyn TelemetrySink>) {
        self.sinks.push(sink);
    }

    /// Builder method to add a sink.
    pub fn with_sink(mut self, sink: Box<dyn TelemetrySink>) -> Self {
        self.add_sink(sink);
        self
    }
}

impl Default for MultiSink {
    fn default() -> Self {
        Self::new()
    }
}

impl TelemetrySink for MultiSink {
    fn export(&mut self, event: &ReasoningEvent) -> Result<(), TelemetryError> {
        for sink in &mut self.sinks {
            sink.export(event)?;
        }
        Ok(())
    }

    fn flush(&mut self) -> Result<(), TelemetryError> {
        for sink in &mut self.sinks {
            sink.flush()?;
        }
        Ok(())
    }

    fn close(&mut self) -> Result<(), TelemetryError> {
        for sink in &mut self.sinks {
            sink.close()?;
        }
        Ok(())
    }
}

// ─────────────────────────────────────────────────────────────────────────────
// Thread-Safe Wrapper
// ─────────────────────────────────────────────────────────────────────────────

/// Thread-safe telemetry exporter.
///
/// Wraps any TelemetrySink in Arc<Mutex<>> for concurrent access.
pub struct TelemetryExporter {
    sink: Arc<Mutex<Box<dyn TelemetrySink>>>,
}

impl TelemetryExporter {
    /// Create a new exporter with the given sink.
    pub fn new(sink: Box<dyn TelemetrySink>) -> Self {
        Self {
            sink: Arc::new(Mutex::new(sink)),
        }
    }

    /// Export an event.
    pub fn export(&self, event: &ReasoningEvent) -> Result<(), TelemetryError> {
        let mut sink = self.sink.lock().map_err(|_| {
            TelemetryError::Database("Lock poisoned".to_string())
        })?;
        sink.export(event)
    }

    /// Flush buffered events.
    pub fn flush(&self) -> Result<(), TelemetryError> {
        let mut sink = self.sink.lock().map_err(|_| {
            TelemetryError::Database("Lock poisoned".to_string())
        })?;
        sink.flush()
    }

    /// Close the exporter.
    pub fn close(&self) -> Result<(), TelemetryError> {
        let mut sink = self.sink.lock().map_err(|_| {
            TelemetryError::Database("Lock poisoned".to_string())
        })?;
        sink.close()
    }

    /// Clone the inner Arc for sharing across threads.
    pub fn clone_arc(&self) -> Self {
        Self {
            sink: Arc::clone(&self.sink),
        }
    }
}

impl Clone for TelemetryExporter {
    fn clone(&self) -> Self {
        self.clone_arc()
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::consciousness::temporal_planning::types::BudgetTier;
    use tempfile::NamedTempFile;

    fn test_event() -> ReasoningEvent {
        let mut event = ReasoningEvent::new(42);
        event.phi_raw = 0.8;
        event.reliability = 0.7;
        event.phi_eff = 0.56;
        event.gamma = 2.0;
        event.budget_tier = BudgetTier::Tier2;
        event.wall_time_us = 15000;
        event.gate_decision = "Allowed".to_string();
        event
    }

    #[test]
    fn test_jsonl_sink() {
        let tmp = NamedTempFile::new().unwrap();
        let path = tmp.path().to_path_buf();

        let mut sink = JsonLinesSink::new(&path).unwrap();
        sink.export(&test_event()).unwrap();
        sink.export(&test_event()).unwrap();
        sink.flush().unwrap();

        assert_eq!(sink.events_written(), 2);

        // Verify content
        let content = std::fs::read_to_string(&path).unwrap();
        let lines: Vec<_> = content.lines().collect();
        assert_eq!(lines.len(), 2);

        // Each line should be valid JSON
        for line in lines {
            let _: ReasoningEvent = serde_json::from_str(line).unwrap();
        }
    }

    #[test]
    fn test_csv_sink() {
        let tmp = NamedTempFile::new().unwrap();
        let path = tmp.path().to_path_buf();

        let mut sink = CsvSink::new(&path).unwrap();
        sink.export(&test_event()).unwrap();
        sink.flush().unwrap();

        let content = std::fs::read_to_string(&path).unwrap();
        let lines: Vec<_> = content.lines().collect();
        assert_eq!(lines.len(), 2); // header + 1 event
        assert!(lines[0].contains("cycle_id"));
        assert!(lines[1].contains("42")); // cycle_id
    }

    #[test]
    fn test_multi_sink() {
        let tmp1 = NamedTempFile::new().unwrap();
        let tmp2 = NamedTempFile::new().unwrap();

        let sink1 = JsonLinesSink::new(tmp1.path()).unwrap();
        let sink2 = JsonLinesSink::new(tmp2.path()).unwrap();

        let mut multi = MultiSink::new()
            .with_sink(Box::new(sink1))
            .with_sink(Box::new(sink2));

        multi.export(&test_event()).unwrap();
        multi.flush().unwrap();

        // Both files should have the event
        let c1 = std::fs::read_to_string(tmp1.path()).unwrap();
        let c2 = std::fs::read_to_string(tmp2.path()).unwrap();
        assert_eq!(c1.lines().count(), 1);
        assert_eq!(c2.lines().count(), 1);
    }

    #[test]
    fn test_exporter_thread_safe() {
        let tmp = NamedTempFile::new().unwrap();
        let sink = JsonLinesSink::new(tmp.path()).unwrap();
        let exporter = TelemetryExporter::new(Box::new(sink));

        // Clone and use from "another thread" (same thread for test simplicity)
        let exporter2 = exporter.clone();
        exporter.export(&test_event()).unwrap();
        exporter2.export(&test_event()).unwrap();
        exporter.flush().unwrap();

        let content = std::fs::read_to_string(tmp.path()).unwrap();
        assert_eq!(content.lines().count(), 2);
    }
}
