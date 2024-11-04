import streamlit as st
import requests
from typing import List, Dict
import json

class Message:
    def __init__(self, role: str, content: str):
        self.role = role
        self.content = content

class MedicinalPlant:
    def __init__(self, name: str, scientific_name: str, region: str, uses: List[str], 
                 preparations: List[Dict], properties: List[str], precautions: List[str]):
        self.name = name
        self.scientific_name = scientific_name
        self.region = region
        self.uses = uses
        self.preparations = preparations
        self.properties = properties
        self.precautions = precautions

# Database of medicinal plants
MEDICINAL_PLANTS_DB = {
    "nefafu": MedicinalPlant(
        name="Nefafu",
        scientific_name="Houttuynia cordata",
        region="Nagaland, Manipur",
        uses=[
            "Treatment of dysentery",
            "Digestive disorders",
            "Anti-inflammatory",
            "Immune system boost"
        ],
        preparations=[
            {
                "method": "Fresh Juice",
                "ingredients": ["Fresh leaves", "Clean water"],
                "steps": [
                    "Wash fresh leaves thoroughly",
                    "Crush and extract juice",
                    "Mix with small amount of water",
                    "Take 2-3 teaspoons twice daily"
                ],
                "dosage": "2-3 teaspoons twice daily"
            },
            {
                "method": "Decoction",
                "ingredients": ["Dried leaves", "Water"],
                "steps": [
                    "Boil 2-3 dried leaves in water",
                    "Reduce to half",
                    "Strain and drink warm"
                ],
                "dosage": "1 cup twice daily"
            }
        ],
        properties=["Antibacterial", "Anti-inflammatory", "Immunomodulatory"],
        precautions=["Avoid during pregnancy", "Start with small doses to test sensitivity"]
    ),
    
    "axone": MedicinalPlant(
        name="Axone (Fermented Soybean)",
        scientific_name="Glycine max",
        region="Nagaland",
        uses=[
            "Digestive health",
            "Protein supplement",
            "Traditional immunity booster"
        ],
        preparations=[
            {
                "method": "Traditional Fermentation",
                "ingredients": ["Soybeans", "Banana leaves"],
                "steps": [
                    "Clean and boil soybeans until soft",
                    "Wrap in banana leaves",
                    "Ferment for 3-5 days",
                    "Store in cool, dry place"
                ],
                "dosage": "Small amount as condiment"
            }
        ],
        properties=["Probiotic", "High protein", "Rich in vitamins"],
        precautions=["Avoid if sensitive to fermented foods", "Store properly to prevent contamination"]
    ),

    "brahmi": MedicinalPlant(
        name="Brahmi",
        scientific_name="Bacopa monnieri",
        region="Assam, Tripura",
        uses=[
            "Memory enhancement",
            "Anxiety and stress relief",
            "Cognitive function improvement",
            "Treatment of epilepsy"
        ],
        preparations=[
            {
                "method": "Brahmi Tea",
                "ingredients": ["Dried Brahmi leaves", "Water", "Honey (optional)"],
                "steps": [
                    "Boil water in a pot",
                    "Add dried Brahmi leaves",
                    "Simmer for 5-10 minutes",
                    "Strain and add honey if desired"
                ],
                "dosage": "1 cup twice daily"
            },
            {
                "method": "Brahmi Powder",
                "ingredients": ["Dried Brahmi leaves"],
                "steps": [
                    "Dry clean Brahmi leaves completely",
                    "Grind into fine powder",
                    "Store in airtight container"
                ],
                "dosage": "1/2 teaspoon with warm milk or water twice daily"
            }
        ],
        properties=["Neuroprotective", "Adaptogenic", "Memory enhancing"],
        precautions=["May cause digestive upset in high doses", "Consult doctor if on medications"]
    )
}

