/*!
 * Causal Trace Observer (Phase 4)
 *
 * Wrapper observer that automatically injects causal correlation metadata
 * into events, enabling the CausalGraph to build parent-child relationships.
 *
 * ## Usage
 *
 * ```rust,ignore
 * use symthaea::observability::{
 *     TraceObserver, CausalTraceObserver, CorrelationContext,
 * };
 *
 * // Create base observer
 * let base = TraceObserver::new("trace.json")?;
 *
 * // Wrap with causal tracking
 * let correlation_id = "req_user_query_42";
 * let mut observer = CausalTraceObserver::new(base, correlation_id);
 *
 * // Events automatically get metadata with parent-child relationships
 * observer.begin_scope("phi_measurement"); // Push parent
 * observer.record_phi_measurement(event)?;
 *
 * observer.begin_scope("routing"); // Nested scope
 * observer.record_router_selection(event)?; // Has phi_measurement as parent
 * observer.end_scope(); // Pop routing
 *
 * observer.end_scope(); // Pop phi_measurement
 * ```
 */

use anyhow::Result;

use super::{
    SymthaeaObserver, ObserverStats,
    CorrelationContext, EventMetadata,
    RouterSelectionEvent, WorkspaceIgnitionEvent, PhiMeasurementEvent,
    PrimitiveActivationEvent, ResponseGeneratedEvent, SecurityCheckEvent,
    ErrorEvent, LanguageStepEvent, NarrativeSelfEvent, CrossModalBindingEvent,
    GWTIntegrationEvent,
};

/// Observer wrapper that injects causal correlation metadata
pub struct CausalTraceObserver<O: SymthaeaObserver> {
    /// Inner observer to delegate to
    inner: O,
    /// Correlation context for tracking parent-child relationships
    context: CorrelationContext,
    /// Last event ID (for automatic parent linking)
    last_event_id: Option<String>,
    /// Whether to automatically link sequential events
    auto_link: bool,
}

impl<O: SymthaeaObserver> CausalTraceObserver<O> {
    /// Create new causal observer wrapping an inner observer
    pub fn new(inner: O, correlation_id: impl Into<String>) -> Self {
        Self {
            inner,
            context: CorrelationContext::new(correlation_id),
            last_event_id: None,
            auto_link: false,
        }
    }

    /// Enable auto-linking (each event becomes parent of the next)
    pub fn with_auto_link(mut self) -> Self {
        self.auto_link = true;
        self
    }

    /// Begin a causal scope (events in this scope have current parent)
    pub fn begin_scope(&mut self, event_id: impl Into<String>) {
        self.context.push_parent(event_id);
    }

    /// End current causal scope
    pub fn end_scope(&mut self) {
        self.context.pop_parent();
    }

    /// Get reference to the correlation context
    pub fn context(&self) -> &CorrelationContext {
        &self.context
    }

    /// Get mutable reference to the correlation context
    pub fn context_mut(&mut self) -> &mut CorrelationContext {
        &mut self.context
    }

    /// Get the inner observer (consumes self)
    pub fn into_inner(self) -> O {
        self.inner
    }

    /// Create event metadata with proper parent linking
    fn create_metadata(&mut self) -> EventMetadata {
        let metadata = self.context.create_event_metadata();

        if self.auto_link {
            // After creating, push this as parent for next event
            if let Some(ref last_id) = self.last_event_id {
                self.context.pop_parent(); // Remove old auto-parent
            }
            self.last_event_id = Some(metadata.id.clone());
            self.context.push_parent(&metadata.id);
        }

        metadata
    }

    /// Create metadata and inject into event
    fn with_metadata<E, F>(&mut self, mut event: E, inject: F) -> E
    where
        F: FnOnce(&mut E, EventMetadata),
    {
        let metadata = self.create_metadata();
        inject(&mut event, metadata);
        event
    }
}

impl<O: SymthaeaObserver> SymthaeaObserver for CausalTraceObserver<O> {
    fn record_router_selection(&mut self, mut event: RouterSelectionEvent) -> Result<()> {
        let metadata = self.create_metadata();
        event.metadata = Some(metadata);
        self.inner.record_router_selection(event)
    }

