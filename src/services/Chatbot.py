# chatbot.py
import openai

class Chatbot:
    def __init__(self, functions_description):
        self.functions_description = functions_description
        
    def detect_function(self, prompt, openai_apikey, model_name):
        """Give LLM a given prompt and get an answer."""
        openai.api_key = openai_apikey

        completion = openai.chat.completions.create(
            model=model_name,
            messages=[{"role": "user", "content": prompt}],

            functions=self.functions_description,
            function_call="auto",  # specify the function call
        )

        output = completion.choices[0].message
        return output
    
    def function_calling(self, prompt, function, content, openai_apikey, model_name):
        """Give LLM a given prompt and get an answer."""
        openai.api_key = openai_apikey

        completion = openai.chat.completions.create(
            model=model_name,
            messages=[{"role": "user", "content": prompt},
                    {"role":"function", "name": function, "content": content}],

            functions=self.functions_description,
            function_call="auto",  # specify the function call
        )

        output = completion.choices[0].message
        return output
    

    