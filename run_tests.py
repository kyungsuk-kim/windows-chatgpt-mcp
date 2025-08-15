#!/usr/bin/env python3
"""
Test runner script for Windows ChatGPT MCP.

This script runs the complete test suite with coverage reporting and
provides options for different test configurations.
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path


def run_command(command, cwd=None):
    """Run a command and return the result."""
    print(f"Running: {' '.join(command)}")
    result = subprocess.run(command, cwd=cwd, capture_output=True, text=True)
    
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)
    
    return result.returncode == 0


def main():
    """Main test runner function."""
    parser = argparse.ArgumentParser(description="Run Windows ChatGPT MCP tests")
    parser.add_argument("--unit", action="store_true", help="Run only unit tests")
    parser.add_argument("--integration", action="store_true", help="Run only integration tests")
    parser.add_argument("--coverage", action="store_true", default=True, help="Generate coverage report")
    parser.add_argument("--no-coverage", action="store_true", help="Skip coverage reporting")
    parser.add_argument("--html", action="store_true", help="Generate HTML coverage report")
    parser.add_argument("--xml", action="store_true", help="Generate XML coverage report")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--fast", action="store_true", help="Skip slow tests")
    parser.add_argument("--parallel", "-n", type=int, help="Run tests in parallel")
    parser.add_argument("--pattern", "-k", type=str, help="Run tests matching pattern")
    parser.add_argument("--file", type=str, help="Run specific test file")
    
    args = parser.parse_args()
    
    # Set up the project root
    project_root = Path(__file__).parent
    os.chdir(project_root)
    
    # Build pytest command
    cmd = ["python", "-m", "pytest"]
    
    # Add test selection options
    if args.unit:
        cmd.extend(["-m", "unit"])
    elif args.integration:
        cmd.extend(["-m", "integration"])
    
    if args.fast:
        cmd.extend(["-m", "not slow"])
    
    if args.pattern:
        cmd.extend(["-k", args.pattern])
    
    if args.file:
        cmd.append(args.file)
    
    # Add coverage options
    if args.coverage and not args.no_coverage:
        cmd.extend([
            "--cov=src",
            "--cov-report=term-missing"
        ])
        
        if args.html:
            cmd.extend(["--cov-report=html:htmlcov"])
        
        if args.xml:
            cmd.extend(["--cov-report=xml"])
    
    # Add verbosity
    if args.verbose:
        cmd.append("-v")
    
    # Add parallel execution
    if args.parallel:
        cmd.extend(["-n", str(args.parallel)])
    
    # Add other useful options
    cmd.extend([
        "--tb=short",
        "--strict-markers",
        "--asyncio-mode=auto"
    ])
    
    print("=" * 60)
    print("Running Windows ChatGPT MCP Test Suite")
    print("=" * 60)
    
    # Run the tests
    success = run_command(cmd)
    
    if success:
        print("\n" + "=" * 60)
        print("✅ All tests passed!")
        
        if args.coverage and not args.no_coverage:
            print("\n📊 Coverage report generated:")
            if args.html:
                print(f"  HTML: {project_root}/htmlcov/index.html")
            if args.xml:
                print(f"  XML: {project_root}/coverage.xml")
        
        print("=" * 60)
        return 0
    else:
        print("\n" + "=" * 60)
        print("❌ Some tests failed!")
        print("=" * 60)
        return 1


if __name__ == "__main__":
    sys.exit(main())