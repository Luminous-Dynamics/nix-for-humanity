import React, { useEffect, useState } from 'react';
import { invoke } from '@tauri-apps/api/tauri';
import {
  Box,
  Paper,
  Typography,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Chip,
  Button,
  Alert,
  Grid,
  Card,
  CardContent,
  LinearProgress,
} from '@mui/material';
import {
  CheckCircle as CheckIcon,
  Warning as WarningIcon,
  Error as ErrorIcon,
  Info as InfoIcon,
  Refresh as RefreshIcon,
  AutoFixHigh as FixIcon,
} from '@mui/icons-material';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

interface HealthCheck {
  name: string;
  status: 'healthy' | 'warning' | 'error';
  message: string;
  recommendation?: string;
}

interface SystemHealth {
  overall_status: 'healthy' | 'warning' | 'critical';
  checks: HealthCheck[];
  cpu_history: { time: string; value: number }[];
  memory_history: { time: string; value: number }[];
  recommendations: string[];
}

interface HealthPageProps {
  systemHealth?: any;
}

const HealthPage: React.FC<HealthPageProps> = ({ systemHealth }) => {
  const [health, setHealth] = useState<SystemHealth | null>(null);
  const [loading, setLoading] = useState(false);
  const [fixing, setFixing] = useState(false);
  const [message, setMessage] = useState<{ type: 'success' | 'error' | 'info'; text: string } | null>(null);

  useEffect(() => {
    runHealthCheck();
  }, []);

  const runHealthCheck = async () => {
    setLoading(true);
    setMessage(null);
    try {
      const result = await invoke<SystemHealth>('run_health_check');
      setHealth(result);

      if (result.overall_status === 'critical') {
        setMessage({ type: 'error', text: 'Critical issues detected! Immediate action recommended.' });
      } else if (result.overall_status === 'warning') {
        setMessage({ type: 'info', text: 'Some issues detected. Review recommendations below.' });
      } else {
        setMessage({ type: 'success', text: 'System is healthy!' });
      }
    } catch (error) {
      setMessage({ type: 'error', text: `Health check failed: ${error}` });
    } finally {
      setLoading(false);
    }
  };

  const autoFix = async () => {
    setFixing(true);
    setMessage(null);
    try {
      await invoke('auto_fix_issues');
      setMessage({ type: 'success', text: 'Automatic fixes applied!' });
      // Rerun health check
      await runHealthCheck();
    } catch (error) {
      setMessage({ type: 'error', text: `Auto-fix failed: ${error}` });
    } finally {
      setFixing(false);
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'healthy':
        return <CheckIcon color="success" />;
      case 'warning':
        return <WarningIcon color="warning" />;
      case 'error':
      case 'critical':
        return <ErrorIcon color="error" />;
      default:
        return <InfoIcon color="info" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'healthy':
        return 'success';
      case 'warning':
        return 'warning';
      case 'error':
      case 'critical':
        return 'error';
      default:
        return 'default';
    }
  };

  // Generate sample history data if not available
  const generateSampleHistory = () => {
    const now = new Date();
    return Array.from({ length: 10 }, (_, i) => ({
      time: new Date(now.getTime() - i * 60000).toLocaleTimeString(),
      value: Math.random() * 40 + 30,
    })).reverse();
  };

  const cpuHistory = health?.cpu_history || generateSampleHistory();
  const memoryHistory = health?.memory_history || generateSampleHistory();

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4">
          System Health Monitor
        </Typography>
        <Box sx={{ display: 'flex', gap: 2 }}>
          <Button
            variant="outlined"
            startIcon={<RefreshIcon />}
            onClick={runHealthCheck}
            disabled={loading}
          >
            Refresh
          </Button>
          <Button
            variant="contained"
            startIcon={<FixIcon />}
            onClick={autoFix}
            disabled={fixing || !health || health.overall_status === 'healthy'}
          >
            Auto Fix
          </Button>
        </Box>
      </Box>

      {message && (
        <Alert severity={message.type} onClose={() => setMessage(null)} sx={{ mb: 2 }}>
          {message.text}
        </Alert>
      )}

      {loading && <LinearProgress sx={{ mb: 2 }} />}

      {/* Overall Status */}
      {health && (
        <Card sx={{ mb: 3 }}>
          <CardContent>
            <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                {getStatusIcon(health.overall_status)}
                <Typography variant="h5" sx={{ ml: 2 }}>
                  Overall System Status
                </Typography>
              </Box>
              <Chip
                label={health.overall_status.toUpperCase()}
                color={getStatusColor(health.overall_status) as any}
                variant="filled"
              />
            </Box>
          </CardContent>
        </Card>
      )}

      {/* Performance Graphs */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              CPU Usage History
            </Typography>
            <ResponsiveContainer width="100%" height={200}>
              <LineChart data={cpuHistory}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="time" />
                <YAxis domain={[0, 100]} />
                <Tooltip />
                <Line type="monotone" dataKey="value" stroke="#0d7377" strokeWidth={2} />
              </LineChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Memory Usage History
            </Typography>
            <ResponsiveContainer width="100%" height={200}>
              <LineChart data={memoryHistory}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="time" />
                <YAxis domain={[0, 100]} />
                <Tooltip />
                <Line type="monotone" dataKey="value" stroke="#14a085" strokeWidth={2} />
              </LineChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>
      </Grid>

      {/* Health Checks */}
      {health && health.checks.length > 0 && (
        <Paper sx={{ p: 3, mb: 3 }}>
          <Typography variant="h6" gutterBottom>
            Health Checks
          </Typography>
          <List>
            {health.checks.map((check, index) => (
              <ListItem key={index}>
                <ListItemIcon>
                  {getStatusIcon(check.status)}
                </ListItemIcon>
                <ListItemText
                  primary={check.name}
                  secondary={
                    <>
                      {check.message}
                      {check.recommendation && (
                        <Typography variant="body2" color="primary" sx={{ mt: 1 }}>
                          Recommendation: {check.recommendation}
                        </Typography>
                      )}
                    </>
                  }
                />
                <Chip
                  label={check.status}
                  color={getStatusColor(check.status) as any}
                  size="small"
                  variant="outlined"
                />
              </ListItem>
            ))}
          </List>
        </Paper>
      )}

      {/* Recommendations */}
      {health && health.recommendations && health.recommendations.length > 0 && (
        <Paper sx={{ p: 3 }}>
          <Typography variant="h6" gutterBottom>
            Recommendations
          </Typography>
          <List>
            {health.recommendations.map((rec, index) => (
              <ListItem key={index}>
                <ListItemIcon>
                  <InfoIcon color="primary" />
                </ListItemIcon>
                <ListItemText primary={rec} />
              </ListItem>
            ))}
          </List>
        </Paper>
      )}
    </Box>
  );
};

export default HealthPage;
