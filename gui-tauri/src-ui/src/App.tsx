import React, { useState, useEffect } from 'react';
import { invoke } from '@tauri-apps/api/tauri';
import {
  ThemeProvider,
  createTheme,
  CssBaseline,
  Box,
  Drawer,
  AppBar,
  Toolbar,
  Typography,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Container,
  Paper,
  Tab,
  Tabs,
} from '@mui/material';
import {
  Package as PackageIcon,
  Settings as SettingsIcon,
  HealthAndSafety as HealthIcon,
  History as HistoryIcon,
  Chat as ChatIcon,
  Dashboard as DashboardIcon,
} from '@mui/icons-material';

// Import pages
import PackagesPage from './pages/Packages';
import ConfigurationPage from './pages/Configuration';
import HealthPage from './pages/Health';
import GenerationsPage from './pages/Generations';
import AssistantPage from './pages/Assistant';
import DashboardPage from './pages/Dashboard';

// Create dark theme with sacred colors
const theme = createTheme({
  palette: {
    mode: 'dark',
    primary: {
      main: '#0d7377',
    },
    secondary: {
      main: '#14a085',
    },
    background: {
      default: '#1e1e1e',
      paper: '#2d2d2d',
    },
  },
  typography: {
    fontFamily: '"Fira Code", "Roboto Mono", monospace',
  },
});

const drawerWidth = 240;

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;
  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`tabpanel-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  );
}

function App() {
  const [currentTab, setCurrentTab] = useState(0);
  const [systemHealth, setSystemHealth] = useState<any>(null);

  useEffect(() => {
    // Load initial system health
    loadSystemHealth();

    // Refresh every 30 seconds
    const interval = setInterval(loadSystemHealth, 30000);
    return () => clearInterval(interval);
  }, []);

  const loadSystemHealth = async () => {
    try {
      const health = await invoke('get_system_health');
      setSystemHealth(health);
    } catch (error) {
      console.error('Failed to load system health:', error);
    }
  };

  const menuItems = [
    { text: 'Dashboard', icon: <DashboardIcon />, component: <DashboardPage /> },
    { text: 'Packages', icon: <PackageIcon />, component: <PackagesPage /> },
    { text: 'Configuration', icon: <SettingsIcon />, component: <ConfigurationPage /> },
    { text: 'Health', icon: <HealthIcon />, component: <HealthPage systemHealth={systemHealth} /> },
    { text: 'Generations', icon: <HistoryIcon />, component: <GenerationsPage /> },
    { text: 'AI Assistant', icon: <ChatIcon />, component: <AssistantPage /> },
  ];

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Box sx={{ display: 'flex' }}>
        <AppBar
          position="fixed"
          sx={{
            width: `calc(100% - ${drawerWidth}px)`,
            ml: `${drawerWidth}px`,
            backgroundColor: 'background.paper',
          }}
        >
          <Toolbar>
            <Typography variant="h6" noWrap component="div" sx={{ flexGrow: 1 }}>
              Luminous Nix - NixOS Management
            </Typography>
            {systemHealth && (
              <Box sx={{ display: 'flex', gap: 2 }}>
                <Typography variant="body2" color="text.secondary">
                  CPU: {systemHealth.cpu_usage?.toFixed(1)}%
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Memory: {systemHealth.memory_usage?.toFixed(1)}%
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Disk: {systemHealth.disk_usage?.toFixed(1)}%
                </Typography>
              </Box>
            )}
          </Toolbar>
        </AppBar>

        <Drawer
          sx={{
            width: drawerWidth,
            flexShrink: 0,
            '& .MuiDrawer-paper': {
              width: drawerWidth,
              boxSizing: 'border-box',
              backgroundColor: 'background.paper',
            },
          }}
          variant="permanent"
          anchor="left"
        >
          <Toolbar>
            <Typography variant="h6" sx={{ color: 'primary.main' }}>
              🌟 Luminous
            </Typography>
          </Toolbar>
          <List>
            {menuItems.map((item, index) => (
              <ListItem
                button
                key={item.text}
                selected={currentTab === index}
                onClick={() => setCurrentTab(index)}
                sx={{
                  '&.Mui-selected': {
                    backgroundColor: 'primary.main',
                    '&:hover': {
                      backgroundColor: 'primary.dark',
                    },
                  },
                }}
              >
                <ListItemIcon sx={{ color: currentTab === index ? 'white' : 'inherit' }}>
                  {item.icon}
                </ListItemIcon>
                <ListItemText primary={item.text} />
              </ListItem>
            ))}
          </List>
        </Drawer>

        <Box
          component="main"
          sx={{
            flexGrow: 1,
            bgcolor: 'background.default',
            p: 3,
            minHeight: '100vh',
          }}
        >
          <Toolbar />
          {menuItems.map((item, index) => (
            <TabPanel key={index} value={currentTab} index={index}>
              {item.component}
            </TabPanel>
          ))}
        </Box>
      </Box>
    </ThemeProvider>
  );
}

export default App;