    fn record_workspace_ignition(&mut self, mut event: WorkspaceIgnitionEvent) -> Result<()> {
        let metadata = self.create_metadata();
        event.metadata = Some(metadata);
        self.inner.record_workspace_ignition(event)
    }

    fn record_phi_measurement(&mut self, mut event: PhiMeasurementEvent) -> Result<()> {
        let metadata = self.create_metadata();
        event.metadata = Some(metadata);
        self.inner.record_phi_measurement(event)
    }

    fn record_primitive_activation(&mut self, mut event: PrimitiveActivationEvent) -> Result<()> {
        let metadata = self.create_metadata();
        event.metadata = Some(metadata);
        self.inner.record_primitive_activation(event)
    }

    fn record_response_generated(&mut self, mut event: ResponseGeneratedEvent) -> Result<()> {
        let metadata = self.create_metadata();
        event.metadata = Some(metadata);
        self.inner.record_response_generated(event)
    }

    fn record_security_check(&mut self, mut event: SecurityCheckEvent) -> Result<()> {
        let metadata = self.create_metadata();
        event.metadata = Some(metadata);
        self.inner.record_security_check(event)
    }

    fn record_error(&mut self, mut event: ErrorEvent) -> Result<()> {
        let metadata = self.create_metadata();
        event.metadata = Some(metadata);
        self.inner.record_error(event)
    }

    fn record_language_step(&mut self, mut event: LanguageStepEvent) -> Result<()> {
        let metadata = self.create_metadata();
        event.metadata = Some(metadata);
        self.inner.record_language_step(event)
    }

    fn record_narrative_self(&mut self, mut event: NarrativeSelfEvent) -> Result<()> {
        let metadata = self.create_metadata();
        event.metadata = Some(metadata);
        self.inner.record_narrative_self(event)
    }

    fn record_cross_modal_binding(&mut self, mut event: CrossModalBindingEvent) -> Result<()> {
        let metadata = self.create_metadata();
        event.metadata = Some(metadata);
        self.inner.record_cross_modal_binding(event)
    }

    fn record_gwt_integration(&mut self, mut event: GWTIntegrationEvent) -> Result<()> {
        let metadata = self.create_metadata();
        event.metadata = Some(metadata);
        self.inner.record_gwt_integration(event)
    }

    fn finalize(&mut self) -> Result<()> {
        self.inner.finalize()
    }

    fn get_stats(&self) -> Result<ObserverStats> {
        self.inner.get_stats()
    }
}

/// Convenience trait for events that can have metadata injected
pub trait WithCausalMetadata {
    /// Set metadata on this event
    fn set_metadata(&mut self, metadata: EventMetadata);

    /// Get metadata from this event
    fn get_metadata(&self) -> Option<&EventMetadata>;
}

// Implement for all event types
impl WithCausalMetadata for RouterSelectionEvent {
    fn set_metadata(&mut self, metadata: EventMetadata) { self.metadata = Some(metadata); }
    fn get_metadata(&self) -> Option<&EventMetadata> { self.metadata.as_ref() }
}

impl WithCausalMetadata for WorkspaceIgnitionEvent {
    fn set_metadata(&mut self, metadata: EventMetadata) { self.metadata = Some(metadata); }
    fn get_metadata(&self) -> Option<&EventMetadata> { self.metadata.as_ref() }
}

impl WithCausalMetadata for PhiMeasurementEvent {
    fn set_metadata(&mut self, metadata: EventMetadata) { self.metadata = Some(metadata); }
    fn get_metadata(&self) -> Option<&EventMetadata> { self.metadata.as_ref() }
}

impl WithCausalMetadata for PrimitiveActivationEvent {
    fn set_metadata(&mut self, metadata: EventMetadata) { self.metadata = Some(metadata); }
    fn get_metadata(&self) -> Option<&EventMetadata> { self.metadata.as_ref() }
}

