from helper import prune_serpapi_response, format_user_profiles
from agents import function_tool
from models import UserProfile
import requests
import os

@function_tool
def web_search(query: str) -> dict[str, any]:
    """
    Performs a real-time web search to find information on the internet.
    This tool is ideal for answering factual questions, getting current information,
    or looking up details about specific entities, events, or concepts.

    Args:
        query (str): The search query to be performed. Be specific and concise.
                     Examples: "Give me details of Abishai", "who won the last world cup",

    Returns:
        dict: A dictionary containing search results.
    """
    try:
        serp_api_key = os.getenv('SERP_API_KEY')
        if not serp_api_key:
            raise ValueError("SERP_API_KEY environment variable not set for web_search tool.")

        url = f'https://serpapi.com/search?q={query}&api_key={serp_api_key}'
        response = requests.get(url)
        data = response.json()
        return prune_serpapi_response(data)
    except requests.exceptions.RequestException as e:
        print(f"Web search failed: {e}")
        return {"error": f"Could not perform web search: {e}"}
    except Exception as e:
        print(f"An error occurred during web search: {e}")
        return {"error": "An error occurred during web search."}

@function_tool
def send_whatsapp_sms(number: str, users: list[UserProfile]) -> str:
    """
    Sends a WhatsApp message to the specified number using a list of user profiles.
    The function formats the message itself via internal utility, no user message input needed.

    Args:
        number (str): Recipient phone number, including country code (e.g., "+92...").
        users (list[dict]): List of user profiles (name, age, location, interests).

    Returns:
        str: Confirmation or error from WhatsApp sending.
    """
    # internally format users to message text
    message = format_user_profiles(users)

    try:
        utlramsg_token = os.getenv('ULTRA_MSG_TOKEN')
        instance_id = os.getenv('ULTRA_MSG_INSTANCE_ID')

        url = f"https://api.ultramsg.com/{instance_id}/messages/chat"
        payload = f"token={utlramsg_token}&to={number}&body={message}"

        payload = payload.encode('utf8').decode('iso-8859-1')
        headers = {'content-type': 'application/x-www-form-urlencoded'}

        response = requests.request("POST", url, data=payload, headers=headers)

        return response.text
    except Exception as e:
        print(f"An error occurred during WhatsApp message delivery: {e}")
        return f"An error occurred during WhatsApp message delivery: {e}"

@function_tool
def get_user_data(min_age: int) -> list[dict]:
    """
    Retrieves a list user profiles from an internal dataset.
    This tool filters users and returns only those who meet or exceed a specified minimum age.

    Args:
        min_age (int): The minimum age (inclusive) for filtering the user profiles.
                       Only users whose age is greater than or equal to this value will be returned.

    Returns:
        list[dict]: A list of dictionaries
    """
    users = [
        {"name": "Muneeb", "age": 22, "location": "Karachi", "interests": ["reading", "gaming"]},
        {"name": "Muhammad Ubaid Hussain", "age": 25, "location": "Lahore", "interests": ["coding", "music"]},
        {"name": "Azan", "age": 19, "location": "Islamabad", "interests": ["sports", "traveling"]},
    ]

    for user in users:
        if user["age"] < min_age:
            users.remove(user)

    return users