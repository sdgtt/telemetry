"""Content filter module for pre-upload filtering to Elasticsearch."""
import json
import re
import os


class ContentFilter:
    """Filter for pre-upload content filtering with whitelist/blacklist support.

    Supports two types of rules:
    - action="keep" (whitelist): Only matching items are uploaded
    - action="drop" (blacklist): Matching items are excluded from upload
    """

    def __init__(self, file_path=None):
        """Initialize filter with optional config file.

        Args:
            file_path: Path to JSON filter configuration file
        """
        self.rules = []
        self.version = None
        if file_path:
            self.load(file_path)

    def load(self, file_path):
        """Load filter rules from JSON file.

        Args:
            file_path: Path to JSON configuration file
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Filter file not found: {file_path}")

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
                return bool(re.search(pattern, message, re.IGNORECASE))
            except re.error:
                return False

        return False

    def _get_applicable_rules(self, issue_type, board=None, project=None):
        """Get rules applicable to the given issue type and scope.

        Args:
            issue_type: Type of issue (e.g., dmesg_error, pytest_failure)
            board: Optional board name for scope checking
            project: Optional project name for scope checking

        Returns:
            Tuple of (whitelist_rules, blacklist_rules)
        """
        whitelist_rules = []
        blacklist_rules = []

        for rule in self.rules:
            # Filter by issue type
            if rule.get("type") != issue_type:
                continue

            # Filter by scope
            if not self._matches_scope(rule, board, project):
                continue

            # Categorize by action
            action = rule.get("action", "drop")  # Default to drop for backward compatibility
            if action == "keep":
                whitelist_rules.append(rule)
            else:
                blacklist_rules.append(rule)

        return whitelist_rules, blacklist_rules

    def should_upload(self, message, issue_type, board=None, project=None):
        """Determine if a message should be uploaded to Elasticsearch.

        Filter Logic:
        1. Get rules matching the issue_type and scope
        2. If whitelist rules exist: message MUST match at least one
        3. If blacklist rules exist: message must NOT match any
        4. No rules = allow upload (backward compatible)

        Args:
            message: The content/message to check
            issue_type: Type of issue (e.g., dmesg_error, pytest_failure)
            board: Optional board name for scope checking
            project: Optional project name for scope checking

        Returns:
            Tuple of (should_upload: bool, reason: str)
        """
        whitelist_rules, blacklist_rules = self._get_applicable_rules(
            issue_type, board, project
        )

        # Whitelist check: if whitelist rules exist, message must match at least one
        if whitelist_rules:
            matched_whitelist = False
            for rule in whitelist_rules:
                if self._matches_pattern(message, rule):
                    matched_whitelist = True
                    break

            if not matched_whitelist:
                return (False, "no whitelist match")

        # Blacklist check: message must not match any blacklist rule
        for rule in blacklist_rules:
            if self._matches_pattern(message, rule):
                return (False, rule.get("description", "blacklist match"))

        return (True, "passed")

    def filter_payload(self, payload_items, issue_type, board=None, project=None, verbose=False):
        """Filter a list of payload items before upload.

        Args:
            payload_items: List of (raw, processed) payload tuples or strings
            issue_type: Type of issue (e.g., dmesg_error, pytest_failure)
            board: Optional board name for scope checking
            project: Optional project name for scope checking
            verbose: If True, print filtered items

        Returns:
            List of indices that should be uploaded
        """
        indices_to_upload = []

        for i, item in enumerate(payload_items):
            # Extract message text from item (handle both tuple and string formats)
            if isinstance(item, (list, tuple)) and len(item) >= 2:
                message = item[1]
            else:
                message = str(item)

            should_upload, reason = self.should_upload(message, issue_type, board, project)

            if should_upload:
                indices_to_upload.append(i)
            elif verbose:
                print(f"Filtered out (reason: {reason}): {message[:80]}...")

        return indices_to_upload
