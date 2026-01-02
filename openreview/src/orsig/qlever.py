"""
QLever API functions for SPARQL query retrieval and execution.
"""

import os
from typing import Any

import requests


def get_sparql_query(short_hash: str) -> str:
    """
    Get a SPARQL query from the QLever link API using a short hash (e.g., 'PZGwbS').
    """
    link_api = os.environ.get("QLEVER_LINK_API", "https://qlever.dev/api/link/")
    url = f"{link_api}{short_hash}/"

    response = requests.get(url)
    response.raise_for_status()

    data = response.json()
    return data["content"]


def issue_sparql_query(query: str) -> dict[str, Any]:
    """
    Execute a SPARQL query against the QLever query API.
    """
    query_api = os.environ.get("QLEVER_QUERY_API", "")

    # Add http:// if no protocol specified
    if query_api and not query_api.startswith(("http://", "https://")):
        query_api = f"http://{query_api}"

    response = requests.get(
        query_api,
        params={"query": query},
        headers={"Accept": "application/sparql-results+json"},
    )
    response.raise_for_status()

    return response.json()


def _convert_email_profile_to_email(profile_id: str) -> str:
    """
    Convert email-as-profile IDs like ~ida_mele_at_iasi_cnr_it to email addresses.
    Returns the original profile_id if it doesn't match the pattern.
    """
    if "_at_" not in profile_id:
        return profile_id

    # Remove ~ prefix if present
    pid = profile_id.lstrip("~")

    # Split on _at_ to get local part and domain
    parts = pid.split("_at_", 1)
    if len(parts) != 2:
        return profile_id

    local_part, domain = parts
    # Replace underscores with dots in domain (e.g., iasi_cnr_it -> iasi.cnr.it)
    domain = domain.replace("_", ".")

    return f"{local_part}@{domain}"


def recipients_from_query(hash_or_url: str) -> list[str]:
    """
    Get OpenReview profile IDs from a SPARQL query result. Finds the first
    column where all values are profile IRIs, extracts the profile IDs, and
    returns them as a list. Accepts a short hash or full URL.
    Converts email-as-profile IDs to actual email addresses.
    """
    short_hash = hash_or_url.rstrip("/").split("/")[-1]
    query = get_sparql_query(short_hash)
    result = issue_sparql_query(query)

    bindings = result.get("results", {}).get("bindings", [])
    if not bindings:
        raise ValueError("Query returned no results")

    variables = result.get("head", {}).get("vars", [])
    profile_prefix = "https://openreview.net/profile?id="

    # Find first column where all values are profile IRIs
    for var in variables:
        profile_ids = []
        all_match = True
        for row in bindings:
            cell = row.get(var, {})
            if cell.get("type") != "uri":
                all_match = False
                break
            value = cell.get("value", "")
            if not value.startswith(profile_prefix):
                all_match = False
                break
            profile_id = value[len(profile_prefix) :]
            # Convert email-as-profile to actual email
            profile_ids.append(_convert_email_profile_to_email(profile_id))

        if all_match and profile_ids:
            return profile_ids

    raise ValueError("No column found with profile IRIs")
