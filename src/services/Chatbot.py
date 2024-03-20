# chatbot.py
import openai
import json

class Chatbot:
    def __init__(self, functions_call):
        self.functions_call = functions_call
        self.tools_list = self.functions_call.get_tools_list()
        self.system_message = functions_call.get_system_message()
        self.functions_available = functions_call.get_functions_available()
        

   
    def ask_chat_gpt(self, model, openai_apikey, messages):

        openai.api_key = openai_apikey

        completion = openai.chat.completions.create(
            model=model,
            messages=messages,
            tools=self.tools_list,
            tool_choice="auto",
        )
        response_message = completion.choices[0].message
        tool_calls = response_message.tool_calls
       

        if tool_calls:     
            available_functions = self.functions_call.get_functions_available()

            for tool_call in tool_calls:
                function_name = tool_call.function.name
                function_to_call = available_functions[function_name]
                function_args = json.loads(tool_call.function.arguments)
                function_response = function_to_call(**function_args)

                messages.append(
                    {
                        "tool_call_id": tool_call.id,
                        "role": "function",
                        "name": function_name,
                        "content": function_response,
                    }
                )  # extend conversation with function response
            second_response = openai.chat.completions.create(
                model=model,
                messages=messages,
            )  # get a new response from the model where it can see the function response
            return second_response.choices[0].message.content
        
        else:
            return response_message.content
        
    def get_system_message(self):
        return self.system_message
    
    def get_tools_list(self):
        return self.tools_list
    
    def get_functions_available(self):
        return self.functions_available
    
    def get_functions_call(self):
        return self.functions_call