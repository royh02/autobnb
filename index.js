import express from 'express';
import cors from 'cors';

const app = express();

// Enable CORS for React frontend
app.use(cors({
    origin: 'http://localhost:3000',
    credentials: true
}));

// Parse JSON bodies
app.use(express.json());

// Test endpoint
app.get('/api/test', (req, res) => {
    res.json({ message: 'Express server is working!' });
});

// Search endpoint
app.post('/api/search', (req, res) => {
    try {
        const { query } = req.body;
        console.log('Received search query:', query);

        // TODO: Add your search logic here
        
        res.json({
            success: true,
            message: 'Search request received',
            query: query
        });
    } catch (error) {
        console.error('Error processing search:', error);
        res.status(500).json({ 
            success: false,
            error: 'Internal server error' 
        });
    }
});

const PORT = process.env.PORT || 5001;
app.listen(PORT, () => {
    console.log(`Express server is running on http://localhost:${PORT}`);
});
