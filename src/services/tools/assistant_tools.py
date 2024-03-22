from src.utils.file_operations import FileUtils

class Tooling:
    def __init__(self, file_name='negotiator_tools.json'):
        self.file_name = file_name
        self.tools_data = self.load_tools()

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
