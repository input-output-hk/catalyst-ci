#!/usr/bin/env python3

import python.cli as cli
import python.db_ops as db_ops
import argparse
import rich

def main():
    # Force color output in CI
    rich.reconfigure(color_system='256')
    
    parser = argparse.ArgumentParser(description='Standard Postgresql Documentation Processing.')
    parser.add_argument('container_name', help='Name of the container')
    parser.add_argument('--verbose', action='store_true', help='Enable verbose output')
    db_ops.add_args(parser)
    
    args = parser.parse_args()
    
    db = db_ops.DBOps(args)

    results = cli.Results("Generate Database Documentation")
    
    # Init the DB.
    res = db.init_database()   
    results.add(res)
    
    if res.ok():       
        db.start()
        res = db.wait_ready(timeout=10)
        results.add(res)
    
    if res.ok():
        res = db.setup()
        results.add(res)

    if res.ok():
        res = db.migrate_schema()
        results.add(res)

    
    results.print()


if __name__ == '__main__':
    main()
