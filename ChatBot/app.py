import streamlit as st
import pandas as pd
import urllib.parse

# Load dataset
@st.cache_data
def load_data():
    return pd.read_csv("docs/drug_knowledge.csv")

# Generate Wikipedia and Google Scholar links
def generate_links(drug_name):
    wiki = f"https://en.wikipedia.org/wiki/{urllib.parse.quote(drug_name)}"
    scholar = f"https://scholar.google.com/scholar?q={urllib.parse.quote(drug_name)}"
    drugbank = f"https://go.drugbank.com/unearth/q?searcher=drugs&query={urllib.parse.quote(drug_name)}"
    return wiki, scholar, drugbank

# Search function
def search_answer(query, df):
    query_lower = query.lower()
    for _, row in df.iterrows():
        drug = str(row['Drug']).lower()
        mutation = str(row['Mutation']).lower()

        if drug in query_lower or mutation in query_lower:
            wiki, scholar, drugbank = generate_links(row['Drug'])
            return (
                f"💊 **{row['Drug']}** is recommended for mutation **{row['Mutation']}**.\n\n"
                f"🧠 **Mechanism**: {row['Mechanism']}\n\n"
                f"⚠️ **Side Effects**: {row['SideEffects']}\n\n"
                f"🔗 **Related Links:**\n"
                f"- [Wikipedia]({wiki})\n"
                f"- [Google Scholar]({scholar})\n"
                f"- [DrugBank]({drugbank})"
            )
    return "❌ Sorry, no matching drug or mutation found in the dataset."

# Streamlit UI
st.title("🧬 AI Agent ChatBot for Drug Discovery")
st.markdown("Ask a question like: *Why is Imatinib recommended?* or *What are the side effects of Trametinib?*")

df = load_data()

user_query = st.text_input("💬 Ask about any drug or mutation:")

if user_query:
    response = search_answer(user_query, df)
    st.markdown(response)
