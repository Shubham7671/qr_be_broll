from pymongo import MongoClient, errors
from bson import ObjectId
import os

MONGO_URI = os.getenv('MONGO_URI')
client = MongoClient(MONGO_URI)
db = client['quickreel']
project_collection = db['projects']

def get_project_by_trim_id(trim_id):
    try:
        # Convert trim_id to ObjectId if it is a valid ObjectId string
        trim_id = ObjectId(trim_id)

        # Find the project containing the trim with the specified trimId
        project = project_collection.find_one({"trims._id": trim_id})

        if project:
            return project
        else:
            return "Project with the specified trimId not found."

    except errors.InvalidId:
        return "Invalid trimId format."
    except Exception as e:
        return f"An error occurred: {e}"

def get_trim_by_trim_id(trim_id):
    try:
        # Convert trim_id to ObjectId if it is a valid ObjectId string
        trim_id = ObjectId(trim_id)

        # Find the project containing the trim with the specified trimId
        project = project_collection.find_one({"trims._id": trim_id})

        if project:
            # Iterate through the trims array to find the specific trim
            for trim in project['trims']:
                if trim['_id'] == trim_id:
                    return trim
            return "Trim with the specified trimId not found in the project."
        else:
            return "Project with the specified trimId not found."

    except errors.InvalidId:
        return "Invalid trimId format."
    except Exception as e:
        return f"An error occurred: {e}"

def update_broll_url(trim_id, broll_url):
    try:
        # Convert trim_id to ObjectId if it is a valid ObjectId string
        trim_id = ObjectId(trim_id)

        # Find the project containing the trim with the specified trimId
        project = project_collection.find_one({"trims._id": trim_id})

        if project:
            # Update the specific trim's brollUrl in the project document
            result = project_collection.update_one(
                {"_id": project['_id'], "trims._id": trim_id},
                {"$set": {"trims.$.brollUrl": broll_url}}
            )

            if result.matched_count > 0:
                return "B-roll URL successfully updated in the database."
            else:
                return "No matching document found to update."
        else:
            return "Project with the specified trimId not found."

    except errors.InvalidId:
        return "Invalid trimId format."
    except Exception as e:
        return f"An error occurred: {e}"
