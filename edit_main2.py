# <main.py>
# uvicorn main:app --reload

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from openai import ChatCompletion, OpenAI
from dotenv import load_dotenv
import logging
import os
import datetime

# mongodb.py에서 함수 import
from mongodb_org import insert_item_many

# Simple in-memory cache
cache = {}

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# OpenAI API key setup
load_dotenv()
API_KEY = os.environ['OPENAI_API_KEY']
client = OpenAI(api_key=API_KEY)

# FastAPI app setup
app = FastAPI()

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# FastAPI models
class UserRequest(BaseModel):
    utterance: str

class BotResponse(BaseModel):
    bot_message: str

# Queue object creation
response_queue = []

# Template directory setup
templates = Jinja2Templates(directory="templates")

# Maximum number of previous exchanges to keep
MAX_HISTORY_LENGTH = 7

# Function to trim the conversation history
def trim_conversation_history():
    global response_queue
    if len(response_queue) > MAX_HISTORY_LENGTH:
        # Keep only the last MAX_HISTORY_LENGTH exchanges
        response_queue = response_queue[-MAX_HISTORY_LENGTH:]

# Root endpoint for rendering HTML
@app.get("/", response_class=HTMLResponse)
def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# Chatbot endpoint
@app.post('/chatbot/', response_model=BotResponse)
async def chat(user_request: UserRequest):
    user_question = user_request.utterance.strip()

    logger.debug(f'Received POST request: {user_question}')

    if user_question:
        # Call trim function before appending new response to ensure the queue length is maintained
        trim_conversation_history()

        gpt_answer = get_qa_by_gpt(user_question)
        response_queue.append(gpt_answer)  # Now the queue will never exceed MAX_HISTORY_LENGTH
        logger.debug(f'Response queue: {response_queue}')
        return JSONResponse(content={'bot_message': gpt_answer})
    else:
        return JSONResponse(content={'bot_message': 'No input received'})

# Additional endpoint to get the response
@app.get('/response/', response_class=JSONResponse)
async def get_response():
    if response_queue:
        return JSONResponse(content={'bot_message': response_queue.pop(0)})
    else:
        return JSONResponse(content={'bot_message': 'No response'})

# Function to get Q&A from GPT
def get_qa_by_gpt(prompt, temperature=0.5, top_p=0.5, max_tokens=100, frequency_penalty=0.6, presence_penalty=0.1, stop=None, n=1):
    # Generate a cache key based on the prompt and parameters
    cache_key = (prompt, temperature, top_p, max_tokens, frequency_penalty, presence_penalty, stop, n)
    # Check if the response is already in the cache
    if cache_key in cache:
        logger.debug(f'Cache hit for prompt: {prompt}')
        return cache[cache_key]

    # Include the conversation history in the prompt
    conversation_history = "".join(response_queue)
    full_prompt = conversation_history + "\nUser: " + prompt + "\nAssistant: "

    prompt_template = [
    {"role": "system", "content":
    """
    You are a chatbot that gives guidance on which clinic the user has to visit giving a three expected illnesses, ordered by likelihood.
    Follow these steps:
    1. If user input their symptoms, complete the prompt as shown below:
    - user's symptom: soar throat with fever
    2. Tell them where to visit based on their symptoms in Korean necessarily, complete the prompt as shown below. You have to tell the result is expected disease.
    Returns:
    <top 3 expected diseases and hospital departments you have to go>
    - 1. asthma - Paediatrics
    - 2. cold - Internal medicine department
    - 3. Chronic Obstructive Pulmonary Disease - Cardiology
    """},
        {"role": "user", "content": full_prompt}
    ]

    try:
        response = client.chat.completions.create(
            model='gpt-3.5-turbo-1106',
            messages=prompt_template,
            temperature=temperature,
            top_p=top_p,
            max_tokens=max_tokens,
            frequency_penalty=frequency_penalty,
            presence_penalty=presence_penalty,
            stop=stop,
            n=n
        )

        message = response.choices[0].message.content
        # Cache the response
        cache[cache_key] = message
        response_queue.append("User: " + prompt)
        response_queue.append("Assistant: " + message)


        # test
        inserted_id = insert_item_many(message, db_name= "HealthCube", collection_name='user_chat_logs')
        print(f"Data inserted with ID: {inserted_id}")

        # # Check if hospital department information is present in the response
        # if "내과" in message:
        #     # Create a document to store in MongoDB
        #     document = {
        #         "timestamp": datetime,
        #         "conversation_history": response_queue.copy(),
        #     }

        #     # Insert the document into MongoDB
        #     inserted_id = insert_user_chat(document)
        #     print("MongoDB insertion successful")

        #     # Clear the response_queue after successful insertion
        #     response_queue.clear()
        # else:
        #     print("Fail to insert in MongoDB")


        logger.debug(f'GPT response: {message}')
        return message
    except Exception as e:
        logger.error(f'Error during OpenAI API call: {e}')
        return "Sorry, I am unable to process your request at the moment."