import React, { useEffect, useState } from 'react';
import { invoke } from '@tauri-apps/api/tauri';
import {
  Box,
  Grid,
  Paper,
  Typography,
  Card,
  CardContent,
  LinearProgress,
  Chip,
  Button,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
} from '@mui/material';
import {
  Speed as SpeedIcon,
  Memory as MemoryIcon,
  Storage as StorageIcon,
  NetworkCheck as NetworkIcon,
  CheckCircle as CheckIcon,
  Warning as WarningIcon,
  Error as ErrorIcon,
} from '@mui/icons-material';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from 'recharts';

interface SystemMetrics {
  cpu_usage: number;
  memory_usage: number;
  disk_usage: number;
  network_status: string;
  uptime: number;
  generation: number;
}

interface QuickAction {
  label: string;
  command: string;
  icon: React.ReactNode;
}

const DashboardPage: React.FC = () => {
  const [metrics, setMetrics] = useState<SystemMetrics | null>(null);
  const [recentActions, setRecentActions] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadDashboard();
    const interval = setInterval(loadDashboard, 5000);
    return () => clearInterval(interval);
  }, []);

  const loadDashboard = async () => {
    try {
      const data = await invoke<SystemMetrics>('get_system_metrics');
      setMetrics(data);
      setLoading(false);
    } catch (error) {
      console.error('Failed to load metrics:', error);
      setLoading(false);
    }
  };

  const executeQuickAction = async (command: string) => {
    try {
      await invoke('execute_command', { command });
      setRecentActions(prev => [command, ...prev.slice(0, 4)]);
    } catch (error) {
      console.error('Failed to execute:', error);
    }
  };

  const quickActions: QuickAction[] = [
    { label: 'Update System', command: 'nix-channel --update', icon: <SpeedIcon /> },
    { label: 'Collect Garbage', command: 'nix-collect-garbage', icon: <StorageIcon /> },
    { label: 'Check Health', command: 'system-health', icon: <CheckIcon /> },
    { label: 'List Generations', command: 'list-generations', icon: <MemoryIcon /> },
  ];

  const getStatusColor = (value: number) => {
    if (value < 50) return '#4caf50';
    if (value < 80) return '#ff9800';
    return '#f44336';
  };

  const getStatusIcon = (value: number) => {
    if (value < 50) return <CheckIcon color="success" />;
    if (value < 80) return <WarningIcon color="warning" />;
    return <ErrorIcon color="error" />;
  };

  if (loading) {
    return (
      <Box sx={{ width: '100%', mt: 4 }}>
        <LinearProgress />
      </Box>
    );
  }

  const chartData = metrics ? [
    { name: 'Used', value: metrics.cpu_usage, fill: getStatusColor(metrics.cpu_usage) },
    { name: 'Free', value: 100 - metrics.cpu_usage, fill: '#333' },
  ] : [];

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        System Dashboard
      </Typography>

      {/* Metrics Cards */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <SpeedIcon color="primary" sx={{ mr: 1 }} />
                <Typography variant="h6">CPU Usage</Typography>
              </Box>
              <Typography variant="h3" color="primary">
                {metrics?.cpu_usage.toFixed(1)}%
              </Typography>
              <LinearProgress
                variant="determinate"
                value={metrics?.cpu_usage || 0}
                sx={{ mt: 2, height: 8, borderRadius: 4 }}
                color={metrics && metrics.cpu_usage > 80 ? 'error' : 'primary'}
              />
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <MemoryIcon color="primary" sx={{ mr: 1 }} />
                <Typography variant="h6">Memory</Typography>
              </Box>
              <Typography variant="h3" color="primary">
                {metrics?.memory_usage.toFixed(1)}%
              </Typography>
              <LinearProgress
                variant="determinate"
                value={metrics?.memory_usage || 0}
                sx={{ mt: 2, height: 8, borderRadius: 4 }}
                color={metrics && metrics.memory_usage > 80 ? 'error' : 'primary'}
              />
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <StorageIcon color="primary" sx={{ mr: 1 }} />
                <Typography variant="h6">Disk Usage</Typography>
              </Box>
              <Typography variant="h3" color="primary">
                {metrics?.disk_usage.toFixed(1)}%
              </Typography>
              <LinearProgress
                variant="determinate"
                value={metrics?.disk_usage || 0}
                sx={{ mt: 2, height: 8, borderRadius: 4 }}
                color={metrics && metrics.disk_usage > 80 ? 'error' : 'primary'}
              />
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <NetworkIcon color="primary" sx={{ mr: 1 }} />
                <Typography variant="h6">System Status</Typography>
              </Box>
              <Typography variant="h5" color="primary">
                {metrics?.network_status || 'Online'}
              </Typography>
              <Chip
                label={`Gen ${metrics?.generation || 0}`}
                color="primary"
                variant="outlined"
                sx={{ mt: 2 }}
              />
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Quick Actions and Recent Activity */}
      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Quick Actions
            </Typography>
            <Grid container spacing={2}>
              {quickActions.map((action) => (
                <Grid item xs={6} key={action.label}>
                  <Button
                    variant="outlined"
                    fullWidth
                    startIcon={action.icon}
                    onClick={() => executeQuickAction(action.command)}
                    sx={{ py: 2 }}
                  >
                    {action.label}
                  </Button>
                </Grid>
              ))}
            </Grid>
          </Paper>
        </Grid>

        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Recent Actions
            </Typography>
            {recentActions.length === 0 ? (
              <Typography color="text.secondary">
                No recent actions
              </Typography>
            ) : (
              <List>
                {recentActions.map((action, index) => (
                  <ListItem key={index}>
                    <ListItemIcon>
                      <CheckIcon color="success" />
                    </ListItemIcon>
                    <ListItemText primary={action} />
                  </ListItem>
                ))}
              </List>
            )}
          </Paper>
        </Grid>
      </Grid>

      {/* System Health Summary */}
      <Paper sx={{ p: 3, mt: 3 }}>
        <Typography variant="h6" gutterBottom>
          System Health Summary
        </Typography>
        <Grid container spacing={2}>
          <Grid item xs={12} md={4}>
            <Box sx={{ display: 'flex', alignItems: 'center' }}>
              {metrics && getStatusIcon(metrics.cpu_usage)}
              <Typography sx={{ ml: 1 }}>
                CPU: {metrics?.cpu_usage < 50 ? 'Healthy' : metrics?.cpu_usage < 80 ? 'Moderate' : 'High'}
              </Typography>
            </Box>
          </Grid>
          <Grid item xs={12} md={4}>
            <Box sx={{ display: 'flex', alignItems: 'center' }}>
              {metrics && getStatusIcon(metrics.memory_usage)}
              <Typography sx={{ ml: 1 }}>
                Memory: {metrics?.memory_usage < 50 ? 'Healthy' : metrics?.memory_usage < 80 ? 'Moderate' : 'High'}
              </Typography>
            </Box>
          </Grid>
          <Grid item xs={12} md={4}>
            <Box sx={{ display: 'flex', alignItems: 'center' }}>
              {metrics && getStatusIcon(metrics.disk_usage)}
              <Typography sx={{ ml: 1 }}>
                Disk: {metrics?.disk_usage < 50 ? 'Healthy' : metrics?.disk_usage < 80 ? 'Moderate' : 'High'}
              </Typography>
            </Box>
          </Grid>
        </Grid>
      </Paper>
    </Box>
  );
};

export default DashboardPage;