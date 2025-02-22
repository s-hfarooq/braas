from ollama import chat
from ollama import ChatResponse

prompt = """
You are tasked with describing what is happening in a video based on a given keyword. When given a keyword, you should describe a typical video that would be found when searching for that keyword on social media platforms.

Here is the keyword:
<video_topic>
{{VIDEO_TOPIC}}
</video_topic>

To create the video description:
1. Consider what type of video content is commonly associated with this keyword
2. Describe the main visual elements and actions that would typically appear in such a video
3. Mention any key characters or subjects that are commonly featured
4. Describe the sequence of events in chronological order
5. Include relevant details about the setting or environment
6. Keep the description between 2-4 sentences long
7. Generate appropriate meme text that would appear at the top and bottom of the video

Your output should be in the following JSON format:

<output_format>
{
    "videoDescription": "Your scene-by-scene description goes here",
    "topText": "Text that would appear at the top of the video",
    "bottomText": "Text that would appear at the bottom of the video"
}
</output_format>

For example, if given the keyword 'dance challenge', describe a typical dance challenge video. If given a meme keyword, describe a typical video of that meme format.

Focus on describing what would be actually visible and happening in the video, as if you were explaining the scene to someone who cannot see it. The top and bottom text should follow common meme formats and humor styles associated with the keyword. Write your final output in the JSON format specified above, ensuring it is properly formatted. Omit tags in your response. Output ONLY the JSON.
"""

response: ChatResponse = chat(model='llama3.2:1b', messages=[
  {
    'role': 'system',
    'content': prompt,
  },
  {
    'role': 'user',
    'content': 'some brainrot short form content',
  },
])

# or access fields directly from the response object
print(response.message.content)