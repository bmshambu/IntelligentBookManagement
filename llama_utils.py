import requests
import json

class BookSummaryGenerator:
    def __init__(self, api_url="http://localhost:11434/api/generate", model_name="llama3.1"):
        self.api_url = api_url
        self.model_name = model_name
        self.headers = {"Content-Type": "application/json"}

    def generate_summary(self, book_content):
        """
        Generate a summary for a given book content.
        
        Args:
            book_content (str): The content of the book to summarize.
        
        Returns:
            str: The generated summary.
        """
        prompt = f"Please provide a summary for the following book content:\n\n{book_content}"
        data = {
            "model": self.model_name,
            "prompt": prompt
        }
        response = self._send_request(data)
        return response

    def generate_review_summary(self, reviews):
        """
        Generate a summary for a list of reviews.
        
        Args:
            reviews (list of str): List of review texts.
        
        Returns:
            str: The generated review summary.
        """
        reviews_text = "\n\n".join(reviews)
        prompt = f"Please summarize the following reviews:\n\n{reviews_text}"
        data = {
            "model": self.model_name,
            "prompt": prompt
        }
        response = self._send_request(data)
        return response

    def _send_request(self, data):
        """
        Send a request to the Llama3 API and return the response.
        
        Args:
            data (dict): The payload data for the API request.
        
        Returns:
            str: The response from the Llama3 API.
        """
        response = requests.post(self.api_url, headers=self.headers, data=json.dumps(data), stream=True)
        if response.status_code == 200:
            result = []
            for line in response.iter_lines():
                if line:
                    line_data = json.loads(line)
                    if "response" in line_data:
                        result.append(line_data["response"])
                    if line_data.get("done", False):
                        break
            return " ".join(result)
        else:
            print("Failed to get response. Status code:", response.status_code)
            print("Response:", response.text)
            return None


