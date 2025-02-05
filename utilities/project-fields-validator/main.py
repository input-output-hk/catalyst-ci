#!/usr/bin/env python3
import json as jsonlib
import os
import sys
import traceback
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from email.message import Message
from enum import Enum
from typing import Any, Dict, Iterable, List, NamedTuple, Optional, Set


class SafeOpener(urllib.request.OpenerDirector):
    """An opener with configurable set of handlers."""

    opener = None

    def __init__(self, handlers: Iterable = None):
        """
        Instantiate an OpenDirector with selected handlers.

        Args:
            handlers: an Iterable of handler classes
        """
        super().__init__()
        handlers = handlers or (
            urllib.request.UnknownHandler,
            urllib.request.HTTPDefaultErrorHandler,
            urllib.request.HTTPRedirectHandler,
            urllib.request.HTTPSHandler,
            urllib.request.HTTPErrorProcessor,
        )

        for handler_class in handlers:
            handler = handler_class()
            self.add_handler(handler)


class RequestException(Exception):
    """There was an ambiguous exception that occurred while handling your
    request.
    """

    def __init__(self, *args, **kwargs):
        """Initialize RequestException with `request` and `response` objects."""
        response = kwargs.pop("response", None)
        self.response = response
        self.request = kwargs.pop("request", None)
        if response is not None and not self.request and hasattr(response, "request"):
            self.request = self.response.request
        super().__init__(*args, **kwargs)


class Response(NamedTuple):
    """Container for HTTP response."""

    body: str
    headers: Message
    status: int
    url: str
    request: urllib.request.Request

    def json(self) -> Any:
        """
        Decode body's JSON.

        Returns:
            Pythonic representation of the JSON object
        """
        try:
            output = jsonlib.loads(self.body)
        except jsonlib.JSONDecodeError as e:
            raise RequestException(e, response=self)
        return output

    def raise_for_status(self):
        """Raise an exception if the response is not successful."""
        if self.status >= 400:
            raise RequestException(Exception("Status Error"), response=self)


# only used by `request`
opener = SafeOpener()


def request(
    method: str,
    url: str,
    json: dict = None,
    params: dict = None,
    headers: dict = None,
    data_as_json: bool = True,
) -> Response:
    """
    Perform HTTP request.

    Args:
        url: url to fetch
        json: dict of keys/values to be encoded and submitted
        params: dict of keys/values to be encoded in URL query string
        headers: optional dict of request headers
        method: HTTP method , such as GET or POST
        data_as_json: if True, data will be JSON-encoded

    Returns:
        A dict with headers, body, status code, and, if applicable, object
        rendered from JSON
    """
    try:
        method = method.upper()
        request_data = None
        headers = headers or {}
        json = json or {}
        params = params or {}
        headers = {"Accept": "application/json", **headers}
        httprequest = None
        response = None

        if method == "GET":
            params = {**params, **json}
            json = None

        if params:
            url += "?" + urllib.parse.urlencode(params, doseq=True, safe="/")

        if json:
            if data_as_json:
                request_data = jsonlib.dumps(json).encode()
                headers["Content-Type"] = "application/json; charset=UTF-8"
            else:
                request_data = urllib.parse.urlencode(json).encode()

        httprequest = urllib.request.Request(
            url,
            data=request_data,
            headers=headers,
            method=method,
        )

        with opener.open(
            httprequest,
        ) as httpresponse:
            response = Response(
                body=httpresponse.read().decode(
                    httpresponse.headers.get_content_charset("utf-8")
                ),
                headers=httpresponse.headers,
                status=httpresponse.status,
                url=httpresponse.url,
                request=httprequest,
            )
    except Exception as e:
        raise RequestException(e, request=httprequest, response=response)

    return response


class FieldType(Enum):
    TEXT = "text"
    DATE = "date"
    SELECT = "name"
    NUMBER = "number"
    ITERATION = "title"


