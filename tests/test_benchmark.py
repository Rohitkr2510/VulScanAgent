from pathlib import Path
from agent.models import (
    VulFinding,
    VulnerabilitySeverity,
    VulnerabilityCategory,
    CandidateStatus,
    FixResult,
    TestResult,
    TestStatus,
)
from agent.eval.benchmark import (
    GroundTruthItem,
    BenchmarkSuite,
    BenchmarkEvaluator,
)


def test_benchmark_evaluator_metrics(tmp_path: Path):
    gt = [
        GroundTruthItem(
            id="GT-1",
            file_path="pyproject.toml",
            line_number=8,
            category="SCA",
            cwe="CWE-79",
            rule_id="CVE-2024-56326",
            is_vulnerability=True
        ),
        GroundTruthItem(
            id="GT-2",
            file_path="docker-compose.yml",
            line_number=5,
            category="IAC",
            cwe="CWE-250",
            is_vulnerability=True
        ),
        GroundTruthItem(
            id="GT-3",
            file_path="app/main.py",
            line_number=28,
            category="SAST",
            is_vulnerability=False
        )
    ]
    suite = BenchmarkSuite(
        suite_name="test-suite",
        target_repo="test-repo",
        ground_truth=gt
    )

    evaluator = BenchmarkEvaluator(suite)

    # Mock finding 1 & 2
    f1 = VulFinding(
        id="SCA-CVE-2024-56326-jinja2",
        file_path="pyproject.toml",
        line_number=8,
        severity=VulnerabilitySeverity.HIGH,
        category=VulnerabilityCategory.SCA,
        title="Jinja2 CVE",
        description="Template breakout",
        cwe_id="CWE-79",
        validation_status=CandidateStatus.CONFIRMED
    )
    f2 = VulFinding(
        id="IAC-COMPOSE-ALL-INTERFACES",
        file_path="docker-compose.yml",
        line_number=5,
        severity=VulnerabilitySeverity.MEDIUM,
        category=VulnerabilityCategory.IAC,
        title="Port exposed",
        description="0.0.0.0 bind",
        cwe_id="CWE-250",
        validation_status=CandidateStatus.CONFIRMED
    )

    # Mock fix results
    fix1 = FixResult(
        finding_id=f1.id,
        success=True,
        applied_files=[f1.file_path],
        attempts=[],
        test_result=TestResult(command="pytest", status=TestStatus.PASSED, exit_code=0, stdout="5 passed", stderr="")
    )
    fix2 = FixResult(
        finding_id=f2.id,
        success=True,
        applied_files=[f2.file_path],
        attempts=[],
        test_result=TestResult(command="pytest", status=TestStatus.PASSED, exit_code=0, stdout="5 passed", stderr="")
    )

    metrics = evaluator.evaluate(
        raw_candidates=[f1, f2],
        confirmed_findings=[f1, f2],
        fix_results=[fix1, fix2],
        provider="google",
        runtime_seconds=5.2
    )

    assert metrics.true_positives == 2
    assert metrics.false_positives == 0
    assert metrics.false_negatives == 0
    assert metrics.true_negatives == 1
    assert metrics.precision == 100.0
    assert metrics.recall == 100.0
    assert metrics.f1_score == 100.0
    assert metrics.accuracy == 100.0
    assert metrics.youden_index == 1.0
    assert metrics.fix_success_rate == 100.0
    assert metrics.zero_regression_rate == 100.0

    report_file = tmp_path / "BENCHMARK.md"
    evaluator.generate_markdown_report(metrics, report_file)
    assert report_file.exists()
    content = report_file.read_text(encoding="utf-8")
    assert "Executive Summary Scorecard" in content
    assert "Confusion Matrix" in content
