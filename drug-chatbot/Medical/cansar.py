def fetch_cansar_info(drug_name):
    """
    Returns a placeholder response with a link to canSAR.ai search results for the given drug name.
    canSAR does not provide a public API, so we simulate a static response.

    Args:
        drug_name (str): The name of the drug to look up.

    Returns:
        dict: A structured dictionary with answer, source name, and source URL.
    """
    return {
        "answer": f"canSAR.ai provides ligandability and drug target information for {drug_name}. Visit the link to explore more.",
        "source": "canSAR.ai (The Institute of Cancer Research)",
        "source_url": f"https://cansar.ai/drug-lookup?query={drug_name.replace(' ', '%20')}"
    }