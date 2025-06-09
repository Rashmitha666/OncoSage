const express = require('express');
const router = express.Router();
const Twitter = require('twitter-api-v2');

// Initialize Twitter client
const client = new Twitter({
    appKey: process.env.TWITTER_API_KEY,
    appSecret: process.env.TWITTER_API_SECRET,
    accessToken: process.env.TWITTER_ACCESS_TOKEN,
    accessSecret: process.env.TWITTER_ACCESS_TOKEN_SECRET,
});

// Endpoint to get cancer-related tweets
router.get('/api/twitter/cancer-trends', async (req, res) => {
    try {
        // Search for tweets containing cancer-related keywords
        const searchQuery = '(cancer OR oncology OR tumor) -is:retweet lang:en';
        const tweets = await client.v2.search(searchQuery, {
            'tweet.fields': ['created_at', 'author_id', 'public_metrics'],
            'user.fields': ['name', 'username', 'profile_image_url'],
            'expansions': ['author_id'],
            'max_results': 10,
        });

        // Format the response
        const formattedTweets = tweets.data.map(tweet => {
            const user = tweets.includes.users.find(u => u.id === tweet.author_id);
            return {
                id: tweet.id,
                text: tweet.text,
                created_at: tweet.created_at,
                user: {
                    name: user.name,
                    screen_name: user.username,
                    profile_image_url: user.profile_image_url,
                },
                metrics: tweet.public_metrics,
            };
        });

        res.json(formattedTweets);
    } catch (error) {
        console.error('Twitter API Error:', error);
        res.status(500).json({ error: 'Failed to fetch tweets' });
    }
});

module.exports = router; 