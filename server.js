require('dotenv').config();
const express = require('express');
const axios = require('axios');
const cors = require('cors');
const path = require('path');

const app = express();
const PORT = process.env.PORT || 3000;

// Ensure credentials exist to prevent runtime errors
const CLIENT_ID = process.env.CLIENT_ID;
const CLIENT_SECRET = process.env.CLIENT_SECRET;

if (!CLIENT_ID || !CLIENT_SECRET) {
  console.error('❌ Missing CLIENT_ID or CLIENT_SECRET in .env file');
  process.exit(1);
}

app.use(cors());
app.use(express.static(path.join(__dirname, 'public')));

// Simple in-memory cache for the token
let cachedToken = null;
let tokenExpiry = null;

async function getAccessToken() {
  // Return cached token if it exists and is not expired (buffer of 60 seconds)
  if (cachedToken && tokenExpiry && Date.now() < (tokenExpiry - 60000)) {
    return cachedToken;
  }

  try {
    const tokenUrl = 'https://api.prokerala.com/token';
    const credentials = Buffer.from(`${CLIENT_ID}:${CLIENT_SECRET}`).toString('base64');

    const response = await axios.post(tokenUrl, 'grant_type=client_credentials', {
      headers: {
        'Authorization': `Basic ${credentials}`,
        'Content-Type': 'application/x-www-form-urlencoded'
      }
    });

    cachedToken = response.data.access_token;
    // Set expiry based on response (usually expires_in is in seconds)
    // If expires_in is not provided, default to 1 hour
    const expiresIn = response.data.expires_in || 3600; 
    tokenExpiry = Date.now() + (expiresIn * 1000);

    return cachedToken;
  } catch (error) {
    console.error('Failed to generate access token:', error.message);
    throw new Error('Authentication failed');
  }
}

app.get('/api/current-chart', async (req, res) => {
  try {
    const { datetime, coordinates } = req.query;

    if (!datetime || !coordinates) {
      return res.status(400).json({
        error: 'Missing datetime or coordinates. Both are required.',
        example: {
          datetime: '1985-04-24T19:55:00-04:00',
          coordinates: '40.71,-74.00'
        }
      });
    }

    const token = await getAccessToken();

    const response = await axios.get('https://api.prokerala.com/v2/astrology/natal-chart', {
      headers: { Authorization: `Bearer ${token}` },
      params: {
        datetime,
        coordinates,
        ayanamsa: 0
      }
    });

    res.json(response.data);
  } catch (error) {
    console.error('[Prokerala API ERROR]', error.response?.data || error.message);
    
    const statusCode = error.response?.status || 500;
    res.status(statusCode).json({
      error: 'Failed to retrieve natal chart',
      detail: error.response?.data || error.message
    });
  }
});

app.get('/', (req, res) => {
  res.send('Quantumelodies API is running. Use the frontend form to query natal chart data.');
});

app.listen(PORT, () => console.log(`✅ Server running on http://localhost:${PORT}`));
