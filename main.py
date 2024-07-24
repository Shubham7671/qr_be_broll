import functions_framework
import os
from utils import *
from dotenv import load_dotenv
load_dotenv("./.env")
# Load environment variables
# Check if all required environment variables are set
# This must happen before importing video which uses API keys without checking
from db import *
from gpt import *
from video import *
from search import *
from deepgramcall import *
from flask_cors import CORS
from termcolor import colored
from flask import Flask, request, jsonify
from moviepy.config import change_settings
from s3upload import *
from download import *


# Set environment variables
deepgram_api_key = os.getenv('DEEPGRAM_API_KEY')
change_settings({"IMAGEMAGICK_BINARY": os.getenv("IMAGEMAGICK_BINARY")})

# Initialize Flask
# app = Flask(__name__)
# CORS(app)

# Constants
# HOST = "0.0.0.0"
# PORT = 8080
AMOUNT_OF_STOCK_VIDEOS = 5
# GENERATING = False


# Generation Endpoint
# @app.route("/api/generate", methods=["POST"])
@functions_framework.http
def generate(request):
    try:
        # Set global variable

        # Clean
        # clean_dir("../temp/")
        # clean_dir("../subtitles/")


        required_vars = ["DEEPGRAM_API_KEY", "PEXELS_API_KEY"]
        missing_vars = [var for var in required_vars if os.getenv(var) is None]

        if missing_vars:
            print(f"Missing environment variables: {', '.join(missing_vars)}")
        else:
            print("All required environment variables are set.")

        # Parse JSON
        data = request.get_json()
        ai_model = "gpt3.5-turbo"  # Get the AI model selected by the user


        # Print little information about the video which is to be generated
        print(colored("[Video to be generated]", "blue"))

        ## trim details && project deatils
        trim_id = data.get("trimId", "669f77d8166ac96fb81f2c30")

        project=get_project_by_trim_id(trim_id)
        trim=get_trim_by_trim_id(trim_id)
 
        if not project:
            print(colored(f"Invalid Trim details: {project}","red"))
            return jsonify(
                {
                    "status": "error",
                    "message": "Could not retrieve the project or trim details.",
                    "data": [],
                }
            )
        
        user_id = project['userid']
        project_id = project['_id']
        # deepgramUrl = trim.get('trimTranscriptURL')
        trimUrl = trim.get('sieveVideoUrl', '')

        # user_id = "65ae09eb6e9a4f2c830fd0bf"
        # project_id = "669014aaf90b21274091be5a"
        # # deepgramUrl = trim.get('trimTranscriptURL')
        # trimUrl ="https://qr-be-file-upload-us-east-1.s3.us-east-1.amazonaws.com/65ae09eb6e9a4f2c830fd0bf/669014aaf90b21274091be5a/669015bf5ce410b81da690a6_autocrop.mp4"



        print(colored(f"Trim details userId: {user_id} project_id:{project_id}  trimUrl:{trimUrl} trimId:{trim_id} ", "blue"))


        # Get Deepgram transcript
        try:
            transcript_data = get_transcript_from_deepgram(deepgram_api_key, trimUrl)
            print(colored(f"Deepgram transcript data: {transcript_data}", "blue"))
        except Exception as e:
            print(colored(f"Error getting transcript from Deepgram: {e}", "red"))
            return jsonify({
                "status": "error",
                "message": "Could not retrieve the transcript from Deepgram.",
                "data": [],
            })


        # Download Deepgram JSON file
        output_dir = "./temp"  # Specify the output directory where the file will be saved
        os.makedirs(output_dir, exist_ok=True) 
        # deepgram_json_file = download_deepgram_json(deepgramUrl, output_dir)


        #download video 
        download_video(trimUrl,output_dir)


        if not transcript_data:
            print(colored(f"Invalid deepgram_json_file: {transcript_data}","red"))
            return jsonify(
                {
                    "status": "error",
                    "message": "Could not download the deepgram_json_file",
                    "data": [],
                }
            )        

        # Specify the folder path and file name
        # file_path = "../temp/deepgramScript.json"

        # Read the JSON data from the file
        # json_data = get_json_data_from_file(file_path)

        # Check if JSON data was successfully read
        if transcript_data:
        # Call the extract_paragraph function with the JSON data
             trimTranscript=extract_paragraph(transcript_data)
             print(f"Transcript of trim => {trimTranscript}")
        else:
             print("No JSON data available.")


        if not trimTranscript:
            return jsonify(
                {
                    "status": "error",
                    "message": f"Error in the extract_paragraph function with the JSON data {trimTranscript}",
                    "data": [],
                }
            )
        


        # Generate search terms
        search_terms = get_search_terms( AMOUNT_OF_STOCK_VIDEOS, trimTranscript, ai_model)

        # Search for a video of the given search term
        video_urls = []

        # Defines how many results it should query and search through
        it = 15

        # Defines the minimum duration of each clip
        min_dur = 3
        final_data=[]
        # Loop through all search terms,
        # and search for a video of the given search term
        for search_term in search_terms:
            found_urls = search_for_stock_videos(
                search_term["translatedWord"], os.getenv("PEXELS_API_KEY"), it, min_dur
            )
            


                # Check for duplicates
            if len(found_urls) > 0:
               for url in found_urls:
                  if url not in video_urls:
                     video_urls.append(url)
                     final_data.append({
                    "word": search_term["searchWord"],
                    "tempPath": "",
                    "videoUrl": url,
                  })
                  break
                

        # Check if video_urls is empty
        if not video_urls:
            print(colored("[-] No videos found to download.", "red"))
            return jsonify(
                {
                    "status": "error",
                    "message": "No videos found to download.",
                    "data": [],
                }
            )
            
        # Define video_paths
        video_paths = []

        # Let user know
        print(colored(f"[+] Downloading {len(video_urls)} videos...", "blue"))

        # Save the videos
        for entry in final_data:
            videoUrl=entry["videoUrl"]
            word=entry["word"]

            try:
                saved_video_path = save_video(videoUrl)
                entry["tempPath"] = saved_video_path
                video_paths.append(saved_video_path)
            except Exception:
                print(colored(f"[-] Could not download video: {video_url}", "red"))

        # Let user know
        print(colored("[+] Videos downloaded!", "green"))


        print(f"****************final data {final_data}")
        final_data=add_start_time(transcript_data,final_data)
        print(colored(f"[+] final data => {final_data} ", "cyan"))



        output_file_path=f"{output_dir}/output_video.mp4"
        input_file_path=f"{output_dir}/input_video.mp4"
        

        # Put everything together
        try:
            # print(colored(f"[+] Video generated: {final_video_path}!", "green"))
            final_video_path = overlay_clips_on_main_video(input_file_path,final_data,output_file_path)
        except Exception as e:
            print(colored(f"[-] Error generating final video: {e}", "red"))
            final_video_path = None

        # Let user know
        print(colored(f"[+] Video generated: {final_video_path}!", "green"))


        #  upload to s3

        video_url = upload_video_to_s3(output_file_path, user_id, project_id, trim_id)
        print(f"Uploaded video URL: {video_url}")

        if video_url:
        # Update the brollUrl in the database
          update_result = update_broll_url(trim_id, video_url)
          print(update_result)


        # Return JSON
        return jsonify(
            {
                "status": "success",
                "message": "Video generated Successfully ",
                "data": video_url,
            }
        )
    except Exception as err:
        print(colored(f"[-] Error: {str(err)}", "red"))
        return jsonify(
            {
                "status": "error",
                "message": f"Could not retrieve stock videos: {str(err)}",
                "data": [],
            }
        )




# if __name__ == "__main__":

#     # Run Flask App
#     app.run(debug=True, host=HOST, port=PORT)
