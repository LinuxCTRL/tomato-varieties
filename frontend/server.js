const express = require('express');
const axios = require('axios');
const path = require('path');
const cors = require('cors');

const app = express();
const PORT = process.env.PORT || 3000;
const API_BASE_URL = process.env.API_BASE_URL || 'http://localhost:5000';

// Middleware
app.use(cors());
app.use(express.static('public'));
app.use(express.json());
app.set('view engine', 'ejs');
app.set('views', path.join(__dirname, 'views'));

// Helper function to make API calls
async function callAPI(endpoint) {
    try {
        const response = await axios.get(`${API_BASE_URL}${endpoint}`);
        return response.data;
    } catch (error) {
        console.error(`API Error for ${endpoint}:`, error.message);
        return { error: error.message };
    }
}

// Routes

// Home page - Display all tomato varieties
app.get('/', async (req, res) => {
    try {
        const data = await callAPI('/varieties');
        
        if (data.error) {
            return res.render('error', { 
                error: data.error,
                message: 'Failed to load tomato varieties. Make sure the Python API is running.'
            });
        }
        
        res.render('index', { 
            varieties: data.varieties || [],
            totalCount: data.total_count || 0,
            scrapedAt: data.scraped_at || '',
            source: data.source || ''
        });
    } catch (error) {
        res.render('error', { 
            error: 'Connection Error',
            message: 'Could not connect to the API. Make sure the Python backend is running on port 5000.'
        });
    }
});

// Search page
app.get('/search', async (req, res) => {
    const query = req.query.q || '';
    
    if (!query) {
        return res.render('search', { 
            query: '',
            results: [],
            totalFound: 0
        });
    }
    
    try {
        const data = await callAPI(`/search?q=${encodeURIComponent(query)}`);
        
        res.render('search', { 
            query: query,
            results: data.results || [],
            totalFound: data.total_found || 0,
            error: data.error || null
        });
    } catch (error) {
        res.render('search', { 
            query: query,
            results: [],
            totalFound: 0,
            error: 'Search failed. Please try again.'
        });
    }
});

// Individual tomato variety page (dynamic route)
app.get('/tomato/:identifier', async (req, res) => {
    const identifier = req.params.identifier;
    
    try {
        const data = await callAPI(`/variety/${encodeURIComponent(identifier)}`);
        
        if (data.error) {
            return res.render('error', { 
                error: 'Variety Not Found',
                message: `No tomato variety found with name or slug: "${identifier}"`
            });
        }
        
        res.render('variety-detail', { 
            variety: data,
            identifier: identifier
        });
    } catch (error) {
        res.render('error', { 
            error: 'Error Loading Variety',
            message: 'Could not load the tomato variety details.'
        });
    }
});

// Stats page
app.get('/stats', async (req, res) => {
    try {
        const data = await callAPI('/stats');
        
        if (data.error) {
            return res.render('error', { 
                error: data.error,
                message: 'Failed to load statistics.'
            });
        }
        
        res.render('stats', { stats: data });
    } catch (error) {
        res.render('error', { 
            error: 'Stats Error',
            message: 'Could not load statistics.'
        });
    }
});

// Loading Animations Demo page
app.get('/loading-demo', (req, res) => {
    res.render('loading-demo');
});

// API proxy routes (for AJAX calls from frontend)
app.get('/api/varieties', async (req, res) => {
    const data = await callAPI('/varieties');
    res.json(data);
});

app.get('/api/varieties/:identifier', async (req, res) => {
    const data = await callAPI(`/variety/${req.params.identifier}`);
    res.json(data);
});

app.get('/api/search', async (req, res) => {
    const query = req.query.q || '';
    const data = await callAPI(`/search?q=${encodeURIComponent(query)}`);
    res.json(data);
});

app.get('/api/refresh', async (req, res) => {
    const data = await callAPI('/refresh');
    res.json(data);
});

// Scraper control endpoints
app.post('/api/scrape', async (req, res) => {
    try {
        const response = await axios.post(`${API_BASE_URL}/scrape`);
        res.json(response.data);
    } catch (error) {
        console.error('Scraper start error:', error.message);
        res.json({ error: error.message });
    }
});

app.get('/api/scrape/status', async (req, res) => {
    const data = await callAPI('/scrape/status');
    res.json(data);
});

// 404 handler
app.use((req, res) => {
    res.status(404).render('error', {
        error: '404 - Page Not Found',
        message: `The page "${req.url}" was not found.`
    });
});

// Start server
app.listen(PORT, () => {
    console.log(`🍅 Tomato Varieties Frontend Server running on port ${PORT}`);
    console.log(`📱 Open your browser to: http://localhost:${PORT}`);
    console.log(`🔗 API Backend should be running on: ${API_BASE_URL}`);
    console.log('');
    console.log('Available routes:');
    console.log('  GET  /                     - Home page (all varieties)');
    console.log('  GET  /search?q=<query>     - Search varieties');
    console.log('  GET  /tomato/<name>        - Individual variety details');
    console.log('  GET  /stats                - Database statistics');
    console.log('  GET  /api/*                - API proxy endpoints');
});