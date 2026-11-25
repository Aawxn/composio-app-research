#!/usr/bin/env python3
"""
Composio App Research Pipeline — CLI Entrypoint

Usage:
  python run_pipeline.py --batch 10              # Test: research first 10 apps
  python run_pipeline.py --all                   # Research all 100 apps
  python run_pipeline.py --app "Attio"           # Research single app
  python run_pipeline.py --verify                # Run Pass 2 verification
  python run_pipeline.py --audit-template        # Generate human audit template
  python run_pipeline.py --patterns              # Compute patterns
  python run_pipeline.py --build-site            # Build site/ from data/
  python run_pipeline.py --all --verify --patterns --build-site  # Full pipeline
"""

import argparse
import asyncio
import sys
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()


def main():
    parser = argparse.ArgumentParser(
        description="Composio App Research Pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--batch",
        type=int,
        metavar="N",
        help="Research first N apps (test mode, e.g. --batch 10)",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Research all 100 apps",
    )
    parser.add_argument(
        "--app",
        type=str,
        metavar="NAME",
        help="Research a single app by name (e.g. --app 'Attio')",
    )
    parser.add_argument(
        "--verify",
        action="store_true",
        help="Run Pass 2 automated verification",
    )
    parser.add_argument(
        "--audit-template",
        action="store_true",
        help="Generate Pass 3 human audit template",
    )
    parser.add_argument(
        "--patterns",
        action="store_true",
        help="Compute pattern analysis and clustering",
    )
    parser.add_argument(
        "--build-site",
        action="store_true",
        help="Build site/ from data/ (index.html, data.json, llms.txt)",
    )
    parser.add_argument(
        "--no-resume",
        action="store_true",
        help="Do not resume from checkpoint; overwrite previous runs",
    )

    args = parser.parse_args()

    if not any([
        args.batch,
        args.all,
        args.app,
        args.verify,
        args.audit_template,
        args.patterns,
        args.build_site,
    ]):
        parser.print_help()
        sys.exit(1)

    # Pass 1: Research
    if args.batch or args.all or args.app:
        from agent.researcher import run_pass1

        asyncio.run(
            run_pass1(
                batch=args.batch,
                single_app=args.app,
                run_all=args.all,
                resume=not args.no_resume,
            )
        )

    # Pass 2: Verify
    if args.verify:
        from agent.verifier import run_pass2

        asyncio.run(run_pass2())

    # Pass 3: Human audit template
    if args.audit_template:
        from agent.human_audit import generate_audit_template

        generate_audit_template()

    # Patterns
    if args.patterns:
        from agent.patterns import compute_and_save_patterns

        compute_and_save_patterns()

    # Build site
    if args.build_site:
        from build_site import build_site

        build_site()

    print("\n✅ Execution completed successfully.")


if __name__ == "__main__":
    main()
