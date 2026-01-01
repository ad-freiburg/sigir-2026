"""
OpenReview client singleton management.
"""

import os
import openreview


# Global client instance (singleton)
_client_instance = None


def get_client() -> openreview.api.OpenReviewClient:
    """
    Get the singleton OpenReview client, creating it lazily on first use.

    Uses environment variables for configuration:
    - OPENREVIEW_API_URL
    - OPENREVIEW_USERNAME
    - OPENREVIEW_PASSWORD
    - OPENREVIEW_IMPERSONATE_GROUP (optional)
    """
    global _client_instance

    if _client_instance is None:
        # Create client from environment variables
        _client_instance = openreview.api.OpenReviewClient(
            baseurl=os.environ.get("OPENREVIEW_API_URL"),
            username=os.environ.get("OPENREVIEW_USERNAME"),
            password=os.environ.get("OPENREVIEW_PASSWORD"),
        )

        # Apply impersonation from environment if set
        impersonate = os.environ.get("OPENREVIEW_IMPERSONATE_GROUP")
        if impersonate:
            _client_instance.impersonate(impersonate)

    return _client_instance


def set_client_params(
    baseurl: str = None,
    username: str = None,
    password: str = None,
    impersonate_group: str = None,
) -> None:
    """
    Override client parameters from command-line arguments.
    Must be called before get_client() to have effect.
    """
    if baseurl:
        os.environ["OPENREVIEW_API_URL"] = baseurl
    if username:
        os.environ["OPENREVIEW_USERNAME"] = username
    if password:
        os.environ["OPENREVIEW_PASSWORD"] = password
    if impersonate_group:
        os.environ["OPENREVIEW_IMPERSONATE_GROUP"] = impersonate_group
