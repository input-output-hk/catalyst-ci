import os
import sys
import requests
import json
from typing import Optional, List, Dict, Any

class ProjectFieldsValidator:
    def __init__(self, github_token: str):
        self.github_token = github_token
        self.headers = {
            "Authorization": f"Bearer {github_token}",
            "Accept": "application/vnd.github.v3+json"
        }
        self.required_fields = ['Status', 'Area', 'Priority', 'Estimate', 'Iteration', 'Start', 'End']

    def run_query(self, query: str, variables: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a GraphQL query against GitHub's API."""
        response = requests.post(
            'https://api.github.com/graphql',
            json={'query': query, 'variables': variables},
            headers=self.headers
        )

        if response.status_code != 200:
            print(f"Query failed with status code: {response.status_code}")
            print(f"Response: {response.text}")
            raise Exception(f"Query failed with status code: {response.status_code}")

        return response.json()

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

        variables = {
            "org": org_name,
            "repo": repo_name,
            "number": pr_number
        }

        result = self.run_query(query, variables)
        return result['data']['repository']['pullRequest']

    def assign_pr(self, org_name: str, repo_name: str, pr_number: int, assignee: str):
        """Assign PR to a user using REST API."""
        url = f"https://api.github.com/repos/{org_name}/{repo_name}/issues/{pr_number}/assignees"
        data = {"assignees": [assignee]}

        response = requests.post(url, json=data, headers=self.headers)

        if response.status_code == 201:
            print(f"✅ PR assigned to @{assignee}")
        else:
            print(f"❌ Failed to assign PR to @{assignee}")
            print(f"Response: {response.text}")

    def get_project_items(self, org_name: str, project_number: int) -> List[Dict[str, Any]]:
        """Fetch all items from the project."""
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

        all_items = []
        cursor = None
        page = 1
        max_pages = 100
        total_items = 0

        sys.stdout.write("\rFetching project items...")
        sys.stdout.flush()

        while page <= max_pages:
            variables = {
                "org": org_name,
                "projectNumber": project_number,
                "cursor": cursor
            }

            try:
                result = self.run_query(query, variables)
                project_data = result['data']['organization']['projectV2']['items']
                page_items = project_data['nodes']

                valid_items = [
                    item for item in page_items 
                    if item['content'] and isinstance(item['content'], dict)
                ]

                all_items.extend(valid_items)
                total_items += len(valid_items)

                sys.stdout.write(f"\rFetching project items... {total_items} found")
                sys.stdout.flush()

                page_info = project_data['pageInfo']
                if not page_info['hasNextPage']:
                    break

                cursor = page_info['endCursor']
                page += 1

            except Exception as e:
                print(f"\nError fetching page {page}: {str(e)}")
                break

        print("\n")
        return all_items

    def validate_item(self, item: Dict[str, Any]) -> List[str]:
        """Validate required fields for an item."""
        try:
            field_values = {}

            for field_value in item['fieldValues']['nodes']:
                if not isinstance(field_value, dict) or 'field' not in field_value:
                    continue
                try:
                    field_name = field_value['field']['name']
                except (KeyError, TypeError):
                    continue

                if 'text' in field_value:
                    field_values[field_name] = field_value['text']
                elif 'date' in field_value:
                    field_values[field_name] = field_value['date']
                elif 'name' in field_value:
                    field_values[field_name] = field_value['name']
                elif 'number' in field_value:
                    field_values[field_name] = str(field_value['number'])
                elif 'title' in field_value and field_name == 'Iteration':
                    field_values[field_name] = field_value['title']

            print("\nCurrent field values:")
            print("="*50)
            for field in self.required_fields:
                value = field_values.get(field, '❌ empty')
                print(f"  • {field}: {value}")

            return [field for field in self.required_fields if not field_values.get(field)]

        except Exception as e:
            print(f"\nError validating fields: {str(e)}")
            return self.required_fields

    def print_validation_results(self, empty_fields: List[str]) -> None:
        """Print validation results in a formatted way."""
        print("\n" + "="*50)
        print("Validation Results:")
        print("="*50)

        if not empty_fields:
            print("✅ All required fields are filled. Validation passed!")
        else:
            print("❌ Validation failed. The following fields need to be filled:")
            for field in empty_fields:
                print(f"  • {field}")
            print("\nPlease fill in these fields in the project board.")

        print("="*50)

def main():
    github_token = os.environ['GITHUB_TOKEN']
    github_repository = os.environ['GITHUB_REPOSITORY']
    pr_number = int(os.environ['GITHUB_EVENT_NUMBER'])
    project_number = int(os.environ['PROJECT_NUMBER'])

    org_name, repo_name = github_repository.split('/')

    print(f"\nValidating PR #{pr_number} in {github_repository}")
    print(f"Project number: {project_number}")
    print("="*50)

    validator = ProjectFieldsValidator(github_token)

    try:
        pr_details = validator.get_pr_details(org_name, repo_name, pr_number)
        author = pr_details['author']['login']
        assignees = [node['login'] for node in pr_details['assignees']['nodes']]

        if not assignees:
            print(f"\nAssigning PR to author @{author}")
            validator.assign_pr(org_name, repo_name, pr_number, author)


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

        validator.print_validation_results(list(validation_errors))

        if validation_errors:
            sys.exit(1)

    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()