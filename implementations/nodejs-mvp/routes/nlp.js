// 🧠 NLP Route Handler
const express = require('express');
const router = express.Router();
const Joi = require('joi');

// Import services
const SacredIntentEngine = require('../services/intent-engine-sacred');
const SacredExecutor = require('../services/sacred-executor');
const LearningSystem = require('../services/learning-system');

// Initialize services
const intentEngine = new SacredIntentEngine();
const executor = new SacredExecutor();
const learningSystem = new LearningSystem();

// Input validation schema
const processSchema = Joi.object({
  input: Joi.string().min(1).max(500).required(),
  context: Joi.object({
    previousCommand: Joi.string(),
    sessionId: Joi.string()
  }).optional()
});

// Main NLP processing endpoint
router.post('/process', async (req, res) => {
  try {
    // Validate input
    const { error, value } = processSchema.validate(req.body);
    if (error) {
      return res.status(400).json({
        error: 'Invalid input',
        details: error.details[0].message
      });
    }

    const { input, context = {} } = value;
    console.log(`Processing: "${input}"`);

    // Step 1: Recognize intent with sacred engine
    const intent = await intentEngine.recognize(input);
    console.log('Sacred Intent:', intent);

    if (intent.action === 'unknown' || intent.confidence < 0.5) {
      return res.json({
        success: false,
        message: "I'm not quite sure what you mean. Could you rephrase that?",
        suggestions: intent.suggestions || intentEngine.getSacredSuggestions(input),
        mantra: 'Every question is a path to understanding'
      });
    }

    // Step 2: Execute with sacred executor
    const result = await executor.execute(intent, {
      context: context,
      sessionId: context.sessionId
    });
    console.log('Sacred Result:', result.success ? 'Success' : 'Failed');

    // Step 3: Handle confirmation required
    if (result.requiresConfirmation) {
      return res.json({
        success: false,
        requiresConfirmation: true,
        command: result.command,
        warning: result.warning,
        mantra: result.mantra,
        action: intent.action
      });
    }

    // Step 4: Learn from interaction
    await learningSystem.learn({
      input,
      intent,
      command: result.command,
      result,
      context
    });

    // Step 5: Format response with sacred touch
    const response = {
      success: result.success,
      message: result.message || formatResponse(intent, result),
      data: result.data,
      command: process.env.NODE_ENV === 'development' ? result.command : undefined,
      intent: process.env.NODE_ENV === 'development' ? intent : undefined,
      mantra: result.mantra || intent.mantra
    };

    res.json(response);

  } catch (error) {
    console.error('NLP processing error:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to process your request',
      message: 'Something went wrong. Please try again.'
    });
  }
});

// Handle command confirmation
router.post('/confirm', async (req, res) => {
  try {
    const { intent, confirmed } = req.body;
    
    if (!intent || typeof confirmed !== 'boolean') {
      return res.status(400).json({
        error: 'Invalid confirmation request',
        message: 'Must provide intent and confirmed status'
      });
    }

    if (!confirmed) {
      return res.json({
        success: false,
        message: 'Command cancelled',
        mantra: 'Sacred boundaries protect us'
      });
    }

    // Execute with confirmation
    const confirmedIntent = { ...intent, confirmed: true };
    const result = await executor.execute(confirmedIntent);

    res.json({
      success: result.success,
      message: result.message,
      data: result.data,
      mantra: result.mantra || 'Mindful action manifested'
    });

  } catch (error) {
    console.error('Confirmation error:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to process confirmation',
      mantra: 'Every error is a teacher'
    });
  }
});

// Get command suggestions
router.get('/suggestions', async (req, res) => {
  const suggestions = await learningSystem.getTopCommands();
  res.json({ suggestions });
});

// Get learning data (dev only)
router.get('/learning', async (req, res) => {
  if (process.env.NODE_ENV !== 'development') {
    return res.status(403).json({ error: 'Not available in production' });
  }
  
  const data = await learningSystem.getData();
  res.json(data);
});

// Helper function to format user-friendly responses
function formatResponse(intent, result) {
  if (!result.success) {
    return `I couldn't ${intent.action}. ${result.error || 'Please try again.'}`;
  }

  switch (intent.action) {
    case 'search':
      return `I found ${result.data.count || 'some'} packages matching "${intent.package}".`;
    
    case 'list':
      return `You have ${result.data.count || 'several'} packages installed.`;
    
    case 'info':
      return `Here's information about ${intent.package || 'your system'}.`;
    
    case 'install':
      return result.data.dryRun 
        ? `I would install ${intent.package} for you. (This is a simulation - use 'sudo' commands for actual installation)`
        : `Installing ${intent.package}...`;
    
    case 'remove':
      return result.data.dryRun
        ? `I would remove ${intent.package} for you. (This is a simulation - use 'sudo' commands for actual removal)`
        : `Removing ${intent.package}...`;
    
    case 'update':
      return `${result.data.message || 'System update completed.'}`;
    
    case 'list-updates':
      return result.data.count > 0
        ? `I found ${result.data.count} available updates.`
        : 'Your system is up to date!';
    
    case 'garbage-collect':
      return result.data.dryRun
        ? `Cleanup would free approximately ${result.data.spaceFreed} of disk space. (This is a simulation)`
        : 'System cleanup completed.';
    
    default:
      return result.message || 'Command completed successfully.';
  }
}

module.exports = router;