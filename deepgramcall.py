import requests

def get_transcript_from_deepgram(deepgram_api_key, audio_url):
    """
    Retrieves the transcript from Deepgram for a given audio URL.

    Args:
        deepgram_api_key (str): The Deepgram API key.
        audio_url (str): The URL of the audio file to transcribe.

    Returns:
        dict: The transcript response from Deepgram.
    """
    try:
        url = "https://api.deepgram.com/v1/listen"
        headers = {
            "Authorization": f"Token {deepgram_api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "url": audio_url
        }
        params = {
            "smart_format": "true",
            "detect_language": "true",
            "model": "nova-2"
        }

        response = requests.post(url, headers=headers, json=data, params=params)

        if response.status_code == 200:
            transcript = response.json()
            return transcript['results']
        else:
            raise Exception(f"Error: {response.status_code} - {response.text}")

    except Exception as e:
        print(f"Error getting transcript from Deepgram: {e}")
        return None