import argparse
import requests
import sys
import json

api_url = "http://localhost"

def database_query(query):
    return "database query result"

def athena_query(prompt):

    url = f"http://localhost:3002/api/chat/completions"
    headers = {
        "Authorization": "Bearer sk-5f69dd653bb743e28f61f6ae8bb2d711",
        "Content-Type": "application/json"
    }
    data = {
        "model": "llama3.2:latest",
        "messages": [{"role": "user", "content": prompt}]
    }

    try:
        response = requests.post(url, headers=headers, json=data)
        return response.json()
    except requests.RequestException as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="LF CLI for API access")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Database command
    db_parser = subparsers.add_parser("database", help="Run a database query")
    db_parser.add_argument("query", help="The SQL query to run")

    # Athena command
    athena_parser = subparsers.add_parser("athena", help="Run an Athena query")
    athena_parser.add_argument("prompt", help="The prompt to run")

    args = parser.parse_args()

    if args.command == "database":
        result = database_query(args.query)
        print(json.dumps(result, indent=2))
    elif args.command == "athena":
        result = athena_query(args.prompt)
        print(result)
    elif not args.command:
        parser.print_help()
        sys.exit(1)
    else:
        print(f"Unknown command: {args.command}", file=sys.stderr)
        parser.print_help()
        sys.exit(1)

if __name__ == "__main__":
    main()