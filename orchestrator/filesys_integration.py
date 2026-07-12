"""
Filesystem Integration Module for Production Orchestrator - Phase 1

Provides real file I/O operations, replacing simulated behavior.
"""

import hashlib
import logging
import os
import ast
from pathlib import Path
from typing import Dict, Set, List, Optional, Tuple
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class FileMetadata:
    """Metadata about a file."""
    path: str
    size_bytes: int
    modified_time: float
    sha256_hash: str
    is_python: bool = False
    is_test: bool = False
    encoding: str = "utf-8"


@dataclass
class DirectorySnapshot:
    """Snapshot of directory structure and files."""
    root_path: str
    files: List[FileMetadata] = field(default_factory=list)
    file_hashes: Dict[str, str] = field(default_factory=dict)  # path -> hash
    total_files: int = 0
    total_lines: int = 0
    python_files: int = 0
    test_files: int = 0

    def compute_directory_hash(self) -> str:
        """Compute hash of all file hashes (represents directory state)."""
        all_hashes = "".join(sorted(self.file_hashes.values()))
        return hashlib.sha256(all_hashes.encode()).hexdigest()


class FilesystemAnalyzer:
    """Analyzes project filesystem with real file I/O."""

    def __init__(self, project_root: str):
        """Initialize analyzer for a project directory.

        Args:
            project_root: Path to project root directory

        Raises:
            ValueError: If path doesn't exist or isn't a directory
        """
        self.project_root = Path(project_root)

        if not self.project_root.exists():
            raise ValueError(f"Project root does not exist: {project_root}")

        if not self.project_root.is_dir():
            raise ValueError(f"Project root is not a directory: {project_root}")

        logger.info(f"Initialized FilesystemAnalyzer for {project_root}")

    def capture_snapshot(self) -> DirectorySnapshot:
        """Capture current state of project filesystem.

        Returns:
            DirectorySnapshot with all file metadata and hashes
        """
        snapshot = DirectorySnapshot(root_path=str(self.project_root))

        try:
            # Walk the project directory
            for root, dirs, files in os.walk(self.project_root):
                # Skip common directories
                dirs[:] = [d for d in dirs if d not in {'.git', '__pycache__', '.pytest_cache', 'node_modules', '.venv', 'venv'}]

                for filename in files:
                    file_path = Path(root) / filename

                    # Skip common non-source files
                    if filename.startswith('.'):
                        continue
                    if filename.endswith(('.pyc', '.pyo', '.so')):
                        continue

                    try:
                        metadata = self._get_file_metadata(file_path)
                        snapshot.files.append(metadata)
                        snapshot.file_hashes[metadata.path] = metadata.sha256_hash

                        snapshot.total_files += 1
                        if metadata.is_python:
                            snapshot.python_files += 1
                        if metadata.is_test:
                            snapshot.test_files += 1

                        # Count lines for Python files
                        if metadata.is_python:
                            try:
                                with open(file_path, 'r', encoding=metadata.encoding, errors='ignore') as f:
                                    snapshot.total_lines += len(f.readlines())
                            except Exception as e:
                                logger.warning(f"Could not count lines in {file_path}: {e}")

                    except Exception as e:
                        logger.warning(f"Could not process file {file_path}: {e}")

            logger.info(f"Captured snapshot: {snapshot.total_files} files, "
                       f"{snapshot.python_files} Python, {snapshot.test_files} tests, "
                       f"{snapshot.total_lines} total lines")

            return snapshot

        except Exception as e:
            logger.error(f"Error capturing filesystem snapshot: {e}")
            raise

    def _get_file_metadata(self, file_path: Path) -> FileMetadata:
        """Get metadata for a single file.

        Args:
            file_path: Path to file

        Returns:
            FileMetadata object

        Raises:
            Exception: If file cannot be read
        """
        stat = file_path.stat()

        # Compute relative path from project root
        try:
            rel_path = file_path.relative_to(self.project_root)
        except ValueError:
            rel_path = file_path

        # Compute hash
        sha256_hash = self._compute_file_hash(file_path)

        # Determine if Python file
        is_python = file_path.suffix == '.py'
        is_test = 'test' in file_path.name or 'tests' in str(rel_path)

        return FileMetadata(
            path=str(rel_path),
            size_bytes=stat.st_size,
            modified_time=stat.st_mtime,
            sha256_hash=sha256_hash,
            is_python=is_python,
            is_test=is_test,
            encoding='utf-8'
        )

    @staticmethod
    def _compute_file_hash(file_path: Path) -> str:
        """Compute SHA256 hash of file contents.

        Args:
            file_path: Path to file

        Returns:
            Hex digest of SHA256 hash
        """
        sha256 = hashlib.sha256()

        try:
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(8192), b''):
                    sha256.update(chunk)
            return sha256.hexdigest()
        except Exception as e:
            logger.error(f"Could not hash file {file_path}: {e}")
            # Return hash of file path as fallback
            return hashlib.sha256(str(file_path).encode()).hexdigest()

    def compare_snapshots(self, before: DirectorySnapshot, after: DirectorySnapshot) -> Dict:
        """Compare two filesystem snapshots.

        Args:
            before: Earlier snapshot
            after: Later snapshot

        Returns:
            Dictionary with changes (files_added, files_deleted, files_modified, etc.)
        """
        before_hashes = before.file_hashes
        after_hashes = after.file_hashes

        before_paths = set(before_hashes.keys())
        after_paths = set(after_hashes.keys())

        files_added = after_paths - before_paths
        files_deleted = before_paths - after_paths
        files_modified = {
            path for path in before_paths & after_paths
            if before_hashes[path] != after_hashes[path]
        }

        return {
            'files_added': sorted(files_added),
            'files_deleted': sorted(files_deleted),
            'files_modified': sorted(files_modified),
            'total_changes': len(files_added) + len(files_deleted) + len(files_modified),
            'before_hash': before.compute_directory_hash(),
            'after_hash': after.compute_directory_hash(),
            'directory_state_changed': before.compute_directory_hash() != after.compute_directory_hash(),
        }

    def get_python_files(self) -> List[Path]:
        """Get all Python files in project.

        Returns:
            List of Path objects for Python files
        """
        python_files = []

        for root, dirs, files in os.walk(self.project_root):
            dirs[:] = [d for d in dirs if d not in {'.git', '__pycache__', '.pytest_cache', 'node_modules', '.venv', 'venv'}]

            for filename in files:
                if filename.endswith('.py') and not filename.startswith('.'):
                    python_files.append(Path(root) / filename)

        return sorted(python_files)

    def read_file(self, relative_path: str) -> str:
        """Read file contents.

        Args:
            relative_path: Path relative to project root

        Returns:
            File contents as string

        Raises:
            FileNotFoundError: If file doesn't exist
        """
        file_path = self.project_root / relative_path

        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {relative_path}")

        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            return f.read()

    def write_file(self, relative_path: str, content: str) -> None:
        """Write content to file.

        Args:
            relative_path: Path relative to project root
            content: Content to write

        Raises:
            Exception: If write fails
        """
        file_path = self.project_root / relative_path

        # Create parent directories if needed
        file_path.parent.mkdir(parents=True, exist_ok=True)

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)

        logger.info(f"Wrote file: {relative_path}")

    def parse_python_file(self, relative_path: str) -> Optional[ast.Module]:
        """Parse Python file and return AST.

        Args:
            relative_path: Path relative to project root

        Returns:
            AST Module or None if parse fails
        """
        try:
            content = self.read_file(relative_path)
            return ast.parse(content)
        except Exception as e:
            logger.warning(f"Could not parse {relative_path}: {e}")
            return None


# Test module usage
if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        project_path = sys.argv[1]
    else:
        project_path = "/home/vali/projects/investing-platform"

    logging.basicConfig(level=logging.INFO)

    try:
        analyzer = FilesystemAnalyzer(project_path)
        snapshot = analyzer.capture_snapshot()

        print(f"✓ Project: {project_path}")
        print(f"✓ Total files: {snapshot.total_files}")
        print(f"✓ Python files: {snapshot.python_files}")
        print(f"✓ Test files: {snapshot.test_files}")
        print(f"✓ Total lines of code: {snapshot.total_lines}")
        print(f"✓ Directory hash: {snapshot.compute_directory_hash()[:16]}...")

    except Exception as e:
        print(f"✗ Error: {e}")
        sys.exit(1)
