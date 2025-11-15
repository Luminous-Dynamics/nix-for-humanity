import React, { useState, useEffect } from 'react';
import { invoke } from '@tauri-apps/api/tauri';
import {
  Box,
  Paper,
  Typography,
  TextField,
  Button,
  Alert,
  Tabs,
  Tab,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Chip,
  Grid,
  IconButton,
  Tooltip,
} from '@mui/material';
import {
  Save as SaveIcon,
  Refresh as RefreshIcon,
  Add as AddIcon,
  Code as CodeIcon,
  AutoAwesome as AIIcon,
  ContentCopy as CopyIcon,
} from '@mui/icons-material';

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index } = props;
  return (
    <div hidden={value !== index}>
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  );
}

const ConfigurationPage: React.FC = () => {
  const [activeTab, setActiveTab] = useState(0);
  const [configContent, setConfigContent] = useState('');
  const [template, setTemplate] = useState('base');
  const [packages, setPackages] = useState<string[]>([]);
  const [newPackage, setNewPackage] = useState('');
  const [aiPrompt, setAiPrompt] = useState('');
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadCurrentConfig();
  }, []);

  const loadCurrentConfig = async () => {
    try {
      const config = await invoke<string>('load_config');
      setConfigContent(config);
    } catch (err) {
      setError(`Failed to load config: ${err}`);
    }
  };

  const saveConfig = async () => {
    setLoading(true);
    setError(null);
    try {
      await invoke('save_config', { content: configContent });
      setSuccess('Configuration saved successfully!');
    } catch (err) {
      setError(`Failed to save: ${err}`);
    } finally {
      setLoading(false);
    }
  };

  const validateConfig = async () => {
    setLoading(true);
    setError(null);
    try {
      const result = await invoke<boolean>('validate_config', { content: configContent });
      if (result) {
        setSuccess('Configuration is valid!');
      } else {
        setError('Configuration has syntax errors');
      }
    } catch (err) {
      setError(`Validation failed: ${err}`);
    } finally {
      setLoading(false);
    }
  };

  const generateFromTemplate = async () => {
    setLoading(true);
    try {
      const config = await invoke<string>('generate_config', {
        template,
        packages: packages.join(' '),
      });
      setConfigContent(config);
      setSuccess('Configuration generated!');
    } catch (err) {
      setError(`Generation failed: ${err}`);
    } finally {
      setLoading(false);
    }
  };

  const generateFromAI = async () => {
    if (!aiPrompt.trim()) return;

    setLoading(true);
    setError(null);
    try {
      const config = await invoke<string>('ai_generate_config', {
        requirements: aiPrompt,
      });
      setConfigContent(config);
      setSuccess('AI generated configuration!');
    } catch (err) {
      setError(`AI generation failed: ${err}`);
    } finally {
      setLoading(false);
    }
  };

  const addPackage = () => {
    if (newPackage && !packages.includes(newPackage)) {
      setPackages([...packages, newPackage]);
      setNewPackage('');
    }
  };

  const removePackage = (pkg: string) => {
    setPackages(packages.filter(p => p !== pkg));
  };

  const copyToClipboard = () => {
    navigator.clipboard.writeText(configContent);
    setSuccess('Copied to clipboard!');
  };

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Configuration Management
      </Typography>

      <Paper sx={{ mb: 2 }}>
        <Tabs value={activeTab} onChange={(_, v) => setActiveTab(v)}>
          <Tab label="Editor" icon={<CodeIcon />} iconPosition="start" />
          <Tab label="Template Builder" icon={<AddIcon />} iconPosition="start" />
          <Tab label="AI Generator" icon={<AIIcon />} iconPosition="start" />
        </Tabs>
      </Paper>

      {/* Status Messages */}
      {error && (
        <Alert severity="error" onClose={() => setError(null)} sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}
      {success && (
        <Alert severity="success" onClose={() => setSuccess(null)} sx={{ mb: 2 }}>
          {success}
        </Alert>
      )}

      {/* Configuration Editor */}
      <TabPanel value={activeTab} index={0}>
        <Paper sx={{ p: 3 }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
            <Typography variant="h6">Configuration Editor</Typography>
            <Box>
              <Tooltip title="Copy to clipboard">
                <IconButton onClick={copyToClipboard}>
                  <CopyIcon />
                </IconButton>
              </Tooltip>
              <Tooltip title="Refresh">
                <IconButton onClick={loadCurrentConfig}>
                  <RefreshIcon />
                </IconButton>
              </Tooltip>
            </Box>
          </Box>

          <TextField
            fullWidth
            multiline
            rows={20}
            value={configContent}
            onChange={(e) => setConfigContent(e.target.value)}
            variant="outlined"
            sx={{
              fontFamily: 'monospace',
              '& .MuiInputBase-input': {
                fontFamily: '"Fira Code", monospace',
                fontSize: '14px',
              },
            }}
          />

          <Box sx={{ mt: 2, display: 'flex', gap: 2 }}>
            <Button
              variant="contained"
              startIcon={<SaveIcon />}
              onClick={saveConfig}
              disabled={loading}
            >
              Save Configuration
            </Button>
            <Button
              variant="outlined"
              onClick={validateConfig}
              disabled={loading}
            >
              Validate Syntax
            </Button>
          </Box>
        </Paper>
      </TabPanel>

      {/* Template Builder */}
      <TabPanel value={activeTab} index={1}>
        <Paper sx={{ p: 3 }}>
          <Typography variant="h6" gutterBottom>
            Template Builder
          </Typography>

          <Grid container spacing={3}>
            <Grid item xs={12} md={6}>
              <FormControl fullWidth>
                <InputLabel>Base Template</InputLabel>
                <Select
                  value={template}
                  onChange={(e) => setTemplate(e.target.value)}
                  label="Base Template"
                >
                  <MenuItem value="base">Base System</MenuItem>
                  <MenuItem value="desktop">Desktop Environment</MenuItem>
                  <MenuItem value="server">Server Configuration</MenuItem>
                  <MenuItem value="development">Development Setup</MenuItem>
                  <MenuItem value="gaming">Gaming System</MenuItem>
                </Select>
              </FormControl>
            </Grid>

            <Grid item xs={12} md={6}>
              <Box sx={{ display: 'flex', gap: 1 }}>
                <TextField
                  fullWidth
                  label="Add Package"
                  value={newPackage}
                  onChange={(e) => setNewPackage(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && addPackage()}
                />
                <Button
                  variant="contained"
                  onClick={addPackage}
                  sx={{ minWidth: '100px' }}
                >
                  Add
                </Button>
              </Box>
            </Grid>

            <Grid item xs={12}>
              <Typography variant="subtitle1" gutterBottom>
                Selected Packages:
              </Typography>
              <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                {packages.length === 0 ? (
                  <Typography color="text.secondary">No packages selected</Typography>
                ) : (
                  packages.map((pkg) => (
                    <Chip
                      key={pkg}
                      label={pkg}
                      onDelete={() => removePackage(pkg)}
                      color="primary"
                      variant="outlined"
                    />
                  ))
                )}
              </Box>
            </Grid>

            <Grid item xs={12}>
              <Button
                variant="contained"
                onClick={generateFromTemplate}
                disabled={loading}
                fullWidth
              >
                Generate Configuration
              </Button>
            </Grid>
          </Grid>
        </Paper>
      </TabPanel>

      {/* AI Generator */}
      <TabPanel value={activeTab} index={2}>
        <Paper sx={{ p: 3 }}>
          <Typography variant="h6" gutterBottom>
            AI Configuration Generator
          </Typography>

          <TextField
            fullWidth
            multiline
            rows={4}
            value={aiPrompt}
            onChange={(e) => setAiPrompt(e.target.value)}
            placeholder="Describe your ideal system... (e.g., 'Web development environment with Docker, Node.js, and PostgreSQL')"
            variant="outlined"
            sx={{ mb: 2 }}
          />

          <Button
            variant="contained"
            startIcon={<AIIcon />}
            onClick={generateFromAI}
            disabled={loading || !aiPrompt.trim()}
            fullWidth
          >
            Generate with AI
          </Button>

          <Box sx={{ mt: 3 }}>
            <Typography variant="subtitle2" color="text.secondary" gutterBottom>
              Example prompts:
            </Typography>
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
              <Chip
                label="Gaming setup with Steam and Discord"
                onClick={() => setAiPrompt('Gaming setup with Steam and Discord')}
                variant="outlined"
                size="small"
              />
              <Chip
                label="Web server with Nginx, SSL, and PHP"
                onClick={() => setAiPrompt('Web server with Nginx, SSL, and PHP')}
                variant="outlined"
                size="small"
              />
              <Chip
                label="Data science environment with Jupyter and Python"
                onClick={() => setAiPrompt('Data science environment with Jupyter and Python')}
                variant="outlined"
                size="small"
              />
            </Box>
          </Box>
        </Paper>
      </TabPanel>
    </Box>
  );
};

export default ConfigurationPage;
