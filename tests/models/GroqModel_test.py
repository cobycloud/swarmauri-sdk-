import os
from swarmauri.standard.models.concrete.GroqModel import GroqModel
from swarmauri.standard.conversations.concrete.SimpleConversation import SimpleConversation
from swarmauri.standard.messages.concrete.HumanMessage import HumanMessage

def test_initialization():
    def test():
        API_KEY = os.getenv('GROQ_API_KEY')
        model = GroqModel(api_key = API_KEY)
        assert model.model_name == 'mixtral-8x7b-32768'
    test()

def test_call():
    def test():
        API_KEY = os.getenv('GROQ_API_KEY')
        conversation = SimpleConversation()


        input_data = "Hello"
        human_message = HumanMessage(input_data)
        conversation.add_message(human_message)

        model = GroqModel(api_key = API_KEY)
        assert type(model.predict(messages=conversation.as_messages())) == str
    test()