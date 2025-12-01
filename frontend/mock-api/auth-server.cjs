const jsonServer = require('json-server');
const jwt = require('jsonwebtoken');
const server = jsonServer.create();
const router = jsonServer.router('mock-api/db.json');
const middlewares = jsonServer.defaults();

const SECRET_KEY = 'onestep-secret-key-2024';
const expiresIn = '24h';

// Create a token from a payload
function createToken(payload) {
  return jwt.sign(payload, SECRET_KEY, { expiresIn });
}

// Verify the token
function verifyToken(token) {
  return jwt.verify(token, SECRET_KEY, (err, decode) => (decode !== undefined ? decode : err));
}

// Check if the user exists in database
function isAuthenticated({ username, password }) {
  const db = router.db;
  const users = db.get('users').value();
  return users.find(user => user.username === username && user.password === password);
}

// Add CORS and custom headers
server.use((req, res, next) => {
  res.header('Access-Control-Allow-Origin', '*');
  res.header('Access-Control-Allow-Methods', 'GET, POST, PUT, PATCH, DELETE, OPTIONS');
  res.header('Access-Control-Allow-Headers', 'Content-Type, Authorization');
  res.header('Access-Control-Expose-Headers', 'X-Total-Count, X-Page, X-Page-Size');

  if (req.method === 'OPTIONS') {
    return res.sendStatus(200);
  }

  next();
});

server.use(jsonServer.bodyParser);

// ============================================
// AUTH ENDPOINTS (must be before router)
// ============================================

// Home endpoint
server.get('/', (req, res) => {
  res.json({
    name: 'OneStep Mock API',
    version: '1.0.0',
    status: 'running',
    endpoints: {
      auth: {
        login: 'POST /auth/login',
        refresh: 'POST /auth/token/refresh',
        me: 'GET /auth/me',
        logout: 'POST /auth/logout'
      },
      api: {
        initiatives: 'GET /api/initiatives',
        people: 'GET /api/people',
        organizational_groups: 'GET /api/organizational_groups'
      }
    },
    test_users: [
      { username: 'admin', password: 'admin123', role: 'superuser' },
      { username: 'maria.silva', password: 'senha123', role: 'staff' },
      { username: 'joao.santos', password: 'senha123', role: 'regular' }
    ]
  });
});

// Auth info endpoint
server.get('/auth', (req, res) => {
  res.json({
    message: 'Auth endpoints available',
    endpoints: {
      login: 'POST /auth/login',
      refresh: 'POST /auth/token/refresh',
      me: 'GET /auth/me',
      logout: 'POST /auth/logout'
    },
    note: 'Use POST method for login with {"username": "admin", "password": "admin123"}'
  });
});

// Login endpoint (with and without trailing slash)
const loginHandler = (req, res) => {
  const { username, password } = req.body;

  console.log('Login attempt:', username);

  if (!username || !password) {
    return res.status(400).json({
      detail: 'Username and password are required'
    });
  }

  const user = isAuthenticated({ username, password });

  if (!user) {
    console.log('Login failed: Invalid credentials');
    return res.status(401).json({
      detail: 'Invalid username or password'
    });
  }

  const access_token = createToken({
    id: user.id,
    username: user.username,
    email: user.email
  });

  const refresh_token = createToken({
    id: user.id,
    username: user.username,
    type: 'refresh'
  });

  const { password: _, ...userWithoutPassword } = user;

  console.log('Login successful:', username);

  res.status(200).json({
    access: access_token,
    refresh: refresh_token,
    user: userWithoutPassword
  });
};

server.post('/auth/login', loginHandler);
server.post('/auth/login/', loginHandler);
server.post('/api/auth/login', loginHandler);
server.post('/api/auth/login/', loginHandler);

// Token refresh endpoint (with and without trailing slash)
const refreshHandler = (req, res) => {
  const { refresh } = req.body;

  if (!refresh) {
    return res.status(400).json({
      detail: 'Refresh token is required'
    });
  }

  try {
    const decoded = verifyToken(refresh);

    if (decoded.type !== 'refresh') {
      return res.status(401).json({
        detail: 'Invalid refresh token'
      });
    }

    const access_token = createToken({
      id: decoded.id,
      username: decoded.username,
      email: decoded.email
    });

    res.status(200).json({
      access: access_token
    });
  } catch (err) {
    res.status(401).json({
      detail: 'Invalid or expired refresh token'
    });
  }
};

