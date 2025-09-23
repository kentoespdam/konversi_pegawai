from core.config import fetch_smartoffice


def fetch_organisasi():
    query = "SELECT * FROM organization"
    return fetch_smartoffice(query)
