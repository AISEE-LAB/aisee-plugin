from __future__ import annotations

from check_dependencies import Dependency, check_dependency, summary


def test_summary_fails_only_when_required_dependency_missing():
    checks = [
        check_dependency(
            Dependency(
                "missing-core",
                "definitely_missing_aisee_module",
                "core",
                True,
                "",
                "",
            )
        )
    ]

    result = summary(checks)

    assert result["ok"] is False
    assert result["missing_required"] == ["missing-core"]
