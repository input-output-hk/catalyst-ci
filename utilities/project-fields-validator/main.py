import os
import requests
import json

def run_query(query, variables):
    headers = {"Authorization": f"Bearer {os.environ['GITHUB_TOKEN']}"}
    request = requests.post('https://api.github.com/graphql', json={'query': query, 'variables': variables}, headers=headers)
    if request.status_code == 200:
        return request.json()
    else:
        raise Exception(f"Query failed with status code: {request.status_code}. {request.json()}")

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
                }
              }
              fieldValues(first: 20) {
                nodes {
                  ... on ProjectV2ItemFieldTextValue {
                    field { name }
                    text
                  }
                  ... on ProjectV2ItemFieldDateValue {
                    field { name }
                    date
                  }
                  ... on ProjectV2ItemFieldSingleSelectValue {
                    field { name }
                    name
                  }
                }
              }
            }
          }
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
    items = result['data']['organization']['projectV2']['items']['nodes']
    return [item for item in items if item['content'] and item['content'].get('number') == pr_number]

def validate_item(item):
    required_fields = ['Status', 'Area', 'Priority', 'Estimate', 'Iteration', 'Start', 'End']
    field_values = {fv['field']['name']: fv.get('text') or fv.get('date') or fv.get('name')
                    for fv in item['fieldValues']['nodes']}
    empty_fields = [field for field in required_fields if not field_values.get(field)]
    return empty_fields

def main():
    org_name = os.environ['ORG_NAME']
    project_number = int(os.environ['PROJECT_NUMBER'])
    pr_number = int(os.environ['PR_NUMBER'])

    items = get_pr_related_items(org_name, project_number, pr_number)

    validation_errors = []
    for item in items:
        empty_fields = validate_item(item)
        if empty_fields:
            validation_errors.append(f"Item ID: {item['id']}, Empty fields: {', '.join(empty_fields)}")

    if validation_errors:
        with open('.github/project_validation_results.txt', 'w') as f:
            for error in validation_errors:
                f.write(f"{error}\n")

if __name__ == "__main__":
    main()