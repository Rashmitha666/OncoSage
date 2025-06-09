import requests

def fetch_dailymed_info(drug_name):
    url = f"https://dailymed.nlm.nih.gov/dailymed/services/v2/spls.json?drug_name={drug_name}"
    res = requests.get(url)
    if res.status_code == 200:
        data = res.json()
        if "data" in data and len(data["data"]) > 0:
            spl = data["data"][0]
            set_id = spl.get('setid', '')
            return {
                "answer": f"NIH DailyMed found basic info for {drug_name}.",
                "source": "DailyMed (NIH)",
                "source_url": f"https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid={set_id}"
            }
    return {
        "answer": f"No detailed DailyMed info found for {drug_name}.",
        "source": "DailyMed (NIH)",
        "source_url": "https://dailymed.nlm.nih.gov/"
}