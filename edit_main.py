# <main.py>
# uvicorn main:app --reload
import json
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from openai import ChatCompletion, OpenAI
from dotenv import load_dotenv
import logging
import os

# Simple in-memory cache
cache = {}

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# OpenAI API key setup
load_dotenv()
API_KEY = os.environ['OPENAI_API_KEY']
client = OpenAI(api_key=API_KEY)

# Initialize OpenAI client
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

class MedicalDepartment(BaseModel):
    name: str
    link: str

# Define medical departments and their links
medical_departments = [
    MedicalDepartment(name="이비인후과", link="file:///C:/Users/user/Desktop/Soobp9-saltlux_sessac_1-front/html/map.html"),
    # Add other departments similarly
    MedicalDepartment(name="내과", link="https://map.naver.com/p/search/%EA%B8%88%EC%B2%9C%EA%B5%AC%20%EB%82%B4%EA%B3%BC?searchType=place&c=13.00,0,0,0,dh"),
    # Add other departments similarly
    MedicalDepartment(name="치과", link="file:///C:/Users/user/Desktop/Soobp9-saltlux_sessac_1-front/html/hospital.html"),
    # Add other departments similarly
]

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

        gpt_answer, department = get_qa_by_gpt(user_question)
        response_queue.append(gpt_answer)  # Now the queue will never exceed MAX_HISTORY_LENGTH
        logger.debug(f'Response queue: {response_queue}')
        return JSONResponse(content={'bot_message': gpt_answer, 'department':department})
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
    # Include the conversation history in the prompt
    conversation_history = "".join(response_queue)
    full_prompt = conversation_history + "\nUser: " + prompt + "\nAssistant: "

    cache_key = (prompt, temperature, top_p, max_tokens, frequency_penalty, presence_penalty, stop, n)  # Define cache_key

    prompt_template = [
        {"role": "system", "content": """I am a good and kind medical assistant.
         I will respond in Korean with answers of fewer than 50 words. If the user
         provides their symptoms, gender, and age, I will provide three likely
         medical conditions. When a user presents information about his or her symptoms,
         “다른 증상은 없나요?” is asked only once in the entire conversation and must
         be answered in the following format. "당신의 증상과 건강상태를 고려하면 유력한
         질병은 (질환명1) (0~100%), (질환명2) (0~100%), (질환명3) (0~100%) 일 가능성이
         높습니다냥. 이에 따라 당신이 방문해야 할 진료과를 추천드리면
         <질환명1과 관련한 진료과 목록>, <질환명2과 관련한 진료과 목록>,
         <질환명3과 관련한 진료과 목록>입니다."`
         (Considering your symptoms and health, the likely diseases
         are (Disease 1) (0~100%), (Disease 2) (0~100%), (Disease 3) (0~100%).
         Accordingly, I recommend visiting <Specialty 1>, <Specialty 2>,
         <Specialty 3>.) """},
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
        # Cache the response using cache_key
        cache[cache_key] = message
        response_queue.append("User: " + prompt)
        response_queue.append("Assistant: " + message)

        # Check if any medical department is mentioned in the bot's response
        for department in medical_departments:
            if department.name in message:
                # If the department name is found, replace it with a clickable link
                department = department.name
                link = f'<a href="{department.link}" target="_blank">{department.name}</a>'
                message = message.replace(department.name, link)

        logger.debug(f'GPT response: {message}')
        return {"msg":message, "department":department}
    except Exception as e:
        logger.error(f'Error during OpenAI API call: {e}')
        return "Sorry, I am unable to process your request at the moment."