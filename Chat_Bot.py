import os
import json
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import FAISS
from langchain.chains.question_answering import load_qa_chain
from langchain import PromptTemplate
from langchain import VectorDBQA
from langchain.memory import ConversationBufferMemory
from langchain.chat_models import ChatOpenAI
from langchain.embeddings.openai import OpenAIEmbeddings
from reportlab.lib.pagesizes import letter
from dotenv import load_dotenv
import pdb
load_dotenv()

# Loading environment variables
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]

# Directory to store conversation files
conversations_dir = os.getcwd() + "/conversations"
os.makedirs(conversations_dir, exist_ok=True)

# Function to load conversation from file
def load_conversation(token_id):
    conversation_file_path = os.path.join(conversations_dir, f"{token_id}_conversation.json")
    if os.path.exists(conversation_file_path):
        if os.path.getsize(conversation_file_path) > 0:  # Check if the file is not empty
            with open(conversation_file_path, "r") as conversation_file:
                return json.load(conversation_file)
        else:
            return []
    return []

# Function to save conversation to file
def save_conversation(token_id, conversation):
    conversation_file_path = os.path.join(conversations_dir, f"{token_id}_conversation.json")
    with open(conversation_file_path, "w") as conversation_file:
        json.dump(conversation, conversation_file, indent=2)

# Baggle Bot class
class Baggle_Bot:
    def __init__(self):
        # Initialize attributes
        self.history = []
        self.human_input = ''
        self.input_documents = []
        self.output_text = ''
        self.save_path = "embedding_directory/"

        # Prompt template for chat
        self.prompt_temp = """
            - Role: Customer support for Baggle
            - Objective: Provide accurate responses to customer queries
            ... (template continues)
            QUESTION: {human_input}
        """

        # Initialize embeddings and database
        self.embeddings = OpenAIEmbeddings()  # Using OpenAI embeddings
        self.db = FAISS.load_local(self.save_path, self.embeddings, allow_dangerous_deserialization=True)

        # Initialize prompt template, memory, and chain
        self.prompt_template = PromptTemplate(input_variables=["context", "human_input", "chat_history"], template=self.prompt_temp)
        self.memory = ConversationBufferMemory(input_key='human_input', memory_key="chat_history", return_messages=True)
        self.chain = load_qa_chain(
            llm=ChatOpenAI(
                openai_api_key=OPENAI_API_KEY,
                model_name="gpt-3.5-turbo",
                presence_penalty=0.0,
                temperature=0,
                max_tokens=500
            ),
            chain_type="stuff",
            memory=self.memory,
            prompt=self.prompt_template
        )

    # Method to ask a question
    def question(self, token, user_input):
        # Search for similar documents in the database
        docs = self.db.similarity_search(user_input)
        # Load conversation history
        conversation = load_conversation(token)
        # Generate response using the chain
        response = self.chain({"input_documents": docs, "human_input": user_input, "chat_history": conversation})
        # Update output text and conversation history
        self.output_text = response['output_text']
        self.history = response['chat_history']
        for text in self.history[-2:]:
            if text.type == "ai":
                conversation.append({"AIMessage": text.content})
            else:
                conversation.append({"HumanMessage": text.content})
        # Save conversation to file
        save_conversation(token, conversation)
        # Return the response
        return response['output_text']
