#!/usr/bin/env python3
"""
CLI Stub for Thumbnail Generation
"""

import sys
from pdftools.cli.common import create_stub_message


def main():
    """Main entry point - shows 'coming soon' message"""
    print(create_stub_message(
        tool_name="pdfthumbnails",
        feature_name="Thumbnail Generation"
    ))
    sys.exit(1)


if __name__ == '__main__':
    main()
