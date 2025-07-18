from helper import prune_serpapi_response
from agents import function_tool
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
        print("\n\n[ WEB SEARCH ] ===> ", data, " <===\n\n")
        return prune_serpapi_response(data)
    except requests.exceptions.RequestException as e:
        print(f"Web search failed: {e}")
        return {"error": f"Could not perform web search: {e}"}
    except Exception as e:
        print(f"An error occurred during web search: {e}")
        return {"error": "An error occurred during web search."}

@function_tool
def send_whatsapp_sms(number: str, message: str) -> str:
    """
    Sends a WhatsApp message to a specified phone number.
    This tool should be used when the user explicitly requests to send a message
    via WhatsApp. Always confirm the recipient's phone number.

    Args:
        number (str): The recipient's phone number, including the country code (e.g., "+92 317 2648144").
                      Must be a string of digits.
        message (str): The text message content to be sent (e.g details of the match)

    Returns:
        str: A confirmation message indicating success or failure of the message delivery,
             including any error details from the WhatsApp API.
    """

    utlramsg_token = os.getenv('ULTRA_MSG_TOKEN')
    instance_id = os.getenv('ULTRA_MSG_INSTANCE_ID')

    url = f"https://api.ultramsg.com/{instance_id}/messages/chat"
    payload = f"token={utlramsg_token}&to={number}&body={message}"

    payload = payload.encode('utf8').decode('iso-8859-1')
    headers = {'content-type': 'application/x-www-form-urlencoded'}

    response = requests.request("POST", url, data=payload, headers=headers)

    print(response.text)

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