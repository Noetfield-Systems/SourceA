"""SourceA shared content-quality spine."""
from content_quality_spine.evaluate import evaluate, evaluate_files
from content_quality_spine.version import PACKAGE_NAME, SPINE_VERSION, rules_hash

__all__ = ["evaluate", "evaluate_files", "SPINE_VERSION", "PACKAGE_NAME", "rules_hash"]
