
const express = require('express');
const axios = require('axios');
const cors = require('cors');
const path = require('path');
require('dotenv').config();

const app = express();
const PORT = process.env.PORT || 3000;

const CLIENT_ID = process.env.CLIENT_ID;
const CLIENT_SECRET = process.env.CLIENT_SECRET;

app.use(cors());
app.use(express.static(path.join(__dirname, 'public')));

async function getAccessToken() {
    const tokenUrl = 'https://api.prokerala.com/token';
    const credentials = Buffer.from(`${CLIENT_ID}:${CLIENT_SECRET}`).toString('base64');

    const response = await axios.post(tokenUrl, 'grant_type=client_credentials', {
        headers: {
            'Authorization': `Basic ${credentials}`,
            'Content-Type': 'application/x-www-form-urlencoded'
        }
    });

    return response.data.access_token;
}

app.get('/api/current-chart', async (req, res) => {
    try {
        const token = await getAccessToken();
        const now = new Date().toISOString();
        const response = await axios.get('https://api.prokerala.com/v1/astrology/natal-chart', {
            headers: { Authorization: `Bearer ${token}` },
            params: {
                datetime: now,
                latitude: 40.7128,
                longitude: -74.0060,
                ayanamsa: 1
            }
        });

        res.json(response.data);
    } catch (error) {
        console.error(error.message);
        res.status(500).json({ error: 'Failed to retrieve astrology data' });
    }
});

app.get('/', (req, res) => {
  res.send('Quantumelodies API is live!');
});


app.listen(PORT, () => console.log(`Server running on port ${PORT}`));
