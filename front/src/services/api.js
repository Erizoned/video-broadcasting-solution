import axios from 'axios';

const API_BASE_URL = 'http://localhost:8001';

const api = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

// Helper function to format stream data for the frontend
const formatStreamData = (stream) => ({
    id: stream.stream_key,
    title: stream.stream_key, // Using stream_key as title for now
    status: stream.status,
    readyTime: stream.ready_time,
    bytesReceived: stream.bytes_received,
    bytesSent: stream.bytes_sent,
    viewersCount: stream.readers_count || (stream.readers ? stream.readers.length : 0),
    tracks: stream.tracks || [],
    isLive: stream.status === 'running',
    // Adding some placeholder data for UI
    streamerName: `Streamer ${stream.stream_key}`,
    category: 'Live Stream',
    description: `Live stream ${stream.stream_key} - ${stream.status === 'running' ? 'Currently Live' : 'Offline'}`,
    thumbnailUrl: `https://picsum.photos/seed/${stream.stream_key}/400/225`,
    streamerAvatar: `https://picsum.photos/seed/avatar-${stream.stream_key}/50/50`
});

export const streamService = {
    // Get all streams
    getAllStreams: async () => {
        try {
            const response = await api.get('/streams');
            return response.data.streams.map(formatStreamData);
        } catch (error) {
            console.error('Error fetching streams:', error);
            throw error;
        }
    },

    // Get stream details by stream key
    getStreamDetails: async (streamKey) => {
        try {
            const response = await api.get(`/streams/${encodeURIComponent(streamKey)}`);
            return formatStreamData(response.data);
        } catch (error) {
            console.error(`Error fetching stream details for ${streamKey}:`, error);
            throw error;
        }
    }
};

export default api; 