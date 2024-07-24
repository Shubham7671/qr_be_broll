import json
import requests

def download_deepgram_json(deepgram_url, output_dir):
    try:
        # Make an HTTP GET request to the Deepgram URL
        response = requests.get(deepgram_url)
        
        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            # Parse the JSON response content
            deepgram_data = response.json()
            
            # Construct the output file path
            output_file=f"{output_dir}/deepgramScript.json"
            
            # Save the JSON data to a file
            with open(output_file, "w") as f:
                json.dump(deepgram_data, f, indent=4)
                
            print(f"Deepgram JSON file downloaded successfully: {output_file}")
            return output_file
        else:
            print(f"Failed to download Deepgram JSON file. Status code: {response.status_code}")
            return None
        
    except Exception as e:
        print(f"An error occurred while downloading Deepgram JSON file: {e}")
        return None
    

def get_json_data_from_file(file_path):
    try:
        with open(file_path, 'r') as file:
            json_data = json.load(file)
        return json_data
    except Exception as e:
        print(f"Error: Failed to read JSON data from file: {e}")
        return None


def download_video(url,output_dir):
    # Send a GET request to the video URL
    response = requests.get(url, stream=True)

    # Check if the request was successful
    if response.status_code == 200:
        # Create a temporary directory
       
            # Create a file in the temporary directory
            output_file=f"{output_dir}/input_video.mp4"
            # Open the file in write mode
            with open(output_file, "wb") as f:
                # Write the content of the response to the file
                for chunk in response.iter_content(chunk_size=1024):
                    if chunk:
                        f.write(chunk)
        
            print(f"Video downloaded successfully: {output_file}")
            return output_file
    else:
        print(f"Failed to download video. Status code: {response.status_code}")
        return None
