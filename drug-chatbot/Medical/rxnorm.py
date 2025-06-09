import requests

def fetch_rxnorm_info(drug_name):
    url = f"https://rxnav.nlm.nih.gov/REST/rxcui.json?name={drug_name}"
    response = requests.get(url)

    if response.status_code == 200:
        try:
            rxcui = response.json()['idGroup']['rxnormId'][0]
            return {
                "answer": f"RxNorm ID for {drug_name} is {rxcui}.",
                "source": "RxNorm (NLM)",
                "source_url": f"https://rxnav.nlm.nih.gov/REST/rxcui/{rxcui}"
            }
        except:
            pass

    return {
        "answer": f"No RxNorm info found for {drug_name}.",
        "source": "RxNorm (NLM)",
        "source_url": "https://rxnav.nlm.nih.gov/"
}