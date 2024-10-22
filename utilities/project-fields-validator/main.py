import os
import sys
from dataclasses import dataclass
from typing import Optional, List, Dict, Any, Set
from enum import Enum
import requests
from requests.exceptions import RequestException

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
    pass

class ProjectFieldsValidator:
    BASE_URL = "https://api.github.com"
    GRAPHQL_URL = f"{BASE_URL}/graphql"

    def __init__(self, github_token: str):
        self.headers = {
            "Authorization": f"Bearer {github_token}",
            "Accept": "application/vnd.github.v3+json"
        }
        self.required_fields = [
            ProjectField("Status"),
            ProjectField("Area"),
            ProjectField("Priority"),
            ProjectField("Estimate"),
            ProjectField("Iteration"),
            ProjectField("Start"),
            ProjectField("End")
        ]

    def _make_request(self, method: str, url: str, **kwargs) -> Dict[str, Any]:
        """Generic method to make HTTP requests with error handling"""
        try:
            response = requests.request(method, url, headers=self.headers, **kwargs)
            response.raise_for_status()
            return response.json()
        except RequestException as e:
            raise GitHubAPIError(f"GitHub API request failed: {str(e)}") from e

    def run_query(self, query: str, variables: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a GraphQL query against GitHub's API."""
        return self._make_request(
            "POST",
            self.GRAPHQL_URL,
            json={'query': query, 'variables': variables}
        )

    def get_pr_details(self, org_name: str, repo_name: str, pr_number: int) -> Dict[str, Any]:
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
        result = self.run_query(query, {"org": org_name, "repo": repo_name, "number": pr_number})
        return result['data']['repository']['pullRequest']

    def assign_pr(self, org_name: str, repo_name: str, pr_number: int, assignee: str) -> None:
        """Assign PR to a user using REST API."""
        url = f"{self.BASE_URL}/repos/{org_name}/{repo_name}/issues/{pr_number}/assignees"
        try:
            self._make_request("POST", url, json={"assignees": [assignee]})
            print(f"✅ PR assigned to @{assignee}")
        except GitHubAPIError as e:
            print(f"❌ Failed to assign PR to @{assignee}: {str(e)}")

    def get_project_items(self, org_name: str, project_number: int) -> List[Dict[str, Any]]:
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

    def _paginate_items(self, query: str, org_name: str, project_number: int) -> List[Dict[str, Any]]:
        """Handle pagination for project items."""
        all_items = []
        cursor = None
        total_items = 0

        while True:
            variables = {
                "org": org_name,
                "projectNumber": project_number,
                "cursor": cursor
            }

            result = self.run_query(query, variables)
            project_data = result['data']['organization']['projectV2']['items']
            valid_items = [
                item for item in project_data['nodes']
                if item.get('content') and isinstance(item['content'], dict)
            ]

            all_items.extend(valid_items)
            total_items += len(valid_items)

            sys.stdout.write(f"\rFetching project items... {total_items} found")
            sys.stdout.flush()

            if not project_data['pageInfo']['hasNextPage']:
                break

            cursor = project_data['pageInfo']['endCursor']

        print("\n")
        return all_items

    def validate_item(self, item: Dict[str, Any]) -> Set[str]:
        """Validate required fields for an item."""
        field_values = self._extract_field_values(item)

        print("\nCurrent field values:")
        print("="*50)
        for field in self.required_fields:
            value = field_values.get(field.name, '❌ empty')
            print(f"  • {field.name}: {value}")

        return {field.name for field in self.required_fields if field.name not in field_values}

    def _extract_field_values(self, item: Dict[str, Any]) -> Dict[str, str]:
        """Extract field values from item data."""
        field_values = {}

        for field_value in item['fieldValues']['nodes']:
            if not isinstance(field_value, dict) or 'field' not in field_value:
                continue

            try:
                field_name = field_value['field']['name']
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
        print("\n" + "="*50)
        print("Validation Results:")
        print("="*50)

        if not empty_fields:
            print("✅ All required fields are filled. Validation passed!")
        else:
            print("❌ Validation failed. The following fields need to be filled:")
            for field in sorted(empty_fields):
                print(f"  • {field}")
            print("\nPlease fill in these fields in the project board.")

        print("="*50)

def main():
    try:
        env_vars = {
            'GITHUB_TOKEN': os.environ.get('GITHUB_TOKEN'),
            'GITHUB_REPOSITORY': os.environ.get('GITHUB_REPOSITORY'),
            'GITHUB_EVENT_NUMBER': os.environ.get('GITHUB_EVENT_NUMBER'),
            'PROJECT_NUMBER': os.environ.get('PROJECT_NUMBER')
        }

        # Validate environment variables
        missing_vars = [k for k, v in env_vars.items() if not v]
        if missing_vars:
            raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")

        github_repository = env_vars['GITHUB_REPOSITORY']
        pr_number = int(env_vars['GITHUB_EVENT_NUMBER'])
        project_number = int(env_vars['PROJECT_NUMBER'])
        org_name, repo_name = github_repository.split('/')

        print(f"\nValidating PR #{pr_number} in {github_repository}")
        print(f"Project number: {project_number}")
        print("="*50)

        validator = ProjectFieldsValidator(env_vars['GITHUB_TOKEN'])

        pr_details = validator.get_pr_details(org_name, repo_name, pr_number)
        author = pr_details['author']['login']
        assignees = [node['login'] for node in pr_details['assignees']['nodes']]

        if not assignees:
            print(f"\nAssigning PR to author @{author}")
            validator.assign_pr(org_name, repo_name, pr_number, author)

        # Get and validate project items
        project_items = validator.get_project_items(org_name, project_number)
        pr_items = [
            item for item in project_items
            if (item['content'].get('number') == pr_number and
                item['content'].get('repository', {}).get('name') == repo_name)
        ]

        if not pr_items:
            print(f"\nWarning: PR #{pr_number} is not linked to project #{project_number}")
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

    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()