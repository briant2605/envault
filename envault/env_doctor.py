"""Doctor: diagnose common issues with a .env file and its vault."""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import List

from envault.vault import vault_path_for
from envault.lint import lint_env, LintIssue


@dataclass
class DoctorReport:
    env_file: Path
    checks: List[str] = field(default_factory=list)   # passed checks
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return len(self.errors) == 0


def run_doctor(env_file: Path) -> DoctorReport:
    """Run all diagnostic checks and return a DoctorReport."""
    report = DoctorReport(env_file=env_file)

    # 1. env file exists
    if not env_file.exists():
        report.errors.append(f".env file not found: {env_file}")
        return report  # no point continuing
    report.checks.append(".env file exists")

    # 2. env file is readable
    if not os.access(env_file, os.R_OK):
        report.errors.append(".env file is not readable")
    else:
        report.checks.append(".env file is readable")

    # 3. vault file exists
    vault = vault_path_for(env_file)
    if not vault.exists():
        report.warnings.append("No vault file found — run 'envault lock' to create one")
    else:
        report.checks.append("Vault file exists")

    # 4. .env not tracked by git (check .gitignore naively)
    gitignore = env_file.parent / ".gitignore"
    if gitignore.exists():
        content = gitignore.read_text()
        if env_file.name not in content and ".env" not in content:
            report.warnings.append(".env may not be listed in .gitignore")
        else:
            report.checks.append(".env appears in .gitignore")
    else:
        report.warnings.append(".gitignore not found — ensure .env is not committed")

    # 5. lint checks
    issues: List[LintIssue] = lint_env(env_file)
    lint_errors = [i for i in issues if i.severity == "error"]
    lint_warns = [i for i in issues if i.severity == "warning"]
    if lint_errors:
        for i in lint_errors:
            report.errors.append(f"Lint error line {i.line}: {i.message}")
    else:
        report.checks.append("No lint errors")
    for i in lint_warns:
        report.warnings.append(f"Lint warning line {i.line}: {i.message}")

    return report
