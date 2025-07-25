# Example Plugin for NixOS GUI

This plugin demonstrates the capabilities of the NixOS GUI plugin system.

## Features

- **Dashboard Widget**: Shows system statistics with periodic updates
- **Menu Integration**: Adds menu items to the GUI
- **Settings Panel**: Configurable options for plugin behavior
- **Event Handling**: Responds to system events
- **Data Persistence**: Saves and loads plugin data
- **Notifications**: Shows user notifications

## Installation

1. Copy this plugin to your plugins directory:
   ```bash
   cp -r example-plugin ~/.config/nixos-gui/plugins/
   ```

2. Enable the plugin in NixOS GUI settings or via configuration:
   ```json
   {
     "enabledPlugins": ["example-plugin"]
   }
   ```

## Development

### Plugin Structure

```
example-plugin/
├── plugin.json      # Plugin manifest
├── index.js         # Main plugin code
├── README.md        # Documentation
└── assets/          # Optional assets
    ├── icon.png
    └── styles.css
```

### API Usage

The plugin demonstrates usage of:

- **UI API**: Menu items, widgets, notifications, settings
- **System API**: Package search, service status
- **Storage API**: Persistent data storage
- **Events API**: Event subscription and emission
- **HTTP API**: External API requests (with restrictions)

### Testing

Test the plugin in development mode:

```bash
npm run dev --plugin=example-plugin
```

## Configuration

The plugin supports the following settings:

- **refreshInterval**: How often to update the widget (milliseconds)
- **showNotifications**: Whether to show notifications for events

## Security

This plugin requests the following permissions:

- `ui.menu` - Add menu items
- `ui.widget` - Create dashboard widgets
- `ui.notify` - Show notifications
- `ui.settings` - Register settings panel
- `system.packages.read` - Read package information
- `storage.read` - Read saved data
- `storage.write` - Save data
- `events.subscribe` - Listen to system events
- `events.emit` - Emit custom events

## License

MIT