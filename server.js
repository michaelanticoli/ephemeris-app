require('dotenv').config();
const express = require('express');
const axios = require('axios');
const cors = require('cors');
const path = require('path');

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
    const datetime = req.query.datetime;
    const coordinates = req.query.coordinates;

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
    res.status(500).json({
      error: 'Failed to retrieve natal chart',
      detail: error.response?.data || error.message
    });
  }
});

app.get('/', (req, res) => {
  res.send('Quantumelodies API is running. Use the frontend form to query natal chart data.');
});

app.listen(PORT, () => console.log(`✅ Server running on http://localhost:${PORT}`));
  res.send('Quantumelodies API is live!');
});


app.listen(PORT, () => console.log(`Server running on port ${PORT}`));
cb39a5f8818ab7cfbfcd4b6a96bd24af9104e09e
