import argparse
import requests
import sys
import json

def database_query(query):
    return "database query result"

def main():
    parser = argparse.ArgumentParser(description="LF CLI for API access")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Database command
    db_parser = subparsers.add_parser("database", help="Run a database query")
    db_parser.add_argument("query", help="The SQL query to run")

    args = parser.parse_args()

    if args.command == "database":
        result = database_query(args.query)
        print(json.dumps(result, indent=2))
    elif not args.command:
        parser.print_help()
        sys.exit(1)
    else:
        print(f"Unknown command: {args.command}", file=sys.stderr)
        parser.print_help()
        sys.exit(1)

if __name__ == "__main__":
    main()