# chatbot.py
import openai
import json

class Chatbot:
    def __init__(self, functions):
        self.functions = functions
        self.tools_list = self.functions.get_tools_list()
        self.system_message = functions.get_system_message()
        

   
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
            available_functions = self.functions.get_functions_available()

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