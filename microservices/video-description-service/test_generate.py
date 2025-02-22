import requests
import json

def test_generate():
    url = "http://localhost:5000/generate"
    headers = {
        "Content-Type": "application/json"
    }
    
    # Test cases
    topics = [
        "cat playing piano",
        "skateboard fail",
        "cooking tutorial gone wrong"
    ]
    
    for topic in topics:
        print(f"\nTesting topic: {topic}")
        print("-" * 50)
        
        payload = {"topic": topic}
        response = requests.post(url, json=payload, headers=headers)
        
        print(f"Status Code: {response.status_code}")
        print("\nRaw Response:")
        print(response.text)
        
        if response.status_code == 200:
            try:
                result = json.loads(response.json()["result"])
                print("\nParsed Response:")
                print("\nVideo Description:")
                print(result["videoDescription"])
                print("\nTop Text:")
                print(result["topText"])
                print("\nBottom Text:")
                print(result["bottomText"])
            except Exception as e:
                print(f"\nError parsing response: {str(e)}")
        else:
            print("Error:", response.text)
        
        print("-" * 50)
        print("\nPress Enter to continue to next topic...")
        input()

if __name__ == "__main__":
    test_generate() 