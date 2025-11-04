#!/usr/bin/env python3

import argparse
import subprocess
import sys
from pathlib import Path

def run(cmd: list[str], cwd: Path | None = None) -> int:
    print(f"Running command: {' '.join(cmd)}")
    proc = subprocess.run(cmd, cwd=cwd, text=True)
    return proc.returncode

def main() -> int:
    parser = argparse.ArgumentParser(description="CI Run Script")
    parser.add_argument("--report-dir", default='reports', help="Where to put junit/html/coverage output")
    parser.add_argument("--extra", nargs=argparse.REMAINDER, help="Pass thru args to pytest", default=[])
    args = parser.parse_args()

    out = Path(args.report_dir)
    out.mkdir(parents=True, exist_ok=True)

    pytest_cmd = [
        sys.executable, "-m", "pytest",
        "--junitxml", str(out / "junit.xml"),
        "--html", str(out / "report.html"),
        "--self-contained-html",
        "--cov", ".", "--cov-report", f"xml:{out / 'coverage.xml'}",
        "--cov-report", f"term",
    ] + args.extra
    
    code = run(pytest_cmd)
    if code == 0:
        print("\n✅ Tests passed successfully.")
    else:
        print("\n❌ Some tests failed.")
    return code


if __name__ == "__main__":
    sys.exit(main())