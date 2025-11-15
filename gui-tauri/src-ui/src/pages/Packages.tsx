import React, { useState, useCallback } from 'react';
import { invoke } from '@tauri-apps/api/tauri';
import {
  Box,
  Paper,
  TextField,
  Button,
  Grid,
  Card,
  CardContent,
  CardActions,
  Typography,
  Chip,
  CircularProgress,
  Alert,
  IconButton,
  InputAdornment,
  ToggleButtonGroup,
  ToggleButton,
} from '@mui/material';
import {
  Search as SearchIcon,
  Download as InstallIcon,
  Delete as RemoveIcon,
  Category as CategoryIcon,
  ViewList,
  ViewModule,
} from '@mui/icons-material';

interface Package {
  name: string;
  version: string;
  description: string;
  installed: boolean;
  category: string;
}

const categories = [
  'All',
  'Browsers',
  'Editors',
  'Development',
  'Media',
  'Security',
  'System',
  'Games',
];

const PackagesPage: React.FC = () => {
  const [packages, setPackages] = useState<Package[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('All');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');

  const searchPackages = useCallback(async () => {
    if (!searchQuery.trim()) return;

    setLoading(true);
    setError(null);

    try {
      const results = await invoke<Package[]>('search_packages', {
        query: searchQuery,
      });
      setPackages(results);
      setSuccess(`Found ${results.length} packages`);
    } catch (err) {
      setError(`Search failed: ${err}`);
    } finally {
      setLoading(false);
    }
  }, [searchQuery]);

  const installPackage = async (packageName: string) => {
    setLoading(true);
    setError(null);

    try {
      const result = await invoke<any>('install_package', {
        package: packageName,
      });

      if (result.success) {
        setSuccess(`Successfully installed ${packageName}`);
        // Update package state
        setPackages(packages.map(pkg =>
          pkg.name === packageName ? { ...pkg, installed: true } : pkg
        ));
      } else {
        setError(`Failed to install ${packageName}: ${result.error}`);
      }
    } catch (err) {
      setError(`Installation error: ${err}`);
    } finally {
      setLoading(false);
    }
  };

  const loadCategory = (category: string) => {
    setSelectedCategory(category);
    if (category === 'All') {
      setSearchQuery('');
    } else {
      setSearchQuery(category.toLowerCase());
      searchPackages();
    }
  };

  const PackageCard = ({ pkg }: { pkg: Package }) => (
    <Card
      sx={{
        height: '100%',
        display: 'flex',
        flexDirection: 'column',
        backgroundColor: 'background.paper',
        '&:hover': {
          backgroundColor: 'action.hover',
        },
      }}
    >
      <CardContent sx={{ flexGrow: 1 }}>
        <Typography gutterBottom variant="h6" component="div">
          {pkg.name}
        </Typography>
        <Typography variant="body2" color="text.secondary" gutterBottom>
          Version: {pkg.version}
        </Typography>
        <Typography variant="body2" paragraph>
          {pkg.description}
        </Typography>
        <Box sx={{ display: 'flex', gap: 1 }}>
          <Chip
            label={pkg.category}
            size="small"
            color="primary"
            variant="outlined"
          />
          {pkg.installed && (
            <Chip
              label="Installed"
              size="small"
              color="success"
              variant="filled"
            />
          )}
        </Box>
      </CardContent>
      <CardActions>
        {!pkg.installed ? (
          <Button
            size="small"
            startIcon={<InstallIcon />}
            onClick={() => installPackage(pkg.name)}
            disabled={loading}
          >
            Install
          </Button>
        ) : (
          <Button
            size="small"
            startIcon={<RemoveIcon />}
            color="error"
            disabled={loading}
          >
            Remove
          </Button>
        )}
      </CardActions>
    </Card>
  );

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Package Management
      </Typography>

      {/* Search Bar */}
      <Paper sx={{ p: 2, mb: 3 }}>
        <Grid container spacing={2} alignItems="center">
          <Grid item xs>
            <TextField
              fullWidth
              variant="outlined"
              placeholder="Search packages..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && searchPackages()}
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <SearchIcon />
                  </InputAdornment>
                ),
              }}
            />
          </Grid>
          <Grid item>
            <Button
              variant="contained"
              onClick={searchPackages}
              disabled={loading}
              sx={{ height: '56px' }}
            >
              Search
            </Button>
          </Grid>
          <Grid item>
            <ToggleButtonGroup
              value={viewMode}
              exclusive
              onChange={(_, newMode) => newMode && setViewMode(newMode)}
            >
              <ToggleButton value="grid">
                <ViewModule />
              </ToggleButton>
              <ToggleButton value="list">
                <ViewList />
              </ToggleButton>
            </ToggleButtonGroup>
          </Grid>
        </Grid>
      </Paper>

      {/* Categories */}
      <Paper sx={{ p: 2, mb: 3 }}>
        <Typography variant="h6" gutterBottom>
          <CategoryIcon sx={{ verticalAlign: 'middle', mr: 1 }} />
          Categories
        </Typography>
        <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
          {categories.map((category) => (
            <Chip
              key={category}
              label={category}
              onClick={() => loadCategory(category)}
              color={selectedCategory === category ? 'primary' : 'default'}
              variant={selectedCategory === category ? 'filled' : 'outlined'}
            />
          ))}
        </Box>
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

      {/* Loading */}
      {loading && (
        <Box sx={{ display: 'flex', justifyContent: 'center', my: 4 }}>
          <CircularProgress />
        </Box>
      )}

      {/* Package Grid/List */}
      {!loading && packages.length > 0 && (
        <Grid container spacing={2}>
          {packages.map((pkg) => (
            <Grid
              item
              key={pkg.name}
              xs={12}
              sm={viewMode === 'grid' ? 6 : 12}
              md={viewMode === 'grid' ? 4 : 12}
            >
              <PackageCard pkg={pkg} />
            </Grid>
          ))}
        </Grid>
      )}

      {/* Empty State */}
      {!loading && packages.length === 0 && searchQuery && (
        <Paper sx={{ p: 4, textAlign: 'center' }}>
          <Typography variant="h6" color="text.secondary">
            No packages found
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Try a different search term or browse by category
          </Typography>
        </Paper>
      )}

      {/* Initial State */}
      {!loading && packages.length === 0 && !searchQuery && (
        <Paper sx={{ p: 4, textAlign: 'center' }}>
          <Typography variant="h6" color="text.secondary">
            Search for packages or browse by category
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
            Try searching for "firefox", "vim", or "docker"
          </Typography>
        </Paper>
      )}
    </Box>
  );
};

export default PackagesPage;