impl WithCausalMetadata for ResponseGeneratedEvent {
    fn set_metadata(&mut self, metadata: EventMetadata) { self.metadata = Some(metadata); }
    fn get_metadata(&self) -> Option<&EventMetadata> { self.metadata.as_ref() }
}

impl WithCausalMetadata for SecurityCheckEvent {
    fn set_metadata(&mut self, metadata: EventMetadata) { self.metadata = Some(metadata); }
    fn get_metadata(&self) -> Option<&EventMetadata> { self.metadata.as_ref() }
}

impl WithCausalMetadata for ErrorEvent {
    fn set_metadata(&mut self, metadata: EventMetadata) { self.metadata = Some(metadata); }
    fn get_metadata(&self) -> Option<&EventMetadata> { self.metadata.as_ref() }
}

impl WithCausalMetadata for LanguageStepEvent {
    fn set_metadata(&mut self, metadata: EventMetadata) { self.metadata = Some(metadata); }
    fn get_metadata(&self) -> Option<&EventMetadata> { self.metadata.as_ref() }
}

impl WithCausalMetadata for NarrativeSelfEvent {
    fn set_metadata(&mut self, metadata: EventMetadata) { self.metadata = Some(metadata); }
    fn get_metadata(&self) -> Option<&EventMetadata> { self.metadata.as_ref() }
}

impl WithCausalMetadata for CrossModalBindingEvent {
    fn set_metadata(&mut self, metadata: EventMetadata) { self.metadata = Some(metadata); }
    fn get_metadata(&self) -> Option<&EventMetadata> { self.metadata.as_ref() }
}

impl WithCausalMetadata for GWTIntegrationEvent {
    fn set_metadata(&mut self, metadata: EventMetadata) { self.metadata = Some(metadata); }
    fn get_metadata(&self) -> Option<&EventMetadata> { self.metadata.as_ref() }
}

#[cfg(test)]
mod tests {
    use super::*;
    use super::super::NullObserver;

    #[test]
    fn test_causal_observer_basic() {
        let base = NullObserver::new();
        let mut observer = CausalTraceObserver::new(base, "test_correlation");

        // Record an event
        let event = PhiMeasurementEvent::default();
        assert!(observer.record_phi_measurement(event).is_ok());

        // Check context state
        assert_eq!(observer.context().correlation_id(), "test_correlation");
        assert_eq!(observer.context().event_count(), 1);
    }

    #[test]
    fn test_causal_observer_scopes() {
        let base = NullObserver::new();
        let mut observer = CausalTraceObserver::new(base, "test");

        // Create root event
        let root_event = PhiMeasurementEvent::default();
        observer.record_phi_measurement(root_event).unwrap();

        // Get the event ID from context
        let root_id = observer.context().event_chain()[0].clone();

        // Begin scope with this event as parent
        observer.begin_scope(&root_id);

        // Child events should have parent
        let child_event = RouterSelectionEvent::default();
        observer.record_router_selection(child_event).unwrap();

        // End scope
        observer.end_scope();

        // Verify chain
        assert_eq!(observer.context().event_count(), 2);
    }

    #[test]
    fn test_causal_observer_auto_link() {
        let base = NullObserver::new();
        let mut observer = CausalTraceObserver::new(base, "test").with_auto_link();

        // First event - no parent
        observer.record_phi_measurement(PhiMeasurementEvent::default()).unwrap();

        // Second event - should have first as parent (via auto_link context)
        observer.record_router_selection(RouterSelectionEvent::default()).unwrap();

        // Third event - should have second as parent
        observer.record_workspace_ignition(WorkspaceIgnitionEvent::default()).unwrap();

        assert_eq!(observer.context().event_count(), 3);
    }

    #[test]
    fn test_with_causal_metadata_trait() {
        let mut event = PhiMeasurementEvent::default();
        assert!(event.get_metadata().is_none());

        let metadata = EventMetadata::new("test");
        event.set_metadata(metadata);

        assert!(event.get_metadata().is_some());
        assert!(event.get_metadata().unwrap().id.starts_with("evt_"));
    }
}
