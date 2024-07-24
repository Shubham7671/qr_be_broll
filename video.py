import uuid
import requests
from moviepy.editor import *
from dotenv import load_dotenv
from moviepy.editor import VideoFileClip
from moviepy.video.fx.crop import crop
load_dotenv("./.env")



def save_video(video_url: str, directory: str = "./temp") -> str:
    """
    Saves a video from a given URL and returns the path to the video.

    Args:
        video_url (str): The URL of the video to save.
        directory (str): The path of the temporary directory to save the video to

    Returns:
        str: The path to the saved video.
    """
    video_id = uuid.uuid4()
    video_path = f"{directory}/{video_id}.mp4"
    with open(video_path, "wb") as f:
        f.write(requests.get(video_url).content)

    return video_path



def overlay_clips_on_main_video(main_video_path, clips_info, output_path):
    """
    Overlays clips on the main video at specified start times for 3 seconds.

    Parameters:
    - main_video_path (str): Path to the main video file.
    - clips_info (list of dicts): List of dictionaries containing 'tempPath' and 'startTime' for each clip.
    - output_path (str): Path to save the final output video.
    """
    # Load the main video
    main_clip = VideoFileClip(main_video_path)

    # Create a list to hold the overlays
    overlays = []

    # Iterate through the clips to be overlaid
    for clip_info in clips_info:
        start_time = clip_info['startTime']
        overlay_clip = VideoFileClip(clip_info['tempPath']).subclip(0, 2)  # Use only the first 3 seconds of the clip

        # Resize the clip
        if round((overlay_clip.w / overlay_clip.h), 4) < 0.5625:
            overlay_clip = crop(overlay_clip, width=overlay_clip.w, height=round(overlay_clip.w / 0.5625), 
                                x_center=overlay_clip.w / 2, y_center=overlay_clip.h / 2)
        else:
            overlay_clip = crop(overlay_clip, width=round(0.5625 * overlay_clip.h), height=overlay_clip.h, 
                                x_center=overlay_clip.w / 2, y_center=overlay_clip.h / 2)
        overlay_clip = overlay_clip.resize((1080, 1920))

        # Set the start time of the overlay
        overlay_clip = overlay_clip.set_start(start_time).set_duration(3)

        # Set the position and size of the overlay if needed
        overlay_clip = overlay_clip.set_position(("center", "center"))

        # Add the overlay clip to the list
        overlays.append(overlay_clip)

    # Create the final composite video with the overlays
    final_video = CompositeVideoClip([main_clip] + overlays)

    # Write the result to a file
    final_video.write_videofile(output_path, codec='libx264')






