from openai import OpenAI
from pydantic import BaseModel
from time import sleep
from dotenv import load_dotenv
import os
import json

# Load environment variables from .env file
load_dotenv()

# Set up OpenAI client
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

# Define Pydantic models for input and output
class QuestionInput(BaseModel):
    request_type: str
    paper_num: int
    question_num: int
    extract: bool = False

class GeneratedQuestionOutput(BaseModel):
    question: str
    extract: str = None
    marks: int

def create_assistant():
    return client.beta.assistants.retrieve("asst_aiTZELsdg1GTcWS6nhYjZZsT")

def create_thread():
    return client.beta.threads.create()

def send_message(thread_id, message):
    thread_message = client.beta.threads.messages.create(
        thread_id,
        role="user",
        content=message  # Send the JSON message
    )
    return thread_message

def run_assistant(thread_id, assistant_id):
    run = client.beta.threads.runs.create(thread_id=thread_id, assistant_id=assistant_id)
    return run

def get_newest_message(thread_id):
    thread_messages = client.beta.threads.messages.list(thread_id)
    return thread_messages.data[0]

def get_run_status(thread_id, run_id):
    run = client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run_id)
    return run.status

def handle_generate_question(paper_num, question_num, extract):
    question_input = QuestionInput(
        request_type="generate_question",
        paper_num=paper_num,
        question_num=question_num,
        extract=extract
    )
    return question_input.json()

def main():
    my_assistant = create_assistant()
    my_thread = create_thread()

    while True:
        paper_num = int(input("Enter paper number: "))
        question_num = int(input("Enter question number: "))
        extract = input("Generate an extract? (yes/no): ").lower() == "yes"

        request_json = handle_generate_question(paper_num, question_num, extract)

        try:
            send_message(my_thread.id, request_json)
            run = run_assistant(my_thread.id, my_assistant.id)

            while run.status != "completed":
                run.status = get_run_status(my_thread.id, run.id)
                sleep(0.1)
                print(" " * 50, end="\r", flush=True)
                print(f"{run.status} ⏳", end="\r", flush=True)

            sleep(0.5)
            response = get_newest_message(my_thread.id)
            response_text = response.content[0].text.value
            
            # Parse the JSON response into Pydantic object
            response_data = json.loads(response_text)
            question_output = GeneratedQuestionOutput(**response_data)
            
            # Print the generated question and extract
            print(f"\nGenerated Question:\n{question_output.question}")
            print(f"\nGenerated Extract:\n{question_output.extract}")
            print(f"\nMarks: {question_output.marks}")

        except Exception as e:
            print(e)

if __name__ == "__main__":
    main()
