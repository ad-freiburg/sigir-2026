"""
RDF helper functions for OpenReview data export.
"""

import os
from typing import List, Tuple, Any, Dict


def get_rdf_base() -> str:
    """
    Get the RDF base URL from environment variable or .env file.
    """
    return os.environ.get('RDF_BASE', 'http://example.org/')


def format_rdf_prefixes(additional_prefixes: List[Tuple[str, str]] = None) -> str:
    """
    Format RDF prefix declarations including @base and any additional prefixes.
    """
    rdf_base = get_rdf_base()
    lines = [f'@base <{rdf_base}> .']

    if additional_prefixes:
        for prefix_name, prefix_uri in additional_prefixes:
            lines.append(f'@prefix {prefix_name}: <{prefix_uri}> .')

    return '\n'.join(lines)


def escape_rdf_literal(value: str) -> str:
    """
    Escape a string value for use in RDF literals.
    """
    # Escape backslashes first, then quotes and newlines
    value = value.replace('\\', '\\\\')
    value = value.replace('"', '\\"')
    value = value.replace('\n', '\\n')
    value = value.replace('\r', '\\r')
    value = value.replace('\t', '\\t')
    return value


def format_rdf_triple(subject: str, predicate: str, object_value: str, is_literal: bool = True) -> str:
    """
    Format an RDF triple.
    """
    if is_literal:
        escaped_value = escape_rdf_literal(object_value)
        return f'{subject} {predicate} "{escaped_value}" .'
    else:
        return f'{subject} {predicate} {object_value} .'


class Rdf:
    """
    Class for generating RDF terms and managing RDF namespaces.
    """

    def __init__(self):
        """
        Initialize with the RDF base URL.
        """
        self.base = get_rdf_base()
        self.submission_prefix = f"{self.base}submission/"
        self.person_prefix = f"{self.base}person/"

    def submissionIri(self, submission_id: str) -> str:
        """
        Create a submission IRI from an OpenReview submission ID.
        """
        return f"submission:{submission_id}"

    def personIri(self, person_id: str) -> str:
        """
        Create a person IRI from a person ID.
        """
        # Remove special characters and create a clean ID
        # Replace ~ with empty string, spaces with underscores
        clean_id = person_id.replace('~', '').replace(' ', '_')
        # For emails, replace @ and . with underscores
        clean_id = clean_id.replace('@', '_at_').replace('.', '_')
        return f"person:{clean_id}"

    def literal(self, value: str) -> str:
        """
        Format a string as an RDF literal.
        """
        escaped = escape_rdf_literal(value)
        return f'"{escaped}"'

    def literalFromJson(self, obj: Dict[str, Any], path: str) -> str:
        """
        Get a value from a JSON object via a path and return as RDF literal.
        """
        current = obj
        for key in path.split('.'):
            if isinstance(current, dict) and key in current:
                current = current.get(key)
            else:
                return ":novalue"

        # If we got a value, return it as a literal
        if current and isinstance(current, str):
            return self.literal(current)
        elif current is not None and not isinstance(current, (dict, list)):
            # Handle other types (numbers, booleans)
            return self.literal(str(current))
        else:
            return ":novalue"

    def iriFromJson(self, obj: Dict[str, Any], path: str, prefix: str) -> str:
        """
        Get a value from a JSON object via a path and return as prefixed IRI.
        """
        current = obj
        for key in path.split('.'):
            if isinstance(current, dict) and key in current:
                current = current.get(key)
            else:
                return ":novalue"

        # If we got a value, return it as a prefixed IRI
        if current and isinstance(current, str):
            # Use special handling for person IRIs
            if prefix == 'person':
                # Remove special characters and create a clean ID
                clean_id = current.replace('~', '').replace(' ', '_')
                # For emails, replace @ and . with underscores
                clean_id = clean_id.replace('@', '_at_').replace('.', '_')
            else:
                # Basic cleaning for other prefixes
                clean_id = current.replace(' ', '_')
            return f"{prefix}:{clean_id}"
        elif current is not None and not isinstance(current, (dict, list)):
            # Handle other types (numbers, booleans)
            return f"{prefix}:{str(current)}"
        else:
            return ":novalue"

    def urlFromJson(self, obj: Dict[str, Any], path: str, fallback: str) -> str:
        """
        Get a URL from a JSON object via a path and return as full IRI with angle brackets.
        """
        current = obj
        for key in path.split('.'):
            if isinstance(current, dict) and key in current:
                current = current.get(key)
            else:
                return fallback

        # If we got a URL, return it as a full IRI
        if current and isinstance(current, str):
            return f"<{current}>"
        else:
            return fallback

    def valuesFromJson(self, obj: Dict[str, Any], path: str) -> List[Any]:
        """
        Get an array of values from a JSON object via a path.
        """
        current = obj
        for key in path.split('.'):
            if isinstance(current, dict) and key in current:
                current = current.get(key)
            else:
                return []

        # If we got a list, return it; otherwise return empty list
        if isinstance(current, list):
            return current
        else:
            return []

    def get_prefixes(self) -> List[Tuple[str, str]]:
        """
        Get the list of prefixes used by this Rdf instance.
        """
        return [
            ('submission', self.submission_prefix),
            ('person', self.person_prefix),
            ('rdfs', 'http://www.w3.org/2000/01/rdf-schema#'),
        ]