import requests
from typing import List
from termcolor import colored

def search_for_stock_videos(query: str, api_key: str, it: int, min_dur: int) -> List[str]:
    """
    Searches for stock videos based on a query.

    Args:
        query (str): The query to search for.
        api_key (str): The API key to use.

    Returns:
        List[str]: A list of stock videos.
    """
    print(f"search_for_stock_videos word => {query}")
    # Build headers
    headers = {
        "Authorization": api_key
    }

    # Build URL
    qurl = f"https://api.pexels.com/videos/search?query={query}&per_page={it}&orientation=portrait"

    video_url = []
    
    try:
        # Send the request
        r = requests.get(qurl, headers=headers)
        r.raise_for_status()  # Raise an exception for HTTP errors
        
        # Parse the response
        response = r.json()
    
        # Parse each video
        raw_urls = []
        video_res = 0
        try:
            for i in range(it):
                # Check if video has desired minimum duration
                if response["videos"][i]["duration"] < min_dur:
                    continue
                raw_urls = response["videos"][i]["video_files"]
                temp_video_url = ""
                
                # Loop through each URL to determine the best quality
                for video in raw_urls:
                    # Check if video has a valid download link
                    if ".com/video-files" in video["link"]:
                        # Only save the URL with the largest resolution
                        if video["height"] > video_res:
                            temp_video_url = video["link"]
                            video_res = video["height"]
                
                # Add the URL to the return list if it's not empty
                if temp_video_url != "":
                    video_url.append(temp_video_url)
                    
        except Exception as e:
            print(colored("[-] No Videos found or an error occurred while processing the response.", "red"))
            print(colored(e, "red"))

    except requests.exceptions.HTTPError as http_err:
        print(colored(f"[-] HTTP error occurred: {http_err}", "red"))
    except requests.exceptions.RequestException as req_err:
        print(colored(f"[-] Request error occurred: {req_err}", "red"))
    except Exception as e:
        print(colored("[-] An unexpected error occurred.", "red"))
        print(colored(e, "red"))

    # Let user know
    print(colored(f"\t=> \"{query}\" found {len(video_url)} Videos", "cyan"))
    
    # Return the video url
    return video_url
