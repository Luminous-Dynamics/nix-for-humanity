# API

HTTP API server for external integration with Symthaea.

## Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| GET | `/phi` | Current Φ value |
| GET | `/graph` | Consciousness graph |
| POST | `/query` | Natural language query |
| WS | `/stream` | Real-time updates |

## Running

```bash
cargo run --bin symthaea-service
# or
cargo run --features service
```

## Configuration

See `api/config.toml` for server configuration options.

## Authentication

API uses token-based authentication. Set `SYMTHAEA_API_TOKEN` environment variable.
