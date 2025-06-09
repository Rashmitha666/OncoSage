import requests

def search_pubmed(topic):
    base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
    search_url = f"{base_url}esearch.fcgi?db=pubmed&term={topic}&retmode=json&retmax=1"
    
    search_res = requests.get(search_url).json()
    ids = search_res.get('esearchresult', {}).get('idlist', [])
    
    if ids:
        pubmed_id = ids[0]
        summary_url = f"{base_url}esummary.fcgi?db=pubmed&id={pubmed_id}&retmode=json"
        summary_res = requests.get(summary_url).json()
        result = summary_res.get('result', {}).get(pubmed_id, {})
        title = result.get('title', 'No title found')
        
        return {
            "answer": f"PubMed article found: {title}",
            "source": "PubMed (NCBI)",
            "source_url": f"https://pubmed.ncbi.nlm.nih.gov/{pubmed_id}/"
        }

    return {
        "answer": f"No PubMed articles found for {topic}.",
        "source": "PubMed (NCBI)",
        "source_url": "https://pubmed.ncbi.nlm.nih.gov/"
}
