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

# OPENAI_API_KEY = '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'
OPENAI_API_KEY=os.environ["OPENAI_API_KEY"]

conversations_dir = os.getcwd()+"/conversations"

# os.path.join(os.path.dirname(os.path.abspath(__file__)), "conversations/")
os.makedirs(conversations_dir, exist_ok=True)

def load_conversation(token_id):
    conversation_file_path = os.path.join(conversations_dir, f"{token_id}_conversation.json")
    if os.path.exists(conversation_file_path):
        if os.path.getsize(conversation_file_path) > 0:  # Check if the file is not empty
            with open(conversation_file_path, "r") as conversation_file:
                return json.load(conversation_file)
        else:
            return []
    return []

def save_conversation(token_id, conversation):
    conversation_file_path = os.path.join(conversations_dir, f"{token_id}_conversation.json")
    with open(conversation_file_path, "w") as conversation_file:
        json.dump(conversation, conversation_file, indent=2)



class Baggle_Bot:
    def __init__(self):
        self.history = []
        self.human_input = ''
        self.input_documents = []
        self.output_text = ''
        
        self.save_path = "embedding_directory/"
        
        self.prompt_temp = """
                - Role: Customer support for Baggle
                - Objective: Provide accurate responses to customer queries
                - Uncertain Answers: Direct customers to contact Baggle customer support via email
                DOCUMENT:
                ==========
                {context}
                ==========
                - Guidelines:
                      1. Base answers on provided information
                      2. Clarify Baggle is a fabric shopping platform, not for logo creation
                      3. Provide exact prices for pricing queries
                      4. Describe e-commerce platform features and customer support for service inquiries
                      5. Share details on fabric types for product-related questions
                      6. Offer information on available lace products when asked about laces
                      7. Provide company headquarters details for location inquiries
                      8. If unaware of promotions, advise checking the website
                      9. Detail specific clothing items, including materials, care instructions, and colors
                      10. Describe product packing style if information is available
                      11. Highlight secure payment methods and positive reviews for trust-building
                      12. Clarify Baggle is primarily accessed through a web browser, not by download
                      13. Emphasize commitment to excellent service without specifying company longevity
                      14. Address shipping failure procedures or policies if known
                      15. Explain how Baggle handles out-of-stock items and managing wishlist items
                      16. Respond in a simple, first-person manner representing the company
                      17. Keep answers concise, limited to one line, unless requested otherwise
                      18. Avoid providing fabricated information
                      19. Give the correct location for store or marketplace.
                      20. Never use word "document" in your answers.
                      21. For WhatsApp inquiries:"Contact numbers/Phone numbers Baggle Senegal +221 777 020 606
         		Baggle Nigeria +234 903 306 6669
			Baggle Gambia +220 230 1535"
		      22. Contact numbers or Phone numbers of  Baggle is: Senegal +221 777 020 606 Baggle Nigeria +234 903 306 6669 Baggle Gambia +220 230 1535


                conversation history = {chat_history}
                
                QUESTION: {human_input}

                """
        
        self.embeddings =OpenAIEmbeddings() 
# OpenAIEmbeddings(model = "text-embedding-3-large")
        self.db = FAISS.load_local(self.save_path, self.embeddings,allow_dangerous_deserialization=True)
        self.prompt_template = PromptTemplate(input_variables=["context", "human_input", "chat_history"],template=self.prompt_temp )
        self.memory = ConversationBufferMemory(input_key = 'human_input', memory_key="chat_history", return_messages = True)
        self.chain = load_qa_chain(
            llm = ChatOpenAI(
                    openai_api_key = OPENAI_API_KEY,
                    model_name = "gpt-3.5-turbo",
                    presence_penalty = 0.0,

                    temperature = 0,
                    max_tokens = 500

                ),
            chain_type="stuff", 
            memory= self.memory, 

            prompt= self.prompt_template
        )
#         print(self.question("hi how are you"))
        
        
    def question(self,token, user_input):
        docs = self.db.similarity_search(user_input)       
        conversation = load_conversation(token)

        response = self.chain({"input_documents": docs, "human_input": user_input, "chat_history": conversation})
        self.output_text = response['output_text']
        self.history = response['chat_history']
        for text in self.history[-2:]:
            if text.type == "ai":
                conversation.append({"AIMessage":text.content})
            else:
                conversation.append({"HumanMessage":text.content})
        save_conversation(token, conversation)
        return response['output_text']