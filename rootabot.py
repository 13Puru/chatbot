import os
import openai
import streamlit as st
from collections import defaultdict
from dotenv import load_dotenv

class RootaBot:
    def __init__(self):
        self.system_prompt = """You are RootaBot, an exclusive expert on indigenous plants and traditional medicine from Northeast India. 
You have access to information about medicinal plants and their traditional uses.

STRICT OPERATIONAL RULES:
1. ONLY answer questions about:
   - Traditional medicinal plants from Northeast India
   - Traditional medicine preparation methods
   - Indigenous medical practices from Northeast India
   - Plant conservation in Northeast India
   - Cultural significance of medicinal plants in Northeast Indian communities

2. IMMEDIATELY REJECT any off-topic questions with:
   "I can only provide information about traditional medicinal plants and practices from Northeast India. Please ask me about indigenous plants, traditional medicines, or healing practices specifically from Northeast India's states (Assam, Meghalaya, Arunachal Pradesh, Nagaland, Manipur, Mizoram, Tripura, and Sikkim)."

3. When answering relevant questions:
   - Include specific Northeast Indian communities/regions
   - Provide both traditional and scientific names
   - Give detailed preparation methods
   - List all precautions
   - Add medical disclaimers"""
        
        self.relevant_keywords = [
            'medicinal', 'plant', 'herb', 'traditional', 'indigenous', 'northeast',
            'assam', 'meghalaya', 'arunachal', 'nagaland', 'manipur', 'mizoram',
            'tripura', 'sikkim', 'tribal', 'healing', 'remedy', 'preparation',
            'decoction', 'poultice', 'medicine', 'cure', 'treatment', 'ailment',
            'nefafu', 'mishimi teeta', 'soh-shang', 'jadur bandhu'
        ]
        
        # Initialize OpenAI API
        load_dotenv()
        openai.api_key = os.getenv("OPENAI_API_KEY")

    def is_relevant_query(self, query: str) -> bool:
        """Check if query is relevant to Northeast Indian traditional medicine"""
        query = query.lower()
        return any(keyword in query for keyword in self.relevant_keywords)

    def get_response(self, query: str) -> str:
        """Generate response based on query relevance"""
        if not self.is_relevant_query(query):
            return ("I can only provide information about traditional medicinal plants and practices from Northeast India. "
                   "Please ask me about indigenous plants, traditional medicines, or healing practices specifically from "
                   "Northeast India's states (Assam, Meghalaya, Arunachal Pradesh, Nagaland, Manipur, Mizoram, Tripura, and Sikkim).")
        
        # Combine system prompt with user query
        full_prompt = f"{self.system_prompt}\n\nUser Query: {query}\nResponse:"
        
        # Generate response using OpenAI API
        response = openai.Completion.create(
            model="gpt-3.5-turbo",  # Use the latest available model
            prompt=full_prompt,
            max_tokens=2048,
            n=1,
            stop=None,
            temperature=0.7,
        )
        
        return response.choices[0].message.content.strip()

def initialize_session_state():
    """Initialize session state variables"""
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    if 'bot' not in st.session_state:
        st.session_state.bot = RootaBot()

def main():
    st.title("🌿 RootaBot - Northeast Indian Traditional Medicine Expert")
    
    st.markdown("""
    Welcome to RootaBot! I specialize in traditional medicinal plants and practices from Northeast India.
    Ask me about indigenous plants, traditional medicines, or healing practices from the northeastern states.
    
    **Sample questions you can ask:**
    - What are the traditional uses of Mishimi Teeta?
    - How is Nefafu used in Arunachal Pradesh?
    - Tell me about medicinal plants used for fever in Assam
    - What are the preparation methods for Soh-shang?
    """)
    
    initialize_session_state()
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Ask about traditional medicine from Northeast India..."):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Generate and display assistant response
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = st.session_state.bot.get_response(prompt)
            message_placeholder.markdown(full_response)
            st.session_state.messages.append({"role": "assistant", "content": full_response})

if __name__ == "__main__":
    main()