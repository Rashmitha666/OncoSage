import requests

def fetch_openfda_label(drug_name):
    url = f"https://api.fda.gov/drug/label.json?search=openfda.generic_name:{drug_name}&limit=1"
    response = requests.get(url)

    if response.status_code == 200:
        try:
            data = response.json()['results'][0]
            summary = data.get('description', ["No description available."])[0]
            return {
                "answer": f"OpenFDA label: {summary[:300]}...",
                "source": "OpenFDA",
                "source_url": "https://open.fda.gov/apis/drug/label/"
            }
        except:
            pass

    return {
        "answer": f"No OpenFDA label info found for {drug_name}.",
        "source": "OpenFDA",
        "source_url": "https://open.fda.gov/"
}
