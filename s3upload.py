import boto3
import os
from botocore.exceptions import NoCredentialsError, PartialCredentialsError

# Load AWS credentials from environment variables or a configuration file
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
AWS_BUCKET_NAME = os.getenv('AWS_BUCKET_NAME')
AWS_REGION = os.getenv('AWS_REGION')

# Initialize S3 client
s3 = boto3.client('s3', 
                  aws_access_key_id=AWS_ACCESS_KEY_ID, 
                  aws_secret_access_key=AWS_SECRET_ACCESS_KEY, 
                  region_name=AWS_REGION)

def upload_video_to_s3(file_path, user_id, project_id, trim_id):
    """
    Uploads a video file to an S3 bucket.

    Args:
        file_path (str): The local path to the video file.
        user_id (str): The user ID.
        project_id (str): The project ID.
        trim_id (str): The trim ID.

    Returns:
        str: The URL of the uploaded video.
    """
    try:
        if not os.path.exists(file_path):
            print("Video file not found at the specified path.")
            return None

        # Construct the S3 key
        s3_key = f"{user_id}/{project_id}/{trim_id}_broll.mp4"

        # Upload the file
        s3.upload_file(file_path, AWS_BUCKET_NAME, s3_key, ExtraArgs={'ContentType': 'video/mp4'})
        
        # Construct the URL of the uploaded video
        s3_url = f"https://{AWS_BUCKET_NAME}.s3.{AWS_REGION}.amazonaws.com/{s3_key}"
        print("Video uploaded successfully:", s3_url)
        return s3_url

    except FileNotFoundError:
        print("The specified file was not found.")
        return None
    except NoCredentialsError:
        print("Credentials not available.")
        return None
    except PartialCredentialsError:
        print("Incomplete credentials provided.")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None


