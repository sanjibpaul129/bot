import uuid
import json
import openai
import gradio
import os
from dotenv import load_dotenv
# API Key management
load_dotenv()
openai.api_key = os.getenv('OPENAI_API_KEY')

# Load context from JSON
with open("content.json", "r") as file:
    data = json.load(file)

# Extract relevant data and convert to context string
project_info = json.dumps(data['project_info'], indent=2)
contact_details = json.dumps(data['contact_details'], indent=2)
communication_history = json.dumps(data['communication_history'], indent=2)
instructions = data['instructions']

context = f"Instructions: {instructions}\n\nProject Info: {project_info}\n\nContact Details: {contact_details}\n\nCommunication History: {communication_history}"

# Session management
sessions = {}

def CustomChatGPT(user_input):
    global sessions  # Access the sessions dictionary
    
    if not sessions.get('current_session'):  # If no current session, generate a new session ID
        session_id = str(uuid.uuid4())
        sessions['current_session'] = session_id
        print(f"New Session ID: {session_id}")  # Print the new session ID
        sessions[session_id] = []  # Initialize conversation history for this session ID

    # Current session's ID
    session_id = sessions['current_session']
    
    # Initialize message history for this call
    messages = [
        {"role": "system", "content": "You are a real estate broker bot for the Jain Group. Your knowledge and responses are based on the project data provided."},
        {"role": "assistant", "content": context},
        {"role": "user", "content": user_input}
    ]
    
    # List of models in the order you want to use
    models = ["gpt-4", "GPT-4-0314", "GPT-4-0613"]
    ChatGPT_reply = ""

    for model_name in models:
        try:
            response = openai.ChatCompletion.create(
                model=model_name,
                messages=messages
            )
            ChatGPT_reply = response['choices'][0]['message']['content']
            break  # If successful, break out of the loop

        except openai.error.OpenAIError as e:  # Catch rate limit or other API exceptions
            print(f"Error with {model_name}: {e}. Trying next model...")
            continue

    # Add to session's conversation history
    sessions[session_id].append(f"User: {user_input}\n")
    sessions[session_id].append(f"Bot: {ChatGPT_reply}\n")

    # Return the entire conversation history of this session
    return ''.join(sessions[session_id])

demo = gradio.Interface(fn=CustomChatGPT, inputs="text",
                        outputs="text", title="Jain Group Bot")

demo.launch(share=True)
