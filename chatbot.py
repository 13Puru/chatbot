import streamlit as st
import re
import json
from langchain_community.llms import Ollama
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain.schema import HumanMessage, AIMessage
import time

class PlantDatabase:
    def __init__(self):
        """Initialize the plant database with traditional medicinal plants from Northeast India"""
        self.plants_db = {
            "nefafu": {
                "scientific_name": "Nepeta hindostana",
                "traditional_names": {
                    "Arunachal Pradesh": "Nefafu",
                    "Assam": "Bhedai-phul"
                },
                "regions": ["Arunachal Pradesh", "Assam"],
                "communities": ["Nyishi", "Apatani", "Assamese"],
                "uses": [
                    "Treatment of fever",
                    "Relief from respiratory ailments",
                    "Treatment of common cold"
                ],
                "preparation": "Leaves are crushed and boiled in water to make a decoction. Taken orally twice daily.",
                "precautions": [
                    "Not recommended for pregnant women",
                    "Avoid excessive consumption"
                ],
                "conservation_status": "Common"
            },
            "mishimi_teeta": {
                "scientific_name": "Coptis teeta",
                "traditional_names": {
                    "Arunachal Pradesh": "Mishimi Teeta",
                    "Assam": "Misimi Tita"
                },
                "regions": ["Arunachal Pradesh", "Assam"],
                "communities": ["Mishmi", "Adi", "Assamese"],
                "uses": [
                    "Treatment of malaria",
                    "Digestive disorders",
                    "Anti-inflammatory"
                ],
                "preparation": "Root powder mixed with warm water or honey. Small doses taken 2-3 times daily.",
                "precautions": [
                    "Start with small doses",
                    "Not for long-term use",
                    "Avoid during pregnancy"
                ],
                "conservation_status": "Endangered"
            },
            "soh_shang": {
                "scientific_name": "Elaeagnus pyriformis",
                "traditional_names": {
                    "Meghalaya": "Soh-shang",
                    "Assam": "Mirika tenga"
                },
                "regions": ["Meghalaya", "Assam"],
                "communities": ["Khasi", "Garo", "Assamese"],
                "uses": [
                    "Blood pressure regulation",
                    "Digestive health",
                    "Vitamin C source"
                ],
                "preparation": "Fresh fruits eaten raw or made into juice. Bark decoction used medicinally.",
                "precautions": [
                    "Moderate consumption recommended",
                    "Watch for allergic reactions"
                ],
                "conservation_status": "Common"
            },
            "jadur_bandhu": {
                "scientific_name": "Homalomena aromatica",
                "traditional_names": {
                    "Assam": "Jadur bandhu",
                    "Manipur": "Ising"
                },
                "regions": ["Assam", "Manipur"],
                "communities": ["Bodo", "Meitei"],
                "uses": [
                    "Rheumatic pain relief",
                    "Skin infections",
                    "Aromatherapy"
                ],
                "preparation": "Rhizome paste applied externally. Essential oil used in aromatherapy.",
                "precautions": [
                    "External use only",
                    "Patch test recommended",
                    "Keep away from eyes"
                ],
                "conservation_status": "Vulnerable"
            }
        }

    def search_plants(self, query: str) -> list:
        """Search for plants in the database based on query terms"""
        query = query.lower()
        results = []
        
        for plant_id, plant_info in self.plants_db.items():
            # Search in scientific name
            if query in plant_info["scientific_name"].lower():
                results.append(plant_info)
                continue
                
            # Search in traditional names
            for region, name in plant_info["traditional_names"].items():
                if query in name.lower():
                    results.append(plant_info)
                    break
                    
            # Search in uses
            if any(query in use.lower() for use in plant_info["uses"]):
                results.append(plant_info)
                
        return results

    def get_plant_info(self, plant_name: str) -> dict:
        """Get detailed information about a specific plant"""
        plant_name = plant_name.lower()
        for plant_id, plant_info in self.plants_db.items():
            if plant_name in plant_id.lower() or \
               plant_name in plant_info["scientific_name"].lower() or \
               any(plant_name in name.lower() for name in plant_info["traditional_names"].values()):
                return plant_info
        return None

class RootaBot:
    def __init__(self):
        """Initialize RootaBot with system prompt, keywords, and plant database"""
        self.system_prompt = """You are RootaBot, exclusively focused expert only and only in indigenous plants and traditional medicine from Northeast India. 
You have access to a database of medicinal plants and their traditional uses.

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
        
        # Initialize plant database
        self.plant_db = PlantDatabase()
        
        # Initialize Ollama with streaming
        callback_manager = CallbackManager([StreamingStdOutCallbackHandler()])
        self.llm = Ollama(
            model="llama2",
            callback_manager=callback_manager,
            temperature=0.7
        )

    def is_relevant_query(self, query: str) -> bool:
        """Check if query is relevant to Northeast Indian traditional medicine"""
        query = query.lower()
        return any(keyword in query for keyword in self.relevant_keywords)

    def enhance_response_with_db(self, query: str, base_response: str) -> str:
        """Enhance the LLM response with specific plant information from the database"""
        plants = self.plant_db.search_plants(query.lower())
        if not plants:
            return base_response
            
        enhanced_response = base_response + "\n\nDetailed plant information from our database:\n\n"
        for plant in plants:
            enhanced_response += f"🌿 {list(plant['traditional_names'].values())[0]} ({plant['scientific_name']})\n"
            enhanced_response += f"📍 Regions: {', '.join(plant['regions'])}\n"
            enhanced_response += f"👥 Communities: {', '.join(plant['communities'])}\n"
            enhanced_response += f"💊 Uses:\n" + "\n".join(f"  - {use}" for use in plant['uses']) + "\n"
            enhanced_response += f"📝 Preparation: {plant['preparation']}\n"
            enhanced_response += f"⚠️ Precautions:\n" + "\n".join(f"  - {precaution}" for precaution in plant['precautions']) + "\n"
            enhanced_response += f"🌍 Conservation Status: {plant['conservation_status']}\n\n"
            
        return enhanced_response

    def get_response(self, query: str) -> str:
        """Generate response based on query relevance and enhance with database information"""
        if not self.is_relevant_query(query):
            return ("I can only provide information about traditional medicinal plants and practices from Northeast India. "
                   "Please ask me about indigenous plants, traditional medicines, or healing practices specifically from "
                   "Northeast India's states (Assam, Meghalaya, Arunachal Pradesh, Nagaland, Manipur, Mizoram, Tripura, and Sikkim).")
        
        # Combine system prompt with user query
        full_prompt = f"{self.system_prompt}\n\nUser Query: {query}\nResponse:"
        base_response = self.llm.invoke(full_prompt)
        
        # Enhance response with database information
        enhanced_response = self.enhance_response_with_db(query, base_response)
        return enhanced_response

def initialize_session_state():
    """Initialize session state variables"""
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    if 'bot' not in st.session_state:
        st.session_state.bot = RootaBot()

def main():
    st.title("🌿 RootaBot - Northeast Indian Traditional Medicine Expert")
    
    # Sidebar with database information
    st.sidebar.title("Available Plants Database")
    bot = RootaBot()
    for plant_id, plant_info in bot.plant_db.plants_db.items():
        st.sidebar.markdown(f"""
        **{list(plant_info['traditional_names'].values())[0]}**  
        *{plant_info['scientific_name']}*  
        Region: {', '.join(plant_info['regions'])}  
        Status: {plant_info['conservation_status']}
        ---
        """)
    
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