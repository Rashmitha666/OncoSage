require('dotenv').config();
const express = require('express');
const path = require('path');
const twitterApi = require('./Scripts/twitterApi');

const app = express();
const PORT = process.env.PORT || 5000;

// Use the Twitter API router
app.use(twitterApi);

// Optionally serve static files (if needed for your frontend)
// app.use(express.static(path.join(__dirname, 'build')));

app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
}); 