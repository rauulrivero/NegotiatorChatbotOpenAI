# chatbot.py
from openai import OpenAI
import time
import json
import dotenv
import os
dotenv.load_dotenv()
ASSISTANT_ID = os.getenv('ASSISTANT_ID')
THREAD_ID = os.getenv('THREAD_ID')

class Chatbot:
    def __init__(self, functions_call):
        self.functions_call = functions_call
        self.tools_list = self.functions_call.get_tools_list()
        self.system_message = functions_call.get_system_message()
        self.functions_available = functions_call.get_functions_available()
        self.client = OpenAI()
        self.run = None
        self.message = None
        self.model_name = "gpt-4-1106-preview"
        global ASSISTANT_ID, THREAD_ID
        if ASSISTANT_ID is None: 
            self._create_assistant()
        if THREAD_ID is None:
            self.create_thread()



    def _create_assistant(self):
        """Función privada para crear un asistente."""
        assistant_name = "Negotiator Assistant"

        file1 = self.client.files.create(file=open("content/festivos-las-arenas.pdf", "rb"), purpose="assistants")
        
        tools = self.tools_list
        tools.append({"type" : "retrieval"})

        assistant = self.client.beta.assistants.create(
            name=assistant_name,
            instructions=self.system_message,
            model=self.model_name,
            tools=tools,
            file_ids=[file1.id]
        )

        # Guarda el ID del asistente creado para uso futuro
        global ASSISTANT_ID
        ASSISTANT_ID = assistant.id
        dotenv.set_key('.env', 'ASSISTANT_ID', ASSISTANT_ID)

    
    def create_thread(self):
            """Crea un nuevo hilo y devuelve su ID."""
            thread = self.client.beta.threads.create()
            
            global THREAD_ID
            THREAD_ID = thread.id
            dotenv.set_key('.env', 'THREAD_ID', THREAD_ID)


   

    def ask_assistant(self, openai_apikey, message):

        self.client.api_key = openai_apikey

        if THREAD_ID is None:
            self.create_thread()

        self.client.beta.threads.messages.create(
            thread_id=THREAD_ID,
            role="user",
            content=message["content"]
        )

        # Step 4: Run the Assistant
        run = self.client.beta.threads.runs.create(
            thread_id=THREAD_ID,
            assistant_id=ASSISTANT_ID,
            instructions=self.system_message
        )

        
        while True:
            # If run is completed, get messages
            run_status = self.client.beta.threads.runs.retrieve(
            thread_id=THREAD_ID,
            run_id=run.id
        )

            if run_status.status == 'completed':
                messages = self.client.beta.threads.messages.list(
                    thread_id=THREAD_ID
                )

                # Loop through messages and print content based on role
                for msg in messages.data:
                    content = msg.content[0].text.value
                    return content

                break

            elif run_status.status == 'requires_action':
                print("Function Calling")
                required_actions = run_status.required_action.submit_tool_outputs.model_dump()
                print(required_actions)
                tool_outputs = []
                
            
                for action in required_actions["tool_calls"]:
                    func_name = action['function']['name']
                    arguments = json.loads(action['function']['arguments'])

                    func_to_call = self.functions_available.get(func_name)
                    
                    # Verifica si la función existe.
                    if func_to_call:
                        output = func_to_call(**arguments)
                        tool_outputs.append({
                            "tool_call_id": action['id'],
                            "output": output
                        })
                    else:
                        raise ValueError(f"Unknown function: {func_name}")
                    
                print("Submitting outputs back to the Assistant...")
                self.client.beta.threads.runs.submit_tool_outputs(
                    thread_id=THREAD_ID,
                    run_id=run.id,
                    tool_outputs=tool_outputs
                )
            else:
                print("Waiting for the Assistant to process...")
                time.sleep(5)
        
        
    def get_system_message(self):
        return self.system_message
    
    def get_tools_list(self):
        return self.tools_list
    
    def get_functions_available(self):
        return self.functions_available
    
    def get_functions_call(self):
        return self.functions_call