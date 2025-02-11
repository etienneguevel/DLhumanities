import os

import requests
from urllib.parse import urlencode
from xml.etree import ElementTree as ET


def build_cql_query(**kwargs):
    """
    Function to build a CQL query from a set of key-value pairs.
    Args:
        **kwargs: Key-value pairs to build the query, the key being the field and the value the search term.
    Returns:
        A string representing the CQL query.
    """
    # Build the query conditions dynamically
    return " and ".join(f"dc.{key} all '{value}'" for key, value in kwargs.items() if value)


def test_query_response(url, params):
    """
    Function to test a query and return the response if successful.
    Args:
        url: The base URL to send the query to.
        params: A dictionary of query parameters.
    Returns:
        The response object if the query was successful, None otherwise.
    """
    # Test the query by sending it to the base URL
    try:
        print(f"Generated URL: {url}?{urlencode(params)}")
        print("Testing the query...")
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()  # Raise HTTPError for bad HTTP responses (4xx or 5xx)
        print("Query successful. Response received.")
        return response
    
    except requests.exceptions.RequestException as e:
        # Handle HTTP-related errors (connection issues, timeout, etc.)
        print(f"Error during HTTP request: {e}")
        return None


def download_file(url, download_dir):
    """
    Function to download a file from a URL and save it to a directory.
    """
    try:
        file_name = os.path.basename(url)
        file_path = os.path.join(download_dir, file_name)
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        with open(file_path, "wb") as file:
            file.write(response.content)

        print(f"File saved: {file_path}")

    except requests.exceptions.RequestException as e:
        print(f"Error downloading {url}: {e}")


def download_documents_and_fulltext(cql_query, max_records=100):
    """
    Function to download results and their content from a Gallica SRU query.
    """
    # Ensure the query is not empty
    if not cql_query.strip():
        print("Error: The 'query' parameter is empty. The query cannot be sent.")
        return None

    params = {
        "version": "1.2",
        "operation": "searchRetrieve",
        "query": cql_query,
        "startRecord": 1,
        "maximumRecords": max_records
    }

    # Test the query
    response = test_query_response("https://gallica.bnf.fr/SRU", params)
    if not response:
        return None

    # Check if the response contains results
    try:
        xml_root = ET.fromstring(response.content)
        records = xml_root.findall(".//{http://www.loc.gov/zing/srw/}record")
        print(f"Number of records found: {len(records)}")
        if not records:
            print("No results found for this query.")
            return
    except ET.ParseError:
        # Handle XML parsing errors
        print("XML parsing error in the response.")
        return

    # Create a download directory
    download_dir = "downloads"
    os.makedirs(download_dir, exist_ok=True)

    # Download metadata and associated documents
    for i, record in enumerate(records, start=1):
        print(f"Processing record {i}/{len(records)}...")  # Log current record
        metadata = record.find(".//{http://www.loc.gov/zing/srw/}recordData")
        if metadata is not None:
            identifiers = metadata.findall(".//{http://purl.org/dc/elements/1.1/}identifier")
            print(f"Identifiers found: {len(identifiers)}")  # Log identifiers count
            for identifier in identifiers:
                url = identifier.text
                print(f"Downloading: {url}")
                download_file(url, download_dir)
        else:
            print("No metadata found for this record.")

