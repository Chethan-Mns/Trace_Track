import requests
import json

# Define the SSE endpoint URL
url = 'http://127.0.0.1:8000/users/locationStream/1/'


# Function to handle incoming SSE events
def handle_event(event):
    # Process the event data here
    print("Received event:", event)


# Make a GET request to the SSE endpoint
response = requests.get(url, stream=True)

# Check if the connection was successful
if response.status_code == 200:
    # Iterate over the response content line by line
    for line in response.iter_lines(decode_unicode=True):
        if line:
            # Parse the event data from the line

            # Handle the event
            handle_event(line)
else:
    print("Failed to connect to SSE endpoint:", response.status_code)
