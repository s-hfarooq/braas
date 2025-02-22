import React, { useEffect, useState } from 'react';

interface VideoItem {
  id: number;
  color: string;
  description: string;
  topText: string;
  bottomText: string;
  videoContent?: string; // base64 video content
}

interface PromptData {
  topic: string;
  output: string;
  top_text: string;
  bottom_text: string;
  metadata: any;
}

interface VideoData {
  prompt: string;
  description: string;
  content: string; // base64 encoded video
  metadata: any;
}

interface BasicDataItem {
  value: {
    description?: string;
    prompt?: string;
    content?: string;
    metadata?: any;
  };
}

interface BasicApiResponse {
  data: BasicDataItem[];
}

// Basic.tech API interfaces
interface BasicConfig {
  projectId: string;
  jwt: string;
  apiKey: string;
}

// Get environment variables from import.meta.env (Vite) or window._env_ (runtime)
const BASIC_CONFIG: BasicConfig = {
  projectId: (window as any)._env_?.BASIC_PROJECT_ID || import.meta.env.VITE_BASIC_PROJECT_ID || '',
  jwt: (window as any)._env_?.BASIC_JWT || import.meta.env.VITE_BASIC_JWT || '',
  apiKey: (window as any)._env_?.BASIC_API_KEY || import.meta.env.VITE_BASIC_API_KEY || ''
};

