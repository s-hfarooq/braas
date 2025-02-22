import React, { useEffect, useState } from 'react';

interface VideoItem {
  id: number;
  color: string;
  description: string;
  topText: string;
  bottomText: string;
}

interface GenerateResponse {
  result: string;
}

const API_URL = 'http://localhost:5000';

const TOPICS = [
  "cat fails",
  "cooking disaster",
  "dance challenge",
  "gaming rage",
  "parkour fail",
  "cute puppy",
  "skateboard trick",
  "magic trick fail",
  "unexpected ending",
  "talent show moment"
];

const VideoFeed: React.FC = () => {
  const [videos, setVideos] = useState<VideoItem[]>([]);
  const [loading, setLoading] = useState(false);

  // Generate a random color
  const getRandomColor = () => {
    const colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEEAD', '#D4A5A5', '#9B59B6'];
    return colors[Math.floor(Math.random() * colors.length)];
  };

  // Get a random topic
  const getRandomTopic = () => {
    return TOPICS[Math.floor(Math.random() * TOPICS.length)];
  };

  // Generate video description from service
  const generateVideoDescription = async (): Promise<VideoItem> => {
    try {
      const response = await fetch(`${API_URL}/generate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
        },
        mode: 'cors',
        credentials: 'include',
        body: JSON.stringify({ topic: getRandomTopic() }),
      });

      if (!response.ok) {
        throw new Error(`Failed to generate video description: ${response.status} ${response.statusText}`);
      }

      const data: GenerateResponse = await response.json();
      const content = JSON.parse(data.result);

      return {
        id: Date.now(),
        color: getRandomColor(),
        description: content.videoDescription,
        topText: content.topText,
        bottomText: content.bottomText,
      };
    } catch (error) {
      console.error('Error generating video description:', error);
      // Fallback to a basic video item if the service fails
      return {
        id: Date.now(),
        color: getRandomColor(),
        description: 'Failed to load description',
        topText: 'Error',
        bottomText: 'Please try again',
      };
    }
  };

  // Generate initial videos
  const generateInitialVideos = async (count: number) => {
    setLoading(true);
    try {
      const newVideos = await Promise.all(
        Array.from({ length: count }, () => generateVideoDescription())
      );
      setVideos(newVideos);
    } catch (error) {
      console.error('Error generating initial videos:', error);
    } finally {
      setLoading(false);
    }
  };

  // Load initial videos
  useEffect(() => {
    generateInitialVideos(5);
  }, []);

  // Handle scroll to load more videos
  const handleScroll = async (e: React.UIEvent<HTMLDivElement>) => {
    const element = e.currentTarget;
    if (
      element.scrollHeight - element.scrollTop <= element.clientHeight * 1.5 &&
      !loading
    ) {
      setLoading(true);
      try {
        const newVideos = await Promise.all(
          Array.from({ length: 5 }, () => generateVideoDescription())
        );
        setVideos(prev => [...prev, ...newVideos]);
      } catch (error) {
        console.error('Error loading more videos:', error);
      } finally {
        setLoading(false);
      }
    }
  };

  // Handle wheel event for snappy scrolling
  const handleWheel = (e: React.WheelEvent<HTMLDivElement>) => {
    e.preventDefault();
    const container = e.currentTarget;
    const scrollAmount = container.clientHeight;
    const direction = e.deltaY > 0 ? 1 : -1;
    
    container.scrollBy({
      top: scrollAmount * direction,
      behavior: 'smooth'
    });
  };

  return (
    <div
      onScroll={handleScroll}
      onWheel={handleWheel}
      style={{
        height: '100vh',
        overflowY: 'auto',
        backgroundColor: '#000',
        scrollSnapType: 'y mandatory',
      }}
    >
      {videos.map((video) => (
        <div
          key={video.id}
          style={{
            height: '100vh',
            backgroundColor: '#000',
            scrollSnapAlign: 'start',
            scrollSnapStop: 'always',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontSize: '24px',
            color: '#fff',
            position: 'relative',
          }}
        >
          <div
            style={{
              width: '60vh',
              height: '60vh',
              backgroundColor: video.color,
              borderRadius: '8px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              position: 'relative',
              overflow: 'hidden',
            }}
          >
            <div
              style={{
                position: 'absolute',
                top: '20px',
                left: '20px',
                right: '20px',
                textAlign: 'center',
                backgroundColor: 'rgba(0, 0, 0, 0.5)',
                padding: '8px 12px',
                borderRadius: '8px',
                fontSize: '18px',
              }}
            >
              {video.topText}
            </div>
            <div
              style={{
                position: 'absolute',
                bottom: '60px',
                left: '20px',
                right: '20px',
                textAlign: 'center',
                backgroundColor: 'rgba(0, 0, 0, 0.5)',
                padding: '8px 12px',
                borderRadius: '8px',
                fontSize: '18px',
              }}
            >
              {video.bottomText}
            </div>
            <div
              style={{
                position: 'absolute',
                bottom: '20px',
                left: '20px',
                right: '20px',
                textAlign: 'center',
                backgroundColor: 'rgba(0, 0, 0, 0.5)',
                padding: '8px 12px',
                borderRadius: '8px',
                fontSize: '14px',
              }}
            >
              {video.description}
            </div>
          </div>
        </div>
      ))}
      {loading && (
        <div
          style={{
            height: '100px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: '#fff',
          }}
        >
          Loading more videos...
        </div>
      )}
    </div>
  );
};

export default VideoFeed; 