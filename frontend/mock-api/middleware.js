module.exports = (req, res, next) => {
  // Add delay to simulate network latency
  setTimeout(() => {
    // Add pagination headers
    if (req.method === 'GET' && req.url.includes('?')) {
      const url = new URL(req.url, `http://${req.headers.host}`);
      const page = parseInt(url.searchParams.get('page') || '1');
      const pageSize = parseInt(url.searchParams.get('page_size') || '10');
      
      // Set pagination headers
      res.setHeader('X-Total-Count', '100');
      res.setHeader('X-Page', page.toString());
      res.setHeader('X-Page-Size', pageSize.toString());
    }

    // Add CORS headers
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'GET, POST, PUT, PATCH, DELETE, OPTIONS');
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization');
    res.setHeader('Access-Control-Expose-Headers', 'X-Total-Count, X-Page, X-Page-Size');

    // Handle OPTIONS requests
    if (req.method === 'OPTIONS') {
      res.sendStatus(200);
      return;
    }

    next();
  }, 300); // 300ms delay
};
