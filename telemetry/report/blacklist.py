"""Blacklist module for filtering known issues from reports."""
import json
import re
import os


class Blacklist:
    """Handles loading and matching known issues against report data."""

    def __init__(self, file_path=None):
        """Initialize blacklist with optional config file.

        Args:
            file_path: Path to JSON blacklist configuration file
        """
        self.rules = []
        self.version = None
        if file_path:
            self.load(file_path)

    def load(self, file_path):
        """Load blacklist rules from JSON file.

        Args:
            file_path: Path to JSON configuration file
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Blacklist file not found: {file_path}")

        with open(file_path, 'r') as f:
            config = json.load(f)

        self.version = config.get("version", "1.0")
        self.rules = config.get("rules", [])

    def _matches_scope(self, rule, board=None, project=None):
        """Check if rule scope matches the current board/project.

        Args:
            rule: The rule dict containing optional scope
            board: Current board name
            project: Current project/job name

        Returns:
            True if rule applies to this board/project
        """
        scope = rule.get("scope")

        # No scope = global rule, applies to everything
        if scope is None:
            return True

        # Check board scope
        if "boards" in scope and scope["boards"]:
            if board and board not in scope["boards"]:
                return False

        # Check project scope
        if "projects" in scope and scope["projects"]:
            if project and project not in scope["projects"]:
                return False

        return True

    def _matches_pattern(self, message, rule):
        """Check if message matches the rule pattern.

        Args:
            message: The error/failure message to check
            rule: The rule dict with pattern and match_type

        Returns:
            True if message matches the pattern
        """
        pattern = rule.get("pattern", "")
        match_type = rule.get("match_type", "contains")

        if match_type == "exact":
            return message == pattern
        elif match_type == "contains":
            return pattern in message
        elif match_type == "regex":
            try:
                return bool(re.search(pattern, message))
            except re.error:
                return False

        return False

    def is_known_issue(self, message, issue_type, board=None, project=None):
        """Check if a message is a known issue.

        Args:
            message: The error/failure message to check
            issue_type: Type of issue (dmesg_error, pytest_failure, missing_driver)
            board: Optional board name for scope checking
            project: Optional project name for scope checking

        Returns:
            Tuple of (is_known, description) where description is the known issue
            description if matched, None otherwise
        """
        for rule in self.rules:
            if rule.get("type") != issue_type:
                continue

            if not self._matches_scope(rule, board, project):
                continue

            if self._matches_pattern(message, rule):
                return (True, rule.get("description", "Known issue"))

        return (False, None)

    def filter_items(self, items, issue_type, mode="mark", board=None, project=None):
        """Filter a list of items based on blacklist rules.

        Args:
            items: List of error/failure messages
            issue_type: Type of issue (dmesg_error, pytest_failure, missing_driver)
            mode: "mark" to annotate known issues, "hide" to remove them
            board: Optional board name for scope checking
            project: Optional project name for scope checking

        Returns:
            Filtered/annotated list of items
        """
        if not items:
            return items

        result = []
        for item in items:
            is_known, description = self.is_known_issue(item, issue_type, board, project)

            if is_known:
                if mode == "hide":
                    # Skip this item entirely
                    continue
                elif mode == "mark":
                    # Annotate with known issue marker
                    result.append(f"{item} [KNOWN: {description}]")
            else:
                result.append(item)

        return result

    def count_known_issues(self, items, issue_type, board=None, project=None):
        """Count how many items in the list are known issues.

        Args:
            items: List of error/failure messages
            issue_type: Type of issue
            board: Optional board name
            project: Optional project name

        Returns:
            Number of known issues found
        """
        count = 0
        for item in items:
            is_known, _ = self.is_known_issue(item, issue_type, board, project)
            if is_known:
                count += 1
        return count
