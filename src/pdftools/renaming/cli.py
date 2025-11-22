#!/usr/bin/env python3
"""
CLI Stub for Invoice Renaming
"""

import sys
from pdftools.cli.common import create_stub_message


def main():
    """Main entry point - shows 'coming soon' message"""
    print(create_stub_message(
        tool_name="pdfrename",
        feature_name="Invoice Renaming"
    ))
    sys.exit(1)


if __name__ == '__main__':
    main()
