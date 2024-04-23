import json

class FileUtils:
    @staticmethod
    def save_json(file_name, data):
        """
        Saves data to a JSON file.

        Args:
            file_name (str): The name of the file to save to.
            data (dict): The data to save into the file.

        Returns:
            None
        """
        with open(file_name, 'w') as outfile:
            json.dump(data, outfile)

    @staticmethod
    def read_json(file_name):
        """
        Reads data from a JSON file.

        Args:
            file_name (str): The name of the file to read from.

        Returns:
            dict: The data read from the file, or an empty dict if the file does not exist.
        """
        try:
            with open(file_name) as json_file:
                return json.load(json_file)
        except FileNotFoundError:
            return {}
