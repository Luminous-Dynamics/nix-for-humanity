/**
 * Secure Authentication Service for Nix for Humanity
 * Replaces hardcoded credentials with proper authentication
 */

const bcrypt = require('bcrypt');
const jwt = require('jsonwebtoken');
const { randomBytes } = require('crypto');
const fs = require('fs').promises;
const path = require('path');

class AuthenticationService {
  constructor(options = {}) {
    this.configPath = options.configPath || path.join(process.env.HOME, '.config/nix-for-humanity');
    this.usersFile = path.join(this.configPath, 'users.json');
    this.secretsFile = path.join(this.configPath, 'secrets.json');
    this.saltRounds = 12;
    this.tokenExpiry = '24h';
    this.refreshTokenExpiry = '7d';
    
    // Initialize on construction
    this.initPromise = this.initialize();
  }

  async initialize() {
    // Ensure config directory exists
    await fs.mkdir(this.configPath, { recursive: true, mode: 0o700 });
    
    // Load or generate secrets
    this.secrets = await this.loadOrGenerateSecrets();
    
    // Load users database
    this.users = await this.loadUsers();
  }

  async ensureInitialized() {
    await this.initPromise;
  }

  async loadOrGenerateSecrets() {
    try {
      const data = await fs.readFile(this.secretsFile, 'utf8');
      return JSON.parse(data);
    } catch (error) {
      // Generate new secrets if file doesn't exist
      const secrets = {
        jwtSecret: randomBytes(64).toString('hex'),
        refreshSecret: randomBytes(64).toString('hex'),
        rotatedAt: new Date().toISOString()
      };
      
      await fs.writeFile(
        this.secretsFile, 
        JSON.stringify(secrets, null, 2),
        { mode: 0o600 }
      );
      
      return secrets;
    }
  }

  async rotateSecrets() {
    await this.ensureInitialized();
    
    // Keep old secret for grace period
    this.secrets.previousJwtSecret = this.secrets.jwtSecret;
    this.secrets.jwtSecret = randomBytes(64).toString('hex');
    this.secrets.refreshSecret = randomBytes(64).toString('hex');
    this.secrets.rotatedAt = new Date().toISOString();
    
    await fs.writeFile(
      this.secretsFile,
      JSON.stringify(this.secrets, null, 2),
      { mode: 0o600 }
    );
  }

  async loadUsers() {
    try {
      const data = await fs.readFile(this.usersFile, 'utf8');
      return JSON.parse(data);
    } catch (error) {
      // Initialize empty users database
      return {};
    }
  }

  async saveUsers() {
    await fs.writeFile(
      this.usersFile,
      JSON.stringify(this.users, null, 2),
      { mode: 0o600 }
    );
  }

  async registerUser(username, password, options = {}) {
    await this.ensureInitialized();
    
    // Validate username
    if (!username || username.length < 3) {
      throw new Error('Username must be at least 3 characters');
    }
    
    if (!/^[a-zA-Z0-9_-]+$/.test(username)) {
      throw new Error('Username can only contain letters, numbers, - and _');
    }
    
    // Check if user exists
    if (this.users[username]) {
      throw new Error('User already exists');
    }
    
    // Validate password strength
    if (!password || password.length < 8) {
      throw new Error('Password must be at least 8 characters');
    }
    
    // Hash password
    const hashedPassword = await bcrypt.hash(password, this.saltRounds);
    
    // Create user
    this.users[username] = {
      username,
      hashedPassword,
      role: options.role || 'user',
      createdAt: new Date().toISOString(),
      lastLogin: null,
      failedAttempts: 0,
      lockedUntil: null
    };
    
    await this.saveUsers();
    
    return {
      username,
      role: this.users[username].role,
      createdAt: this.users[username].createdAt
    };
  }

  async validateUser(username, password) {
    await this.ensureInitialized();
    
    const user = this.users[username];
    if (!user) {
      // Don't reveal if user exists
      await this.simulateHashDelay();
      return null;
    }
    
    // Check if account is locked
    if (user.lockedUntil && new Date(user.lockedUntil) > new Date()) {
      throw new Error('Account is temporarily locked');
    }
    
    // Verify password
    const valid = await bcrypt.compare(password, user.hashedPassword);
    
    if (!valid) {
      // Increment failed attempts
      user.failedAttempts = (user.failedAttempts || 0) + 1;
      
      // Lock account after 5 failed attempts
      if (user.failedAttempts >= 5) {
        user.lockedUntil = new Date(Date.now() + 15 * 60 * 1000).toISOString(); // 15 minutes
        await this.saveUsers();
        throw new Error('Account locked due to too many failed attempts');
      }
      
      await this.saveUsers();
      return null;
    }
    
    // Reset failed attempts on successful login
    user.failedAttempts = 0;
    user.lockedUntil = null;
    user.lastLogin = new Date().toISOString();
    await this.saveUsers();
    
    return {
      username: user.username,
      role: user.role,
      lastLogin: user.lastLogin
    };
  }

  async simulateHashDelay() {
    // Simulate bcrypt timing to prevent username enumeration
    return new Promise(resolve => setTimeout(resolve, 100));
  }

  generateTokens(user) {
    const payload = {
      username: user.username,
      role: user.role
    };
    
    const accessToken = jwt.sign(
      payload,
      this.secrets.jwtSecret,
      { expiresIn: this.tokenExpiry }
    );
    
    const refreshToken = jwt.sign(
      payload,
      this.secrets.refreshSecret,
      { expiresIn: this.refreshTokenExpiry }
    );
    
    return { accessToken, refreshToken };
  }

  verifyToken(token) {
    try {
      // Try current secret
      return jwt.verify(token, this.secrets.jwtSecret);
    } catch (error) {
      // Try previous secret during rotation grace period
      if (this.secrets.previousJwtSecret) {
        try {
          return jwt.verify(token, this.secrets.previousJwtSecret);
        } catch {
          throw error;
        }
      }
      throw error;
    }
  }

  verifyRefreshToken(token) {
    return jwt.verify(token, this.secrets.refreshSecret);
  }

  async changePassword(username, oldPassword, newPassword) {
    await this.ensureInitialized();
    
    // Validate user
    const validUser = await this.validateUser(username, oldPassword);
    if (!validUser) {
      throw new Error('Invalid credentials');
    }
    
    // Validate new password
    if (!newPassword || newPassword.length < 8) {
      throw new Error('New password must be at least 8 characters');
    }
    
    // Hash new password
    const hashedPassword = await bcrypt.hash(newPassword, this.saltRounds);
    
    // Update user
    this.users[username].hashedPassword = hashedPassword;
    this.users[username].passwordChangedAt = new Date().toISOString();
    
    await this.saveUsers();
  }

  async deleteUser(username) {
    await this.ensureInitialized();
    
    if (!this.users[username]) {
      throw new Error('User not found');
    }
    
    delete this.users[username];
    await this.saveUsers();
  }

  async listUsers() {
    await this.ensureInitialized();
    
    return Object.values(this.users).map(user => ({
      username: user.username,
      role: user.role,
      createdAt: user.createdAt,
      lastLogin: user.lastLogin,
      locked: user.lockedUntil && new Date(user.lockedUntil) > new Date()
    }));
  }
}

module.exports = AuthenticationService;