#!/usr/bin/env python3
"""
CLI Stub for PDF Split
"""

import sys
from pdftools.cli.common import create_stub_message


def main():
    """Main entry point - shows 'coming soon' message"""
    print(create_stub_message(
        tool_name="pdfsplit",
        feature_name="PDF Split"
    ))
    sys.exit(1)


if __name__ == '__main__':
    main()