@dataclass
class ProjectField:
    name: str
    value: Optional[str] = None
    field_type: Optional[FieldType] = None


class GitHubAPIError(Exception):
    """Exception for GitHub API errors"""

    def __init__(self, message: str, response_data: Optional[Dict] = None):
        super().__init__(message)
        self.response_data = response_data


class ProjectFieldsValidator:
    BASE_URL = "https://api.github.com"
    GRAPHQL_URL = f"{BASE_URL}/graphql"

    def __init__(self, github_token: str):
        if not github_token:
            raise ValueError("GitHub token is required but was empty")

        self.headers = {
            "Authorization": f"Bearer {github_token}",
            "Accept": "application/vnd.github.v3+json",
        }
        self.required_fields = [
            ProjectField("Status"),
            ProjectField("Area"),
            ProjectField("Priority"),
            ProjectField("Estimate"),
            ProjectField("Iteration"),
            ProjectField("Start"),
            ProjectField("End"),
        ]

    def _make_request(self, method: str, url: str, **kwargs) -> Dict[str, Any]:
        """Generic method to make HTTP requests with error handling"""
        try:
            response = request(method, url, headers=self.headers, **kwargs)
            response.raise_for_status()

            print(f"\nAPI Response Status: {response.status}")

            try:
                data = response.json()

                if "errors" in data:
                    error_messages = "; ".join(
                        error.get("message", "Unknown error")
                        for error in data["errors"]
                    )
                    raise GitHubAPIError(f"GraphQL API errors: {error_messages}", data)

                if "data" in data and data["data"] is None:
                    raise GitHubAPIError("API returned null data", data)

                return data
            except jsonlib.JSONDecodeError as e:
                raise GitHubAPIError(
                    f"Failed to parse API response: {str(e)} METHOD={method} URL={url} JSON={kwargs.get('json')}"
                )

        except RequestException as e:
            raise GitHubAPIError(
                f"GitHub API request failed: {str(e)} METHOD={method} URL={url} ARGS={kwargs}"
            )

    def run_query(self, query: str, variables: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a GraphQL query against GitHub's API."""
        return self._make_request(
            "POST", self.GRAPHQL_URL, json={"query": query, "variables": variables}
        )

    def get_pr_details(
        self, org_name: str, repo_name: str, pr_number: int
    ) -> Dict[str, Any]:
        """Get PR details including assignees."""
        query = """
        query($org: String!, $repo: String!, $number: Int!) {
          repository(owner: $org, name: $repo) {
            pullRequest(number: $number) {
              id
              author {
                login
              }
              assignees(first: 10) {
                nodes {
                  login
                }
              }
            }
          }
        }
        """

        print(f"\nFetching PR details for {org_name}/{repo_name}#{pr_number}")

        result = self.run_query(
            query, {"org": org_name, "repo": repo_name, "number": pr_number}
        )

        if not result.get("data"):
            raise GitHubAPIError("No data returned from API", result)
        if not result["data"].get("repository"):
            raise GitHubAPIError("Repository not found", result)
        if not result["data"]["repository"].get("pullRequest"):
            raise GitHubAPIError(f"PR #{pr_number} not found", result)

        return result["data"]["repository"]["pullRequest"]

    def assign_pr(
        self, org_name: str, repo_name: str, pr_number: int, assignee: str
    ) -> None:
        """Assign PR to a user using REST API."""
        url = (
            f"{self.BASE_URL}/repos/{org_name}/{repo_name}/issues/{pr_number}/assignees"
        )
        try:
            self._make_request("POST", url, json={"assignees": [assignee]})
            print(f"✅ PR assigned to @{assignee}")
        except GitHubAPIError as e:
            print(f"❌ Failed to assign PR to @{assignee}: {str(e)}")

    def get_project_items(
        self, org_name: str, project_number: int
    ) -> List[Dict[str, Any]]:
        """Fetch all items from the project with pagination."""
        query = """
        query($org: String!, $projectNumber: Int!, $cursor: String) {
          organization(login: $org) {
            projectV2(number: $projectNumber) {
              items(first: 100, after: $cursor) {
                pageInfo {
                  hasNextPage
                  endCursor
                }
                nodes {
                  id
                  content {
                    ... on PullRequest {
                      number
                      title
                      url
                      author {
                        login
                      }
                      repository {
                        name
                      }
                    }
                  }
                  fieldValues(first: 20) {
                    nodes {
                      ... on ProjectV2ItemFieldTextValue {
                        field {
                          ... on ProjectV2FieldCommon {
                            name
                          }
                        }
                        text
                      }
                      ... on ProjectV2ItemFieldDateValue {
                        field {
                          ... on ProjectV2FieldCommon {
                            name
                          }
                        }
                        date
                      }
                      ... on ProjectV2ItemFieldSingleSelectValue {
                        field {
                          ... on ProjectV2FieldCommon {
                            name
                          }
                        }
                        name
                      }
                      ... on ProjectV2ItemFieldNumberValue {
                        field {
                          ... on ProjectV2FieldCommon {
                            name
                          }
                        }
                        number
                      }
                      ... on ProjectV2ItemFieldIterationValue {
                        field {
                          ... on ProjectV2FieldCommon {
                            name
                          }
                        }
                        title
                        startDate
                        duration
                      }
                    }
                  }
                }
              }
            }
          }
        }
        """
        return self._paginate_items(query, org_name, project_number)

    def _paginate_items(
        self, query: str, org_name: str, project_number: int
    ) -> List[Dict[str, Any]]:
        """Handle pagination for project items."""
        all_items = []
        cursor = None
        total_items = 0

        while True:
            variables = {
                "org": org_name,
                "projectNumber": project_number,
                "cursor": cursor,
            }

            try:
                result = self.run_query(query, variables)
                if not result.get("data", {}).get("organization", {}).get("projectV2"):
                    raise GitHubAPIError("Could not access project data", result)

                project_data = result["data"]["organization"]["projectV2"]["items"]
                valid_items = [
                    item
                    for item in project_data["nodes"]
                    if item.get("content") and isinstance(item["content"], dict)
                ]

                all_items.extend(valid_items)
                total_items += len(valid_items)

                sys.stdout.write(f"\rFetching project items... {total_items} found")
                sys.stdout.flush()

                if not project_data["pageInfo"]["hasNextPage"]:
                    break

                cursor = project_data["pageInfo"]["endCursor"]

            except GitHubAPIError as e:
                print(f"\nError fetching project items: {str(e)}")
                if e.response_data:
                    print("\nAPI Response data:")
                    print(jsonlib.dumps(e.response_data, indent=2))
                raise

        print("\n")
        return all_items

    def validate_item(self, item: Dict[str, Any]) -> Set[str]:
        """Validate required fields for an item."""
        field_values = self._extract_field_values(item)

        print("\nCurrent field values:")
        print("=" * 50)
        for field in self.required_fields:
            value = field_values.get(field.name, "❌ empty")
            print(f"  • {field.name}: {value}")

        return {
            field.name
            for field in self.required_fields
            if field.name not in field_values
        }

    def _extract_field_values(self, item: Dict[str, Any]) -> Dict[str, str]:
        """Extract field values from item data."""
        field_values = {}

        for field_value in item["fieldValues"]["nodes"]:
            if not isinstance(field_value, dict) or "field" not in field_value:
                continue

            try:
                field_name = field_value["field"]["name"]
                for field_type in FieldType:
                    if field_type.value in field_value:
                        value = field_value[field_type.value]
                        if isinstance(value, (int, float)):
                            value = str(value)
                        field_values[field_name] = value
                        break
            except (KeyError, TypeError):
                continue

        return field_values

    @staticmethod
    def print_validation_results(empty_fields: Set[str]) -> None:
        """Print validation results in a formatted way."""
        print("\n" + "=" * 50)
        print("Validation Results:")
        print("=" * 50)

        if not empty_fields:
            print("✅ All required fields are filled. Validation passed!")
        else:
            print("❌ Validation failed. The following fields need to be filled:")
            for field in sorted(empty_fields):
                print(f"  • {field}")
            print("\nPlease fill in these fields in the project board.")

        print("=" * 50)


def clean_env_var(var: str) -> str:
    """Clean environment variable by removing quotes and extra whitespace"""
    if var is None:
        return None
    return var.strip().strip("\"'")


def main():
    try:
        env_vars = {
            "GITHUB_TOKEN": clean_env_var(os.environ.get("GITHUB_TOKEN")),
            "GITHUB_REPOSITORY": clean_env_var(os.environ.get("GITHUB_REPOSITORY")),
            "GITHUB_EVENT_NUMBER": clean_env_var(os.environ.get("GITHUB_EVENT_NUMBER")),
            "PROJECT_NUMBER": clean_env_var(os.environ.get("PROJECT_NUMBER")),
        }

        debug_vars = env_vars.copy()
        debug_vars["GITHUB_TOKEN"] = "[REDACTED]" if env_vars["GITHUB_TOKEN"] else None
        print("\nEnvironment variables:")
        for key, value in debug_vars.items():
            print(f"{key}: {value}")

        missing_vars = [k for k, v in env_vars.items() if not v]
        if missing_vars:
            raise ValueError(
                f"Missing required environment variables: {', '.join(missing_vars)}"
            )

        try:
            pr_number = int(env_vars["GITHUB_EVENT_NUMBER"])
            project_number = int(
                env_vars.get("PROJECT_NUMBER", "102")
            )  # Default to 102 if not set
        except ValueError as e:
            raise ValueError(
                f"Invalid numeric value in environment variables: {str(e)}"
            )

        github_repository = env_vars["GITHUB_REPOSITORY"]
        try:
            org_name, repo_name = github_repository.split("/")
        except ValueError:
            raise ValueError(
                f"Invalid repository format: {github_repository}. Expected format: owner/repo"
            )

        print(f"\nValidating PR #{pr_number} in {github_repository}")
        print(f"Project number: {project_number}")
        print("=" * 50)

        validator = ProjectFieldsValidator(env_vars["GITHUB_TOKEN"])

        try:
            pr_details = validator.get_pr_details(org_name, repo_name, pr_number)
            author = pr_details["author"]["login"]
            assignees = [node["login"] for node in pr_details["assignees"]["nodes"]]

            if not assignees:
                print(f"\nAssigning PR to author @{author}")
                validator.assign_pr(org_name, repo_name, pr_number, author)

            project_items = validator.get_project_items(org_name, project_number)
            pr_items = [
                item
                for item in project_items
                if (
                    item["content"].get("number") == pr_number
                    and item["content"].get("repository", {}).get("name") == repo_name
                )
            ]

            if not pr_items:
                print(
                    f"\nWarning: PR #{pr_number} is not linked to project #{project_number}"
                )
                print("Please add it to the project using the following steps:")
                print("1. Go to the project board")
                print("2. Click '+ Add items'")
                print("3. Search for this PR")
                print("4. Click 'Add selected items'")
                sys.exit(0)

            validation_errors = set()
            for item in pr_items:
                empty_fields = validator.validate_item(item)
                validation_errors.update(empty_fields)

            validator.print_validation_results(validation_errors)

            if validation_errors:
                sys.exit(1)

        except GitHubAPIError as e:
            print(f"\nError accessing GitHub API: {str(e)}")
            if e.response_data:
                print("\nAPI Response data:")
                print(jsonlib.dumps(e.response_data, indent=2))
            sys.exit(1)

    except ValueError as e:
        print(f"Configuration error: {str(e)}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {str(e)}")
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
