import re
import os
import json
import openai
from termcolor import colored
from dotenv import load_dotenv
from typing import List

# Load environment variables
load_dotenv("./.env")

# Set environment variables
AZURE_OPENAI_API_KEY = os.getenv('AZURE_OPENAI_API_KEY')
AZURE_OPENAI_ENDPOINT = os.getenv('AZURE_OPENAI_ENDPOINT')
DEPLOYMENT_NAME_GPT35 = os.getenv('DEPLOYMENT_NAME_GPT35')

# Configure OpenAI to use Azure
openai.api_type = "azure"
openai.api_base = AZURE_OPENAI_ENDPOINT
openai.api_version = "2023-05-15"
openai.api_key = AZURE_OPENAI_API_KEY



def generate_response(prompt: str, ai_model: str) -> str:
    """
    Generate a response using the specified AI model.

    Args:
        prompt (str): The prompt to send to the AI model.
        ai_model (str): The AI model to use for generation.

    Returns:
        str: The response from the AI model.
    """

    if ai_model in ["gpt3.5-turbo"]:
        print(colored("inside **************gpt3.5-turbo", "green"))
        # Use Azure OpenAI endpoint
        deployment_name = DEPLOYMENT_NAME_GPT35 
        
        response = openai.ChatCompletion.create(
            engine=deployment_name,
            messages=[{"role": "user", "content": prompt}],
        )
        response = response.choices[0].message['content']


    else:
        raise ValueError("Invalid AI model selected.")

    return response





def get_search_terms(amount: int, script: str, ai_model: str) -> List[dict]:
    """
    Generate a JSON-Array of search terms for stock videos,
    depending on the subject of a video.

    Args:
        video_subject (str): The subject of the video.
        amount (int): The amount of search terms to generate.
        script (str): The script of the video.
        ai_model (str): The AI model to use for generation.

    Returns:
        List[dict]: The search terms for the video subject.
    """

    prompt = f"""
    Analyze the script and generate up to {amount} words that are present inside the script mentioned below and are most related to objects, emotions, moments, or catchy words.
    Do not include names.
    These words must be present inside the script and must be only one word.
    If the words are in not in English, translate them into English and provide both the original and translated words.
    These words are to be returned as a JSON array of objects with fields "searchWord" and "translatedWord".
    If the word is already in English, both "searchWord" and "translatedWord" should be the same.
    Do not mention the prompt or details about the script itself.
    Here are the requirements:
    - YOU MUST ONLY RETURN THE JSON-ARRAY OF OBJECTS.
    - DO NOT RETURN ANYTHING ELSE.
    - DO NOT RETURN THE SCRIPT.
    - Each object in the array must have fields "searchWord" and "translatedWord".

    Script:
    {script}
    """
    print(colored("inside gpt ", "green"))
   # Generate search terms
    response = generate_response(prompt, ai_model)
    print(colored(f"Final Search Terms: {response}", "green"))
    response = response.replace('json','').strip().strip('`') # removes json from response
    print(colored(f"Final script paragraph in formatted: {response}", "green"))

    # Parse response into a list of search terms
    search_terms = []
    
    try:
        search_terms = json.loads(response)
        if not isinstance(search_terms, list) or not all(isinstance(term, dict) for term in search_terms):
            raise ValueError("Response is not a list of objects.")

    except (json.JSONDecodeError, ValueError):
        # Get everything between the first and last square brackets
        response = response[response.find("[") + 1:response.rfind("]")]

        print(colored("[*] GPT returned an unformatted response. Attempting to clean...", "yellow"))

        # Attempt to extract list-like string and convert to list
        match = re.search(r'\["(?:[^"\\]|\\.)*"(?:,\s*"[^"\\]*")*\]', response)
        print(match.group())
        if match:
            try:
                search_terms = json.loads(match.group())
            except json.JSONDecodeError:
                print(colored("[-] Could not parse response.", "red"))
                return []

    # Let user know
    print(colored(f"\nGenerated {len(search_terms)} search terms: {', '.join([term['searchWord'] for term in search_terms])}", "cyan"))

    # Return search terms
    return search_terms
