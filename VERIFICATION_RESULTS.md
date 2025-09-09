# Verification Results - 2025-09-09 00:27

## Module Status
- luminous_nix.core.native_nix_api.NativeNixAPI: ✅ Working
- luminous_nix.core.json_optimized_nix.JSONOptimizedNix: ✅ Working
- luminous_nix.core.integrated_backend.IntegratedBackend: ✅ Working
- luminous_nix.core.executor.SafeExecutor: ✅ Working
- luminous_nix.services.cache.CacheService: ✅ Working
- luminous_nix.services.search.SearchService: ✅ Working
- luminous_nix.ai.hrm_reasoner_v2.HRMv2NixOSReasoner: ✅ Working
- luminous_nix.embeddings.gemma_encoder.GemmaEncoder: ❌ Not working

## Command Status
- `help`: ✅ (1959ms)
- `list`: ✅ (3240ms)
- `search vim`: ✅ (2013ms)
- `"install firefox" --dry-run`: ❌ (5000ms)

## Performance
- Average response: 3053ms
- Target: <100ms
- Status: ❌ Not met
