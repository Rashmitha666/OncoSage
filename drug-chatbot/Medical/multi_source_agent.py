from wikipedia_loader import get_wikipedia_answer
from clinical_trials import get_clinical_trials
from dailymed import fetch_dailymed_info
from pubmed import search_pubmed
from cansar import fetch_cansar_info
from groq_agent import get_groq_answer  # New import

def answer_multi_source(topic, question):
    responses = []

    # Groq AI Answer (added as first source)
    groq_response = get_groq_answer(question)
    responses.append(groq_response)

    # Wikipedia Answer
    wiki = get_wikipedia_answer(topic, question)
    responses.append(wiki)

    # Clinical Trials Info
    trials = get_clinical_trials(topic)
    responses.append(trials)

    # DailyMed Drug Info (Only if topic looks like a drug)
    if len(topic.split()) <= 3:
        dailymed = fetch_dailymed_info(topic)
        responses.append(dailymed)

    # PubMed Search Result
    pubmed = search_pubmed(topic)
    responses.append(pubmed)

    # canSAR.ai Info (for drug or cancer biology targets)
    cansar = fetch_cansar_info(topic)
    responses.append(cansar)

    return {"answers": responses}
