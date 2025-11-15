import React, { useState, useEffect, useRef } from 'react';
import { invoke } from '@tauri-apps/api/tauri';
import { listen } from '@tauri-apps/api/event';
import {
  Box,
  Paper,
  Typography,
  TextField,
  Button,
  List,
  ListItem,
  Avatar,
  Chip,
  IconButton,
  CircularProgress,
  Alert,
  ToggleButtonGroup,
  ToggleButton,
  Tooltip,
} from '@mui/material';
import {
  Send as SendIcon,
  SmartToy as AIIcon,
  Person as PersonIcon,
  Clear as ClearIcon,
  ContentCopy as CopyIcon,
  Code as CodeIcon,
  AutoAwesome as MagicIcon,
} from '@mui/icons-material';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  model?: string;
  streaming?: boolean;
}

const AssistantPage: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [streaming, setStreaming] = useState(false);
  const [model, setModel] = useState('auto');
  const [error, setError] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const [streamBuffer, setStreamBuffer] = useState('');

  useEffect(() => {
    // Listen for streaming events
    const unlistenStream = listen('ai-stream-chunk', (event) => {
      const chunk = event.payload as string;
      setStreamBuffer((prev) => prev + chunk);
    });

    const unlistenComplete = listen('ai-stream-complete', () => {
      if (streamBuffer) {
        const lastMessage = messages[messages.length - 1];
        if (lastMessage && lastMessage.streaming) {
          setMessages((prev) => {
            const updated = [...prev];
            updated[updated.length - 1] = {
              ...lastMessage,
              content: streamBuffer,
              streaming: false,
            };
            return updated;
          });
        }
      }
      setStreamBuffer('');
      setStreaming(false);
      setLoading(false);
    });

    return () => {
      unlistenStream.then((fn) => fn());
      unlistenComplete.then((fn) => fn());
    };
  }, [messages, streamBuffer]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const sendMessage = async () => {
    if (!input.trim() || loading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: input,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setLoading(true);
    setError(null);

    try {
      const response = await invoke<any>('ai_chat', {
        query: input,
        useStreaming: streaming,
      });

      if (streaming) {
        // Add placeholder for streaming
        const aiMessage: Message = {
          id: (Date.now() + 1).toString(),
          role: 'assistant',
          content: 'Thinking...',
          timestamp: new Date(),
          model: response.model_used,
          streaming: true,
        };
        setMessages((prev) => [...prev, aiMessage]);
      } else {
        const aiMessage: Message = {
          id: (Date.now() + 1).toString(),
          role: 'assistant',
          content: response.text,
          timestamp: new Date(),
          model: response.model_used,
        };
        setMessages((prev) => [...prev, aiMessage]);
        setLoading(false);
      }
    } catch (err) {
      setError(`Failed to get response: ${err}`);
      setLoading(false);
    }
  };

  const clearConversation = () => {
    setMessages([]);
    setStreamBuffer('');
  };

  const copyMessage = (content: string) => {
    navigator.clipboard.writeText(content);
  };

  const suggestedPrompts = [
    'How do I install a web browser?',
    'Create a development environment for Python',
    'Explain NixOS generations',
    'Generate a configuration for gaming',
    'What packages do I need for web development?',
  ];

  const handleSuggestion = (prompt: string) => {
    setInput(prompt);
  };

  return (
    <Box sx={{ height: 'calc(100vh - 200px)', display: 'flex', flexDirection: 'column' }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Typography variant="h4">
          AI Assistant
        </Typography>
        <Box sx={{ display: 'flex', gap: 2, alignItems: 'center' }}>
          <ToggleButtonGroup
            value={model}
            exclusive
            onChange={(_, value) => value && setModel(value)}
            size="small"
          >
            <ToggleButton value="auto">
              <Tooltip title="Auto-select best model">
                <MagicIcon />
              </Tooltip>
            </ToggleButton>
            <ToggleButton value="hrm">HRM</ToggleButton>
            <ToggleButton value="mistral">Mistral</ToggleButton>
            <ToggleButton value="codellama">Code</ToggleButton>
          </ToggleButtonGroup>
          <Button
            variant="outlined"
            startIcon={<ClearIcon />}
            onClick={clearConversation}
            disabled={messages.length === 0}
          >
            Clear
          </Button>
        </Box>
      </Box>

      {error && (
        <Alert severity="error" onClose={() => setError(null)} sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      {/* Suggested Prompts (show when no messages) */}
      {messages.length === 0 && (
        <Paper sx={{ p: 2, mb: 2 }}>
          <Typography variant="subtitle2" gutterBottom>
            Try asking:
          </Typography>
          <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
            {suggestedPrompts.map((prompt) => (
              <Chip
                key={prompt}
                label={prompt}
                onClick={() => handleSuggestion(prompt)}
                variant="outlined"
                size="small"
              />
            ))}
          </Box>
        </Paper>
      )}

      {/* Messages */}
      <Paper sx={{ flexGrow: 1, overflow: 'auto', p: 2, mb: 2 }}>
        <List>
          {messages.map((message) => (
            <ListItem
              key={message.id}
              sx={{
                flexDirection: message.role === 'user' ? 'row-reverse' : 'row',
                alignItems: 'flex-start',
                mb: 2,
              }}
            >
              <Avatar
                sx={{
                  bgcolor: message.role === 'user' ? 'primary.main' : 'secondary.main',
                  mx: 1,
                }}
              >
                {message.role === 'user' ? <PersonIcon /> : <AIIcon />}
              </Avatar>
              <Paper
                sx={{
                  p: 2,
                  maxWidth: '70%',
                  backgroundColor: message.role === 'user' ? 'primary.dark' : 'background.paper',
                }}
              >
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                  <Typography variant="caption" color="text.secondary">
                    {message.role === 'assistant' && message.model && `${message.model} • `}
                    {message.timestamp.toLocaleTimeString()}
                  </Typography>
                  <IconButton size="small" onClick={() => copyMessage(message.content)}>
                    <CopyIcon fontSize="small" />
                  </IconButton>
                </Box>
                <Typography
                  variant="body1"
                  sx={{
                    whiteSpace: 'pre-wrap',
                    fontFamily: message.content.includes('```') ? 'monospace' : 'inherit',
                  }}
                >
                  {message.streaming && streamBuffer ? streamBuffer : message.content}
                </Typography>
                {message.streaming && (
                  <Box sx={{ display: 'flex', alignItems: 'center', mt: 1 }}>
                    <CircularProgress size={16} sx={{ mr: 1 }} />
                    <Typography variant="caption" color="text.secondary">
                      Streaming response...
                    </Typography>
                  </Box>
                )}
              </Paper>
            </ListItem>
          ))}
          <div ref={messagesEndRef} />
        </List>
      </Paper>

      {/* Input */}
      <Paper sx={{ p: 2 }}>
        <Box sx={{ display: 'flex', gap: 2 }}>
          <TextField
            fullWidth
            variant="outlined"
            placeholder="Ask me anything about NixOS..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && !e.shiftKey && sendMessage()}
            multiline
            maxRows={4}
            disabled={loading}
            InputProps={{
              endAdornment: (
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <Tooltip title="Enable streaming">
                    <ToggleButton
                      value="stream"
                      selected={streaming}
                      onChange={() => setStreaming(!streaming)}
                      size="small"
                    >
                      <CodeIcon />
                    </ToggleButton>
                  </Tooltip>
                </Box>
              ),
            }}
          />
          <Button
            variant="contained"
            onClick={sendMessage}
            disabled={loading || !input.trim()}
            sx={{ minWidth: '100px' }}
            startIcon={loading ? <CircularProgress size={20} /> : <SendIcon />}
          >
            {loading ? 'Thinking...' : 'Send'}
          </Button>
        </Box>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 1 }}>
          <Typography variant="caption" color="text.secondary">
            Powered by HRM (27M) for NixOS • Ollama for conversations
          </Typography>
          <Typography variant="caption" color="text.secondary">
            {streaming ? 'Streaming enabled' : 'Streaming disabled'}
          </Typography>
        </Box>
      </Paper>
    </Box>
  );
};

export default AssistantPage;