class RootaBot:
    def __init__(self):
        self.api_url = "http://localhost:11434/api/chat"
        self.system_prompt = """You are RootaBot,exclusively foccused expert only and only in indigenous plants and traditional medicine from Northeast India. 
You have access to a database of medicinal plants and their traditional uses. Use this information when responding to queries.
STRICT OPERATIONAL RULES:
1. ONLY answer questions about:
   - Traditional medicinal plants from Northeast India
   - Traditional medicine preparation methods
   - Indigenous medical practices from Northeast India
   - Plant conservation in Northeast India
   - Cultural significance of medicinal plants in Northeast Indian communities

2. IMMEDIATELY REJECT any questions about:
   - Modern medicine or pharmaceuticals
   - Medical practices from other regions
   - Non-medical topics
   - General health advice
   - Any topic not directly related to Northeast Indian traditional medicine

3. For ANY off-topic questions, respond ONLY with:
   "I can only provide information about traditional medicinal plants and practices from Northeast India. Please ask me about indigenous plants, traditional medicines, or healing practices specifically from Northeast India's states (Assam, Meghalaya, Arunachal Pradesh, Nagaland, Manipur, Mizoram, Tripura, and Sikkim)."

4. When answering relevant questions:
   - Include specific Northeast Indian communities/regions
   - Provide both traditional and scientific names
   - Give detailed preparation methods
   - List all precautions
   - Add medical disclaimers

You MUST stay strictly within Northeast Indian traditional medicine knowledge.

When discussing medical treatments:
1. Always start with appropriate health disclaimers
2. Provide specific details about plant preparation methods
3. Mention known precautions and contraindications
4. Include both traditional and scientific names of plants
5. Cite which indigenous communities traditionally use these methods

For plant information requests:
1. Share traditional knowledge respectfully
2. Explain preparation methods in detail
3. Include dosage guidelines when available
4. Mention conservation status if relevant

Remember: Always emphasize that this is traditional knowledge for educational purposes only."""

        self.relevant_keywords = [
            'medicinal', 'plant', 'herb', 'traditional', 'indigenous', 'northeast',
            'assam', 'meghalaya', 'arunachal', 'nagaland', 'manipur', 'mizoram',
            'tripura', 'sikkim', 'tribal', 'healing', 'remedy', 'preparation',
            'decoction', 'poultice', 'medicine', 'cure', 'treatment', 'ailment',
            'leihao', 'nefafu', 'mishimi', 'teeta', 'tami', 'soh-shang', 'jadur'
        ]

    def is_relevant_query(self, query: str) -> bool:
        """Enhanced relevance checking"""
        query = query.lower()
        
        # Must contain at least one relevant keyword
        has_relevant_keywords = any(keyword in query for keyword in self.relevant_keywords)
        
        # Expanded list of irrelevant topics
        irrelevant_patterns = [
            r'\b(computer|phone|internet|technology|software|hardware)\b',
            r'\b(car|vehicle|transportation|traffic)\b',
            r'\b(movie|entertainment|game|sport)\b',
            r'\b(politics|government|election|policy)\b',
            r'\b(modern medicine|pharmacy|hospital|doctor)\b',
            r'\b(weather|climate|forecast)\b',
            r'\b(business|finance|money|market)\b',
            r'\b(food|recipe|cooking|cuisine)\b',  # unless specifically about medicinal preparations
            r'\b(fashion|clothing|style)\b',
            r'\b(music|dance|art)\b'
        ]
        
        has_irrelevant_topics = any(re.search(pattern, query) for pattern in irrelevant_patterns)
        
        return has_relevant_keywords and not has_irrelevant_topics 
    
    def get_plant_info(self, plant_name: str) -> str:
        plant = MEDICINAL_PLANTS_DB.get(plant_name.lower())
        if plant:
            return f"""
Plant Name: {plant.name}
Scientific Name: {plant.scientific_name}
Region: {plant.region}

Traditional Uses:
{chr(10).join(f"- {use}" for use in plant.uses)}

Properties:
{chr(10).join(f"- {prop}" for prop in plant.properties)}

Preparation Methods:
{chr(10).join(f'''
Method: {prep['method']}
Ingredients: {', '.join(prep['ingredients'])}
Steps:
{chr(10).join(f"  {i+1}. {step}" for i, step in enumerate(prep['steps']))}
Recommended Dosage: {prep['dosage']}
''' for prep in plant.preparations)}

Precautions:
{chr(10).join(f"- {precaution}" for precaution in plant.precautions)}
"""
        return None

    def generate_response(self, messages: List[Message]) -> str:
        formatted_messages = [{"role": "system", "content": self.system_prompt}]
        
        # Check if the query is about a specific plant in our database
        if len(messages) > 0:
            last_message = messages[-1].content.lower()
            for plant_name in MEDICINAL_PLANTS_DB.keys():
                if plant_name in last_message:
                    plant_info = self.get_plant_info(plant_name)
                    if plant_info:
                        formatted_messages.append({
                            "role": "system",
                            "content": f"Here is detailed information about {plant_name}:\n{plant_info}"
                        })
        
        formatted_messages.extend([{"role": msg.role, "content": msg.content} for msg in messages])
        
        payload = {
            "model": "llama2",
            "messages": formatted_messages,
            "stream": False
        }
        
        try:
            response = requests.post(self.api_url, json=payload)
            response.raise_for_status()
            return response.json()["message"]["content"]
        except requests.exceptions.RequestException as e:
            return f"Error: {str(e)}"

