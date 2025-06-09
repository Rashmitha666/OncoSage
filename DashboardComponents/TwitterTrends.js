import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Card, List, Typography, Spin, Alert } from 'antd';
import { TwitterOutlined } from '@ant-design/icons';

const { Title, Text } = Typography;

const TwitterTrends = () => {
    const [tweets, setTweets] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        fetchTweets();
        // Refresh tweets every 5 minutes
        const interval = setInterval(fetchTweets, 300000);
        return () => clearInterval(interval);
    }, []);

    const fetchTweets = async () => {
        try {
            setLoading(true);
            // Replace with your backend API endpoint
            const response = await axios.get('/api/twitter/cancer-trends');
            setTweets(response.data);
            setError(null);
        } catch (err) {
            setError('Failed to fetch tweets. Please try again later.');
            console.error('Error fetching tweets:', err);
        } finally {
            setLoading(false);
        }
    };

    return (
        <Card
            title={
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <TwitterOutlined style={{ fontSize: '20px', color: '#1DA1F2' }} />
                    <Title level={4} style={{ margin: 0 }}>Cancer-Related Twitter Trends</Title>
                </div>
            }
            style={{ marginBottom: '20px' }}
        >
            {error && <Alert message={error} type="error" style={{ marginBottom: '16px' }} />}
            
            {loading ? (
                <div style={{ textAlign: 'center', padding: '20px' }}>
                    <Spin size="large" />
                </div>
            ) : (
                <List
                    dataSource={tweets}
                    renderItem={(tweet) => (
                        <List.Item>
                            <div style={{ width: '100%' }}>
                                <div style={{ display: 'flex', alignItems: 'center', marginBottom: '8px' }}>
                                    <img
                                        src={tweet.user.profile_image_url}
                                        alt={tweet.user.name}
                                        style={{
                                            width: '40px',
                                            height: '40px',
                                            borderRadius: '50%',
                                            marginRight: '12px'
                                        }}
                                    />
                                    <div>
                                        <Text strong>{tweet.user.name}</Text>
                                        <Text type="secondary" style={{ marginLeft: '8px' }}>
                                            @{tweet.user.screen_name}
                                        </Text>
                                    </div>
                                </div>
                                <Text>{tweet.text}</Text>
                                <div style={{ marginTop: '8px' }}>
                                    <Text type="secondary">
                                        {new Date(tweet.created_at).toLocaleString()}
                                    </Text>
                                </div>
                            </div>
                        </List.Item>
                    )}
                />
            )}
        </Card>
    );
};

export default TwitterTrends; 