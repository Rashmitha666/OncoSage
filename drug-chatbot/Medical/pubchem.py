import requests

def fetch_pubchem_info(drug_name):
    url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{drug_name}/property/MolecularFormula,MolecularWeight,CanonicalSMILES,InChIKey/JSON"
    response = requests.get(url)

    if response.status_code == 200:
        try:
            props = response.json()['PropertyTable']['Properties'][0]
            return {
                "answer": f"PubChem found properties for {drug_name}: Molecular Formula: {props['MolecularFormula']}, Molecular Weight: {props['MolecularWeight']}",
                "source": "PubChem",
                "source_url": f"https://pubchem.ncbi.nlm.nih.gov/compound/{drug_name.replace(' ', '%20')}"
            }
        except:
            pass

    return {
        "answer": f"No PubChem data found for {drug_name}.",
        "source": "PubChem",
        "source_url": "https://pubchem.ncbi.nlm.nih.gov/"
}
