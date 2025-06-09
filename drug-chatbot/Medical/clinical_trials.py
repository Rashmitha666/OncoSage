import requests

def get_clinical_trials(drug):
    url = f"https://clinicaltrials.gov/api/query/full_studies?expr={drug}&min_rnk=1&max_rnk=3&fmt=json"
    res = requests.get(url)
    try:
        trial = res.json()['FullStudiesResponse']['FullStudies'][0]['Study']
        summary = trial['ProtocolSection']['DescriptionModule']['BriefSummary']
        return f"Clinical Trial Info: {summary}"
    except:
        return "No clinical trialinfofound."