const BASE_URL = `https://api.basic.tech/account/${BASIC_CONFIG.projectId}/db`;

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
  const [loadingPrompts, setLoadingPrompts] = useState(false);
  const [generatingVideo, setGeneratingVideo] = useState(false);
  const [offset, setOffset] = useState(0);

  // Basic.tech API headers
  const headers = {
    'Authorization': `Bearer ${BASIC_CONFIG.jwt}`,
    'Content-Type': 'application/json',
    'Accept': 'application/json'
  };

  // Generate a random color
  const getRandomColor = () => {
    const colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEEAD', '#D4A5A5', '#9B59B6'];
    return colors[Math.floor(Math.random() * colors.length)];
  };

  // Get a random topic
  const getRandomTopic = () => {
    return TOPICS[Math.floor(Math.random() * TOPICS.length)];
  };

  // Get existing videos from Basic.tech
  const getExistingVideos = async (limit: number = 5): Promise<VideoItem[]> => {
    console.log(`[getExistingVideos] Fetching ${limit} videos with offset ${offset}`);
    try {
      const url = `${BASE_URL}/video`;
      const params = new URLSearchParams({ 
        limit: limit.toString(),
        offset: offset.toString()
      });
      console.log(`[getExistingVideos] Calling Basic.tech API: ${url}?${params}`);
      console.log(`[getExistingVideos] Headers:`, headers);
      
      const response = await fetch(`${url}?${params}`, {
        method: 'GET',
        headers
      });

      console.log(`[getExistingVideos] Response status:`, response.status);
      const responseText = await response.text();
      console.log(`[getExistingVideos] Raw response text:`, responseText);

      if (!response.ok) {
        throw new Error(`Failed to get videos: ${response.status} ${response.statusText} - ${responseText}`);
      }

      let data;
      try {
        data = JSON.parse(responseText);
        console.log(`[getExistingVideos] Parsed response data:`, data);
      } catch (e) {
        console.error(`[getExistingVideos] Failed to parse response as JSON:`, e);
        return [];
      }

      // Check what kind of response we got
      console.log(`[getExistingVideos] Response type:`, typeof data);
      console.log(`[getExistingVideos] Is array?`, Array.isArray(data));
      console.log(`[getExistingVideos] Has data property?`, 'data' in data);
      
      let videos: VideoItem[] = [];

      if (!Array.isArray(data)) {
        console.log(`[getExistingVideos] Response is not an array, trying to access data property`);
        const apiResponse = data as BasicApiResponse;
        if (apiResponse.data && Array.isArray(apiResponse.data)) {
          console.log(`[getExistingVideos] Found array in data property with ${apiResponse.data.length} items`);
          videos = apiResponse.data.map((item: BasicDataItem) => {
            console.log(`[getExistingVideos] Processing item:`, item);
            const videoItem = {
              id: Date.now() + Math.random(),
              color: getRandomColor(),
              description: item.value?.description || 'No description available',
              topText: item.value?.prompt || 'Watch this video',
              bottomText: item.value?.description || 'No description available',
              videoContent: item.value?.content
            };
            console.log(`[getExistingVideos] Created video item:`, {
              ...videoItem,
              videoContent: videoItem.videoContent ? `${videoItem.videoContent.substring(0, 50)}...` : 'none'
            });
            return videoItem;
          });
        }
      } else {
        console.log(`[getExistingVideos] Response is an array with ${data.length} items`);
        videos = data.map((item: { data: { value: VideoData } }) => {
          console.log(`[getExistingVideos] Processing array item:`, item);
          const videoItem = {
            id: Date.now() + Math.random(),
            color: getRandomColor(),
            description: item.data?.value?.description || 'No description available',
            topText: item.data?.value?.prompt || 'Watch this video',
            bottomText: item.data?.value?.description || 'No description available',
            videoContent: item.data?.value?.content
          };
          console.log(`[getExistingVideos] Created video item:`, {
            ...videoItem,
            videoContent: videoItem.videoContent ? `${videoItem.videoContent.substring(0, 50)}...` : 'none'
          });
          return videoItem;
        });
      }

      console.log(`[getExistingVideos] Returning ${videos.length} videos`);
      return videos;
    } catch (error) {
      console.error('[getExistingVideos] Error:', error);
      return [];
    }
  };

  // Generate and store prompt directly to Basic.tech
  const generateVideoDescription = async (): Promise<VideoItem> => {
    try {
      const topic = getRandomTopic();
      const promptData: PromptData = {
        topic,
        output: `A funny video about ${topic}`,
        top_text: `Watch this ${topic}`,
        bottom_text: "You won't believe what happens next!",
        metadata: { generated: true }
      };

      const response = await fetch(`${BASE_URL}/prompts`, {
        method: 'POST',
        headers,
        body: JSON.stringify({ value: promptData })
      });

      if (!response.ok) {
        throw new Error(`Failed to store prompt: ${response.status} ${response.statusText}`);
      }

      const data = await response.json();
      return {
        id: Date.now(),
        color: getRandomColor(),
        description: data.data.value.output,
        topText: data.data.value.top_text,
        bottomText: data.data.value.bottom_text,
      };
    } catch (error) {
      console.error('Error generating video description:', error);
      const fallbackTopic = getRandomTopic();
      return {
        id: Date.now(),
        color: getRandomColor(),
        description: `A funny video about ${fallbackTopic}`,
        topText: `Watch this ${fallbackTopic}`,
        bottomText: "You won't believe what happens next!",
      };
    }
  };

  // Generate initial content
  const generateInitialContent = async (count: number) => {
    console.log(`[generateInitialContent] Starting with count ${count}`);
    setLoadingPrompts(true);
    try {
      // First try to get existing videos
      console.log('[generateInitialContent] Attempting to fetch existing videos');
      const existingVideos = await getExistingVideos(count);
      console.log(`[generateInitialContent] Got ${existingVideos.length} existing videos:`, 
        existingVideos.map(v => ({
          ...v,
          videoContent: v.videoContent ? `${v.videoContent.substring(0, 50)}...` : 'none'
        }))
      );
      
      if (existingVideos.length > 0) {
        console.log('[generateInitialContent] Setting videos in state');
        setVideos(existingVideos);
      }

      // If we got fewer videos than requested, fall back to prompts
      if (existingVideos.length < count) {
        console.log('[generateInitialContent] Generating additional content');
        setGeneratingVideo(true);
        const numToGenerate = count - existingVideos.length;
        const newContent = await Promise.all(
          Array.from({ length: numToGenerate }, () => generateVideoDescription())
        );
        console.log(`[generateInitialContent] Generated ${newContent.length} new items`);
        setVideos(prev => [...prev, ...newContent]);
        setGeneratingVideo(false);
      }
    } catch (error) {
      console.error('[generateInitialContent] Error:', error);
    } finally {
      setLoadingPrompts(false);
    }
  };

  // Load initial content
  useEffect(() => {
    generateInitialContent(5);
  }, []);

  // Handle scroll to load more videos
  const handleScroll = async (e: React.UIEvent<HTMLDivElement>) => {
    const element = e.currentTarget;
    const scrolledToBottom = element.scrollHeight - element.scrollTop <= element.clientHeight * 1.2;
    
    if (scrolledToBottom && !loadingPrompts && !generatingVideo) {
      console.log('[handleScroll] Reached bottom, loading more videos');
      setLoadingPrompts(true);
      try {
        // Try to get more existing videos first
        const nextOffset = offset + 5;
        console.log(`[handleScroll] Fetching more videos with offset ${nextOffset}`);
        const existingVideos = await getExistingVideos(5);
        console.log(`[handleScroll] Got ${existingVideos.length} more videos`);
        
        if (existingVideos.length > 0) {
          setVideos(prev => {
            // Filter out any duplicates based on content
            const newVideos = existingVideos.filter(newVideo => 
              !prev.some(existingVideo => 
                existingVideo.description === newVideo.description &&
                existingVideo.topText === newVideo.topText &&
                existingVideo.bottomText === newVideo.bottomText
              )
            );
            console.log(`[handleScroll] Adding ${newVideos.length} new unique videos`);
            return [...prev, ...newVideos];
          });
          setOffset(nextOffset);
        } else {
          // Generate just one new video at a time
          console.log('[handleScroll] No more videos, generating new video');
          setGeneratingVideo(true);
          const newVideo = await generateVideoDescription();
          console.log('[handleScroll] Generated new video');
          setVideos(prev => [...prev, newVideo]);
          setGeneratingVideo(false);
        }
      } catch (error) {
        console.error('[handleScroll] Error:', error);
      } finally {
        setLoadingPrompts(false);
      }
    }
  };

  // Handle wheel scrolling with cleanup
  const wheelHandler = (e: WheelEvent) => {
    e.preventDefault();
    const container = e.currentTarget as HTMLDivElement;
    const scrollAmount = container.clientHeight;
    const direction = e.deltaY > 0 ? 1 : -1;
    container.scrollBy({
      top: scrollAmount * direction,
      behavior: 'smooth'
    });
  };

  // Setup wheel event listener with cleanup
  const setupWheelHandler = (el: HTMLDivElement | null) => {
    if (el) {
      const handler = wheelHandler.bind(null);
      el.addEventListener('wheel', handler, { passive: false });
      return () => {
        el.removeEventListener('wheel', handler);
      };
    }
  };

  // Render video or fallback
  const renderContent = (video: VideoItem) => {
    console.log('[renderContent] Rendering video item:', video);
    if (video.videoContent) {
      console.log('[renderContent] Video content found, length:', video.videoContent.length);
      try {
        // Validate base64
        const isValidBase64 = /^[A-Za-z0-9+/=]+$/.test(video.videoContent.trim());
        console.log('[renderContent] Is valid base64:', isValidBase64);
        
        if (!isValidBase64) {
          console.warn('[renderContent] Invalid base64 content, falling back to color');
          return (
            <div
              style={{
                width: '100%',
                height: '100%',
                backgroundColor: video.color,
                position: 'absolute',
                top: 0,
                left: 0,
              }}
            />
          );
        }

        return (
          <video
            autoPlay
            loop
            muted
            playsInline
            controls // Added controls for debugging
            style={{
              width: '100%',
              height: '100%',
              objectFit: 'cover',
              position: 'absolute',
              top: 0,
              left: 0,
            }}
            onError={(e) => {
              console.error('[renderContent] Video error:', e);
            }}
            onLoadedData={() => {
              console.log('[renderContent] Video loaded successfully');
            }}
          >
            <source 
              src={`data:video/mp4;base64,${video.videoContent}`} 
              type="video/mp4"
              onError={(e) => {
                console.error('[renderContent] Source error:', e);
              }}
            />
            Your browser does not support the video tag.
          </video>
        );
      } catch (error) {
        console.error('[renderContent] Error rendering video:', error);
      }
    }

    console.log('[renderContent] No video content, using color fallback');
    return (
      <div
        style={{
          width: '100%',
          height: '100%',
          backgroundColor: video.color,
          position: 'absolute',
          top: 0,
          left: 0,
        }}
      />
    );
  };

  return (
    <div
      onScroll={handleScroll}
      style={{
        height: '100vh',
        overflowY: 'auto',
        backgroundColor: '#000',
        scrollSnapType: 'y mandatory',
        position: 'relative',
      }}
      ref={el => {
        if (el) {
          const cleanup = setupWheelHandler(el);
          return () => cleanup?.();
        }
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
              borderRadius: '8px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              position: 'relative',
              overflow: 'hidden',
            }}
          >
            {renderContent(video)}
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
                zIndex: 1,
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
                zIndex: 1,
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
                zIndex: 1,
              }}
            >
              {video.description}
            </div>
          </div>
        </div>
      ))}
      {(loadingPrompts || generatingVideo) && (
        <div
          style={{
            position: 'fixed',
            bottom: '20px',
            left: '50%',
            transform: 'translateX(-50%)',
            backgroundColor: 'rgba(0, 0, 0, 0.8)',
            color: '#fff',
            padding: '12px 24px',
            borderRadius: '8px',
            fontSize: '16px',
            zIndex: 1000,
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
          }}
        >
          <div className="loading-spinner" style={{
            width: '20px',
            height: '20px',
            border: '3px solid #fff',
            borderTop: '3px solid transparent',
            borderRadius: '50%',
            animation: 'spin 1s linear infinite',
          }} />
          {generatingVideo ? 'Loading video...' : 'Loading more content...'}
        </div>
      )}
      <style>
        {`
          @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
          }
        `}
      </style>
    </div>
  );
};

export default VideoFeed; 