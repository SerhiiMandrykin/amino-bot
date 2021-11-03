import os

from google.cloud import dialogflow_v2 as dialogflow
from google.oauth2.service_account import Credentials

from lib.exceptions import NoDialogflowCredentialsFileFound


class ChatClient:
    def __init__(self, project_id):
        self.project_id = project_id
        self.file_path = os.getcwd() + '/dialogflow.json'
        if not os.path.isfile(self.file_path):
            raise NoDialogflowCredentialsFileFound(
                'No Dialogflow credentials file found. Please add it. The name should be dialogflow.json'
            )

        self.session_client = dialogflow.SessionsClient(
            credentials=Credentials.from_service_account_file(self.file_path))

    def get_response(self, session_id, text):
        """Returns the result of detect intent with texts as inputs.

        Using the same `session_id` between requests allows continuation
        of the conversation."""
        session = self.session_client.session_path(self.project_id, session_id)

        text_input = dialogflow.TextInput(text=text, language_code='ru')

        query_input = dialogflow.QueryInput(text=text_input)

        response = self.session_client.detect_intent(
            request={"session": session, "query_input": query_input}
        )

        return response.query_result.fulfillment_text
