import React, { useEffect, useState } from 'react';

interface VideoItem {
  id: number;
  color: string;
}

const VideoFeed: React.FC = () => {
  const [videos, setVideos] = useState<VideoItem[]>([]);
  const [loading, setLoading] = useState(false);

  // Generate a random color
  const getRandomColor = () => {
    const colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEEAD', '#D4A5A5', '#9B59B6'];
    return colors[Math.floor(Math.random() * colors.length)];
  };

  // Generate initial videos
  const generateVideos = (count: number, startIndex: number = 0) => {
    return Array.from({ length: count }, (_, i) => ({
      id: startIndex + i,
      color: getRandomColor(),
    }));
  };

  // Load initial videos
  useEffect(() => {
    setVideos(generateVideos(5));
  }, []);

  // Handle scroll to load more videos
  const handleScroll = (e: React.UIEvent<HTMLDivElement>) => {
    const element = e.currentTarget;
    if (
      element.scrollHeight - element.scrollTop <= element.clientHeight * 1.5 &&
      !loading
    ) {
      setLoading(true);
      // Simulate loading delay
      setTimeout(() => {
        setVideos(prev => [...prev, ...generateVideos(5, prev.length)]);
        setLoading(false);
      }, 500);
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
            }}
          >
            <div
              style={{
                position: 'absolute',
                bottom: '20px',
                right: '20px',
                backgroundColor: 'rgba(0, 0, 0, 0.5)',
                padding: '8px 12px',
                borderRadius: '8px',
              }}
            >
              Video #{video.id + 1}
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