def initialize_session_state():
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "bot" not in st.session_state:
        st.session_state.bot = RootaBot()

def display_plant_database():
    st.header("📚 Traditional Medicine Database")
    for plant_name, plant in MEDICINAL_PLANTS_DB.items():
        with st.expander(f"🌿 {plant.name} ({plant.scientific_name})"):
            st.write(f"**Region:** {plant.region}")
            
            st.subheader("Traditional Uses")
            for use in plant.uses:
                st.write(f"- {use}")
            
            st.subheader("Properties")
            for prop in plant.properties:
                st.write(f"- {prop}")
            
            st.subheader("Preparation Methods")
            for prep in plant.preparations:
                st.write(f"**{prep['method']}**")
                st.write("Ingredients:")
                for ingredient in prep['ingredients']:
                    st.write(f"- {ingredient}")
                st.write("Steps:")
                for i, step in enumerate(prep['steps'], 1):
                    st.write(f"{i}. {step}")
                st.write(f"**Dosage:** {prep['dosage']}")
            
            st.subheader("Precautions")
            for precaution in plant.precautions:
                st.write(f"- {precaution}")

def main():
    st.set_page_config(page_title="RootaBot", page_icon="🌿", layout="wide")
    
    st.title("🌿 RootaBot")
    st.markdown("""
    Welcome to RootaBot! Your guide to traditional medicine from Northeast India. 
    Explore our database of medicinal plants or ask questions about traditional remedies.
    
    _Note: This information is for educational purposes only. Always consult healthcare professionals for medical advice._
    """)
    
    # Initialize session state
    initialize_session_state()
    
    # Two-column layout
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("💬 Chat with RootaBot")
        # Display chat messages
        for message in st.session_state.messages:
            with st.chat_message(message.role):
                st.write(message.content)
        
        # Chat input
        if prompt := st.chat_input("Ask about traditional plants and medicines..."):
            # Add user message to chat
            st.session_state.messages.append(Message("user", prompt))
            with st.chat_message("user"):
                st.write(prompt)
                
            # Generate and display assistant response
            with st.chat_message("assistant"):
                with st.spinner("Researching traditional knowledge..."):
                    response = st.session_state.bot.generate_response(st.session_state.messages)
                    st.write(response)
            
            # Add assistant response to chat history
            st.session_state.messages.append(Message("assistant", response))
    
    with col2:
        display_plant_database()
    
    # Sidebar
    with st.sidebar:
        st.header("About RootaBot")
        st.markdown("""
        RootaBot combines traditional knowledge from Northeast India with modern accessibility.
        
        **Regions Covered:**
        * Assam
        * Meghalaya
        * Arunachal Pradesh
        * Nagaland
        * Manipur
        * Mizoram
        * Tripura
        * Sikkim
        
        **Important Notice:**
        The information provided is based on traditional knowledge and is for educational purposes only. 
        Always consult qualified healthcare professionals for medical advice.
        """)
        
        if st.button("Clear Chat"):
            st.session_state.messages = []
            st.rerun()

if __name__ == "__main__":
    main()