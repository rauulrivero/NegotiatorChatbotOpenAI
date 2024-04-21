from src.utils.file_operations import FileUtils
import os
from dotenv import load_dotenv, unset_key
from openai import OpenAI

class Tooling:
    def __init__(self, file_name='negotiator_tools.json'):
        self.file_name = file_name
        self.tools_data = self.load_tools()
        load_dotenv()

        self.client = OpenAI()
        self.client.api_key = os.getenv("OPENAI_API_KEY")

    def load_tools(self):
        """
        Carga las herramientas desde el archivo JSON.
        """
        return FileUtils.read_json(self.file_name)

    def add_tool(self, tool):
        """
        Añade una nueva herramienta al archivo JSON.

        Args:
            tool (dict): La herramienta a añadir.
        """
        if 'tools' not in self.tools_data:
            self.tools_data['tools'] = []
        self.tools_data['tools'].append(tool)
        self.save_tools()

    def save_tools(self):
        """
        Guarda las herramientas modificadas de vuelta en el archivo JSON.
        """
        FileUtils.save_json(self.file_name, self.tools_data)

    def get_tools(self):
        """
        Obtiene todas las herramientas.

        Returns:
            list: Una lista de todas las herramientas.
        """
        return self.tools_data.get('tools', [])

    def delete_assistant(self):
        """
        Elimina un asistente.

        Args:
            assistant_id (str): El ID del asistente a eliminar.
        """

        assistant_id = os.getenv('ASSISTANT_ID')

        self.client.beta.assistants.delete(assistant_id)

        unset_key('.env', 'ASSISTANT_ID')


    # delete tool por la key del json
    def delete_tool(self, tool_key):
        """
        Elimina una herramienta.

        Args:
            tool_key (str): La clave de la herramienta a eliminar.
        """
        tools = self.get_tools()
        for tool in tools:
            if tool.get('key') == tool_key:
                tools.remove(tool)
                self.save_tools()
                break
            
    def delete_thread(self):
        """
        Elimina un hilo.
        """

        thread_id = os.getenv('THREAD_ID')
        self.client.beta.threads.delete(thread_id)
        unset_key('.env', 'THREAD_ID')