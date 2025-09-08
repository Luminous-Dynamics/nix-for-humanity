import React, { useState, useEffect } from 'react';
import { invoke } from '@tauri-apps/api/tauri';
import {
  Box,
  Paper,
  Typography,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  IconButton,
  Button,
  Alert,
  Chip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Tooltip,
} from '@mui/material';
import {
  Restore as RestoreIcon,
  Delete as DeleteIcon,
  Compare as CompareIcon,
  Info as InfoIcon,
  Save as SaveIcon,
  ArrowBack as RollbackIcon,
} from '@mui/icons-material';

interface Generation {
  id: number;
  date: string;
  current: boolean;
  description?: string;
  packages_count: number;
  size_mb: number;
}

const GenerationsPage: React.FC = () => {
  const [generations, setGenerations] = useState<Generation[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [selectedGen, setSelectedGen] = useState<Generation | null>(null);
  const [compareDialog, setCompareDialog] = useState(false);
  const [compareGen1, setCompareGen1] = useState<number | null>(null);
  const [compareGen2, setCompareGen2] = useState<number | null>(null);
  const [comparisonResult, setComparisonResult] = useState<string>('');
  const [deleteConfirm, setDeleteConfirm] = useState<number | null>(null);

  useEffect(() => {
    loadGenerations();
  }, []);

  const loadGenerations = async () => {
    setLoading(true);
    try {
      const gens = await invoke<Generation[]>('list_generations');
      setGenerations(gens);
    } catch (err) {
      setError(`Failed to load generations: ${err}`);
    } finally {
      setLoading(false);
    }
  };

  const switchToGeneration = async (id: number) => {
    setLoading(true);
    setError(null);
    try {
      await invoke('switch_generation', { id });
      setSuccess(`Switched to generation ${id}. System will reboot.`);
      await loadGenerations();
    } catch (err) {
      setError(`Failed to switch: ${err}`);
    } finally {
      setLoading(false);
    }
  };

  const deleteGeneration = async (id: number) => {
    setLoading(true);
    setError(null);
    try {
      await invoke('delete_generation', { id });
      setSuccess(`Generation ${id} deleted.`);
      setDeleteConfirm(null);
      await loadGenerations();
    } catch (err) {
      setError(`Failed to delete: ${err}`);
    } finally {
      setLoading(false);
    }
  };

  const compareGenerations = async () => {
    if (!compareGen1 || !compareGen2) return;
    
    setLoading(true);
    try {
      const result = await invoke<string>('compare_generations', {
        gen1: compareGen1,
        gen2: compareGen2,
      });
      setComparisonResult(result);
    } catch (err) {
      setError(`Comparison failed: ${err}`);
    } finally {
      setLoading(false);
    }
  };

  const rollbackToGeneration = async (id: number) => {
    setLoading(true);
    setError(null);
    try {
      await invoke('rollback_generation', { id });
      setSuccess(`Rolled back to generation ${id}`);
      await loadGenerations();
    } catch (err) {
      setError(`Rollback failed: ${err}`);
    } finally {
      setLoading(false);
    }
  };

  const formatSize = (mb: number) => {
    if (mb < 1024) return `${mb.toFixed(1)} MB`;
    return `${(mb / 1024).toFixed(2)} GB`;
  };

  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr);
    return date.toLocaleString();
  };

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        System Generations
      </Typography>

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

      <Paper sx={{ p: 2, mb: 2 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Typography variant="h6">
            {generations.length} Generations
          </Typography>
          <Button
            variant="outlined"
            startIcon={<CompareIcon />}
            onClick={() => setCompareDialog(true)}
          >
            Compare Generations
          </Button>
        </Box>
      </Paper>

      <Paper>
        <List>
          {generations.map((gen) => (
            <ListItem
              key={gen.id}
              sx={{
                backgroundColor: gen.current ? 'action.selected' : 'inherit',
                borderLeft: gen.current ? '4px solid' : 'none',
                borderLeftColor: 'primary.main',
              }}
            >
              <ListItemText
                primary={
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <Typography variant="h6">
                      Generation {gen.id}
                    </Typography>
                    {gen.current && (
                      <Chip label="CURRENT" color="primary" size="small" />
                    )}
                  </Box>
                }
                secondary={
                  <Box>
                    <Typography variant="body2" color="text.secondary">
                      {formatDate(gen.date)}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      {gen.packages_count} packages • {formatSize(gen.size_mb)}
                    </Typography>
                    {gen.description && (
                      <Typography variant="body2" sx={{ mt: 1 }}>
                        {gen.description}
                      </Typography>
                    )}
                  </Box>
                }
              />
              <ListItemSecondaryAction>
                <Box sx={{ display: 'flex', gap: 1 }}>
                  {!gen.current && (
                    <>
                      <Tooltip title="Switch to this generation">
                        <IconButton
                          edge="end"
                          onClick={() => switchToGeneration(gen.id)}
                          disabled={loading}
                        >
                          <RestoreIcon />
                        </IconButton>
                      </Tooltip>
                      <Tooltip title="Rollback to this generation">
                        <IconButton
                          edge="end"
                          onClick={() => rollbackToGeneration(gen.id)}
                          disabled={loading}
                        >
                          <RollbackIcon />
                        </IconButton>
                      </Tooltip>
                      <Tooltip title="Delete this generation">
                        <IconButton
                          edge="end"
                          onClick={() => setDeleteConfirm(gen.id)}
                          disabled={loading}
                        >
                          <DeleteIcon />
                        </IconButton>
                      </Tooltip>
                    </>
                  )}
                  <Tooltip title="Generation details">
                    <IconButton
                      edge="end"
                      onClick={() => setSelectedGen(gen)}
                    >
                      <InfoIcon />
                    </IconButton>
                  </Tooltip>
                </Box>
              </ListItemSecondaryAction>
            </ListItem>
          ))}
        </List>
      </Paper>

      {/* Compare Dialog */}
      <Dialog
        open={compareDialog}
        onClose={() => setCompareDialog(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>Compare Generations</DialogTitle>
        <DialogContent>
          <Box sx={{ display: 'flex', gap: 2, mt: 2 }}>
            <TextField
              select
              label="Generation 1"
              value={compareGen1 || ''}
              onChange={(e) => setCompareGen1(Number(e.target.value))}
              fullWidth
              SelectProps={{ native: true }}
            >
              <option value="">Select...</option>
              {generations.map((gen) => (
                <option key={gen.id} value={gen.id}>
                  Generation {gen.id} {gen.current && '(current)'}
                </option>
              ))}
            </TextField>
            <TextField
              select
              label="Generation 2"
              value={compareGen2 || ''}
              onChange={(e) => setCompareGen2(Number(e.target.value))}
              fullWidth
              SelectProps={{ native: true }}
            >
              <option value="">Select...</option>
              {generations.map((gen) => (
                <option key={gen.id} value={gen.id}>
                  Generation {gen.id} {gen.current && '(current)'}
                </option>
              ))}
            </TextField>
          </Box>
          {comparisonResult && (
            <Paper sx={{ p: 2, mt: 2, backgroundColor: 'background.default' }}>
              <Typography variant="body2" component="pre" sx={{ fontFamily: 'monospace' }}>
                {comparisonResult}
              </Typography>
            </Paper>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setCompareDialog(false)}>Cancel</Button>
          <Button
            onClick={compareGenerations}
            variant="contained"
            disabled={!compareGen1 || !compareGen2 || compareGen1 === compareGen2}
          >
            Compare
          </Button>
        </DialogActions>
      </Dialog>

      {/* Delete Confirmation Dialog */}
      <Dialog
        open={deleteConfirm !== null}
        onClose={() => setDeleteConfirm(null)}
      >
        <DialogTitle>Confirm Deletion</DialogTitle>
        <DialogContent>
          <Typography>
            Are you sure you want to delete generation {deleteConfirm}?
            This action cannot be undone.
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDeleteConfirm(null)}>Cancel</Button>
          <Button
            onClick={() => deleteGeneration(deleteConfirm!)}
            color="error"
            variant="contained"
          >
            Delete
          </Button>
        </DialogActions>
      </Dialog>

      {/* Generation Details Dialog */}
      {selectedGen && (
        <Dialog
          open={Boolean(selectedGen)}
          onClose={() => setSelectedGen(null)}
          maxWidth="sm"
          fullWidth
        >
          <DialogTitle>Generation {selectedGen.id} Details</DialogTitle>
          <DialogContent>
            <List>
              <ListItem>
                <ListItemText
                  primary="Date Created"
                  secondary={formatDate(selectedGen.date)}
                />
              </ListItem>
              <ListItem>
                <ListItemText
                  primary="Package Count"
                  secondary={selectedGen.packages_count}
                />
              </ListItem>
              <ListItem>
                <ListItemText
                  primary="Size"
                  secondary={formatSize(selectedGen.size_mb)}
                />
              </ListItem>
              {selectedGen.description && (
                <ListItem>
                  <ListItemText
                    primary="Description"
                    secondary={selectedGen.description}
                  />
                </ListItem>
              )}
              <ListItem>
                <ListItemText
                  primary="Status"
                  secondary={selectedGen.current ? 'Currently Active' : 'Inactive'}
                />
              </ListItem>
            </List>
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setSelectedGen(null)}>Close</Button>
          </DialogActions>
        </Dialog>
      )}
    </Box>
  );
};

export default GenerationsPage;