server.post('/auth/token/refresh', refreshHandler);
server.post('/auth/token/refresh/', refreshHandler);
server.post('/api/auth/token/refresh', refreshHandler);
server.post('/api/auth/token/refresh/', refreshHandler);

// Logout endpoint (with and without trailing slash)
const logoutHandler = (req, res) => {
  res.status(200).json({
    detail: 'Successfully logged out'
  });
};

server.post('/auth/logout', logoutHandler);
server.post('/auth/logout/', logoutHandler);
server.post('/api/auth/logout', logoutHandler);
server.post('/api/auth/logout/', logoutHandler);

// Get current user endpoint (with and without trailing slash)
const meHandler = (req, res) => {
  const authHeader = req.headers.authorization;

  if (!authHeader || !authHeader.startsWith('Bearer ')) {
    return res.status(401).json({
      detail: 'Authentication credentials were not provided'
    });
  }

  const token = authHeader.substring(7);

  try {
    const decoded = verifyToken(token);
    const db = router.db;
    const user = db.get('users').find({ id: decoded.id }).value();

    if (!user) {
      return res.status(404).json({
        detail: 'User not found'
      });
    }

    const { password: _, ...userWithoutPassword } = user;
    res.status(200).json(userWithoutPassword);
  } catch (err) {
    res.status(401).json({
      detail: 'Invalid or expired token'
    });
  }
};

server.get('/auth/me', meHandler);
server.get('/auth/me/', meHandler);
server.get('/api/auth/me', meHandler);
server.get('/api/auth/me/', meHandler);

// ============================================
// MIDDLEWARES
// ============================================

// Add delay to simulate network latency
server.use((req, res, next) => {
  setTimeout(next, 300);
});

// Use default middlewares
server.use(middlewares);

// Rewrite routes to match Django API structure
server.use(jsonServer.rewriter({
  '/api/initiatives/:id/hierarchy': '/initiatives?parent_id=:id',
  '/api/initiatives/:id/children': '/initiatives?parent_id=:id',
  '/api/initiatives/:id/coordinator-changes': '/coordinator_changes?initiative.id=:id',
  '/api/initiatives/failed-imports': '/failed_imports',
  '/api/*': '/$1',
}));

// Middleware to transform list responses to Django pagination format
server.use((req, res, next) => {
  const originalSend = res.send;
  
  res.send = function(data) {
    // Only transform GET requests to list endpoints (not detail endpoints)
    if (req.method === 'GET' && !req.url.match(/\/\d+\/?$/)) {
      try {
        const parsedData = typeof data === 'string' ? JSON.parse(data) : data;
        
        // If it's an array, transform to paginated response
        if (Array.isArray(parsedData)) {
          const page = parseInt(req.query.page || '1');
          const pageSize = parseInt(req.query.page_size || '10');
          const start = (page - 1) * pageSize;
          const end = start + pageSize;
          const paginatedData = parsedData.slice(start, end);
          
          const paginatedResponse = {
            count: parsedData.length,
            next: end < parsedData.length ? `${req.protocol}://${req.get('host')}${req.path}?page=${page + 1}&page_size=${pageSize}` : null,
            previous: page > 1 ? `${req.protocol}://${req.get('host')}${req.path}?page=${page - 1}&page_size=${pageSize}` : null,
            results: paginatedData
          };
          
          return originalSend.call(this, JSON.stringify(paginatedResponse));
        }
      } catch (e) {
        // If parsing fails, just send original data
      }
    }
    
    return originalSend.call(this, data);
  };
  
  next();
});

// Use router for data endpoints
server.use(router);

// Start server
const PORT = 8000;
server.listen(PORT, () => {
  console.log(`\n🚀 Mock API Server is running!`);
  console.log(`\n📍 Endpoints:`);
  console.log(`   - Home: http://localhost:${PORT}`);
  console.log(`   - Auth: http://localhost:${PORT}/auth/login`);
  console.log(`   - API:  http://localhost:${PORT}/api/initiatives`);
  console.log(`\n👤 Test Users:`);
  console.log(`   - Username: admin       | Password: admin123 (Superuser)`);
  console.log(`   - Username: maria.silva | Password: senha123 (Staff)`);
  console.log(`   - Username: joao.santos | Password: senha123 (Regular)`);
  console.log(`\n💡 Test login:`);
  console.log(`   curl -X POST http://localhost:${PORT}/auth/login \\`);
  console.log(`     -H "Content-Type: application/json" \\`);
  console.log(`     -d '{"username": "admin", "password": "admin123"}'`);
  console.log(`\n✨ Ready to accept requests!\n`);
});
