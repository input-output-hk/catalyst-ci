import os
import sys
import requests
import json

def run_query(query, variables):
    headers = {"Authorization": f"Bearer {os.environ['GITHUB_TOKEN']}"}
    request = requests.post('https://api.github.com/graphql', json={'query': query, 'variables': variables}, headers=headers)
    if request.status_code == 200:
        return request.json()
    else:
        print(f"Query failed with status code: {request.status_code}")
        print(f"Response: {request.text}")
        raise Exception(f"Query failed with status code: {request.status_code}")

def get_pr_related_items(org_name, project_number, pr_number):
    query = """
    query($org: String!, $number: Int!, $prNumber: Int!) {
      organization(login: $org) {
        projectV2(number: $number) {
          items(first: 100) {
            nodes {
              id
              content {
                ... on PullRequest {
                  number
                  title
                  url
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
                }
              }
            }
          }
        }
      }
      repository(owner: $org, name: "catalyst-voices") {
        pullRequest(number: $prNumber) {
          number
          title
          url
        }
      }
    }
    """
    variables = {
        "org": org_name,
        "number": project_number,
        "prNumber": pr_number
    }
    result = run_query(query, variables)
    print(f"API Response: {json.dumps(result, indent=2)}")
    if 'data' not in result:
        print(f"Error in API response: {result.get('errors', 'Unknown error')}")
        return []

    pr_info = result['data']['repository']['pullRequest']
    print(f"Found PR: #{pr_info['number']} - {pr_info['title']} ({pr_info['url']})")

    items = result['data']['organization']['projectV2']['items']['nodes']
    pr_items = [item for item in items if item['content'] and isinstance(item['content'], dict) and item['content'].get('number') == pr_number]

    if not pr_items:
        print(f"PR #{pr_number} exists but is not linked to the project. Please add it to the project.")
    return pr_items

def validate_item(item):
    required_fields = ['Status', 'Area', 'Priority', 'Estimate', 'Iteration', 'Start', 'End']
    field_values = {}
    for field_value in item['fieldValues']['nodes']:
        field_name = field_value['field']['name']
        if 'text' in field_value:
            field_values[field_name] = field_value['text']
        elif 'date' in field_value:
            field_values[field_name] = field_value['date']
        elif 'name' in field_value:
            field_values[field_name] = field_value['name']

    empty_fields = [field for field in required_fields if not field_values.get(field)]
    return empty_fields


def main():
    org_name = os.environ['ORG_NAME']
    project_number = int(os.environ['PROJECT_NUMBER'])
    pr_number = int(os.environ['PR_NUMBER'])

    items = get_pr_related_items(org_name, project_number, pr_number)

    if not items:
        print(f"No project items found for PR #{pr_number}")
        sys.exit(0)

    validation_errors = []
    for item in items:
        empty_fields = validate_item(item)
        if empty_fields:
            error_message = f"PR #{pr_number}, Item ID: {item['id']}, Empty fields: {', '.join(empty_fields)}"
            validation_errors.append(error_message)
            print(f"Validation Error: {error_message}")  # Print to console

    if validation_errors:
        with open('.github/project_validation_results.txt', 'w') as f:
            for error in validation_errors:
                f.write(f"{error}\n")
        print("Validation failed. See results in .github/project_validation_results.txt")
        sys.exit(1)
    else:
        print(f"Validation passed for PR #{pr_number}")

if __name__ == "__main__":
    main()