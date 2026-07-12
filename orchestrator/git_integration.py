"""
Git Integration Module for Production Orchestrator - Phase 1

Provides real git operations via GitPython library.
"""

import logging
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)

try:
    import git
    HAS_GITPYTHON = True
except ImportError:
    HAS_GITPYTHON = False
    logger.warning("GitPython not installed, using subprocess fallback")


@dataclass
class CommitInfo:
    """Information about a commit."""
    hash: str
    author: str
    message: str
    timestamp: str
    files_changed: int


@dataclass
class FileStatus:
    """Status of a file in git."""
    path: str
    status: str  # 'staged', 'unstaged', 'untracked', 'deleted'
    is_modified: bool = False
    is_new: bool = False
    is_deleted: bool = False


@dataclass
class DiffStat:
    """Diff statistics."""
    file_path: str
    additions: int
    deletions: int
    changes: int


class GitAnalyzer:
    """Analyzes git repository with real git operations."""

    def __init__(self, project_root: str):
        """Initialize git analyzer for a project.

        Args:
            project_root: Path to project root (must be git repo)

        Raises:
            ValueError: If not a git repository
        """
        self.project_root = Path(project_root)

        if not (self.project_root / '.git').exists():
            raise ValueError(f"Not a git repository: {project_root}")

        if HAS_GITPYTHON:
            self.repo = git.Repo(project_root)
        else:
            self.repo = None

        logger.info(f"Initialized GitAnalyzer for {project_root}")

    def get_current_branch(self) -> str:
        """Get current branch name.

        Returns:
            Branch name or 'detached' if detached HEAD
        """
        try:
            if HAS_GITPYTHON:
                return self.repo.active_branch.name
            else:
                return self._run_git(['branch', '--show-current']).strip()
        except Exception as e:
            logger.warning(f"Could not get branch name: {e}")
            return "unknown"

    def get_current_commit(self) -> str:
        """Get current commit hash.

        Returns:
            Short commit hash (7 chars)
        """
        try:
            if HAS_GITPYTHON:
                return self.repo.head.commit.hexsha[:7]
            else:
                return self._run_git(['rev-parse', '--short', 'HEAD']).strip()
        except Exception as e:
            logger.error(f"Could not get current commit: {e}")
            return "unknown"

    def get_file_status(self) -> List[FileStatus]:
        """Get status of all files in repository.

        Returns:
            List of FileStatus objects
        """
        statuses = []

        try:
            if HAS_GITPYTHON:
                # Get all changes
                for item in self.repo.index.diff(None):  # unstaged
                    path = item.a_path
                    statuses.append(FileStatus(
                        path=path,
                        status='unstaged',
                        is_modified=item.change_type == 'M',
                        is_deleted=item.change_type == 'D'
                    ))

                for item in self.repo.index.diff('HEAD'):  # staged
                    path = item.a_path
                    statuses.append(FileStatus(
                        path=path,
                        status='staged',
                        is_modified=item.change_type == 'M',
                        is_deleted=item.change_type == 'D'
                    ))

                # Untracked files
                for item in self.repo.untracked_files:
                    statuses.append(FileStatus(
                        path=item,
                        status='untracked',
                        is_new=True
                    ))
            else:
                # Fallback using git status
                output = self._run_git(['status', '--porcelain'])
                for line in output.strip().split('\n'):
                    if not line:
                        continue
                    status_code = line[:2]
                    path = line[3:]

                    if status_code == '??':
                        statuses.append(FileStatus(path=path, status='untracked', is_new=True))
                    elif 'M' in status_code:
                        statuses.append(FileStatus(path=path, status='modified', is_modified=True))
                    elif 'D' in status_code:
                        statuses.append(FileStatus(path=path, status='deleted', is_deleted=True))

            return statuses

        except Exception as e:
            logger.error(f"Could not get file status: {e}")
            return []

    def is_repository_clean(self) -> bool:
        """Check if repository has no uncommitted changes.

        Returns:
            True if clean (no changes), False otherwise
        """
        statuses = self.get_file_status()
        return len(statuses) == 0

    def get_commit_history(self, max_commits: int = 10) -> List[CommitInfo]:
        """Get recent commit history.

        Args:
            max_commits: Maximum number of commits to return

        Returns:
            List of CommitInfo objects
        """
        commits = []

        try:
            if HAS_GITPYTHON:
                for commit in self.repo.iter_commits('HEAD', max_count=max_commits):
                    commits.append(CommitInfo(
                        hash=commit.hexsha[:7],
                        author=commit.author.name,
                        message=commit.message.split('\n')[0],  # First line only
                        timestamp=datetime.fromtimestamp(commit.committed_date).isoformat(),
                        files_changed=commit.stats.total.get('files', 0)
                    ))
            else:
                output = self._run_git(['log', '--oneline', f'-n{max_commits}'])
                for line in output.strip().split('\n'):
                    if not line:
                        continue
                    parts = line.split(' ', 1)
                    commits.append(CommitInfo(
                        hash=parts[0],
                        author='unknown',
                        message=parts[1] if len(parts) > 1 else '',
                        timestamp=datetime.now().isoformat(),
                        files_changed=0
                    ))

            return commits

        except Exception as e:
            logger.error(f"Could not get commit history: {e}")
            return []

    def get_diff_summary(self, from_commit: str = 'HEAD~1', to_commit: str = 'HEAD') -> Dict:
        """Get diff summary between commits.

        Args:
            from_commit: Source commit (default: previous)
            to_commit: Target commit (default: current)

        Returns:
            Dictionary with diff statistics
        """
        try:
            if HAS_GITPYTHON:
                diff_index = self.repo.commit(from_commit).diff(to_commit)
                files_changed = []

                for diff in diff_index:
                    files_changed.append(DiffStat(
                        file_path=diff.a_path or diff.b_path,
                        additions=diff.diff.count(b'\n+'),
                        deletions=diff.diff.count(b'\n-'),
                        changes=diff.diff.count(b'\n+') + diff.diff.count(b'\n-')
                    ))

                return {
                    'from': from_commit,
                    'to': to_commit,
                    'files_changed': len(files_changed),
                    'total_additions': sum(f.additions for f in files_changed),
                    'total_deletions': sum(f.deletions for f in files_changed),
                    'files': [{'path': f.file_path, 'adds': f.additions, 'dels': f.deletions} for f in files_changed]
                }
            else:
                output = self._run_git(['diff', '--stat', f'{from_commit}..{to_commit}'])
                return {
                    'from': from_commit,
                    'to': to_commit,
                    'output': output,
                    'files_changed': 0
                }

        except Exception as e:
            logger.warning(f"Could not get diff summary: {e}")
            return {'error': str(e)}

    def stage_file(self, relative_path: str) -> bool:
        """Stage a file for commit.

        Args:
            relative_path: Path relative to repo root

        Returns:
            True if successful
        """
        try:
            if HAS_GITPYTHON:
                self.repo.index.add(relative_path)
            else:
                self._run_git(['add', relative_path])

            logger.info(f"Staged file: {relative_path}")
            return True

        except Exception as e:
            logger.error(f"Could not stage file {relative_path}: {e}")
            return False

    def commit(self, message: str, author: str = "Orchestrator <orchestrator@local>") -> Optional[str]:
        """Create a commit.

        Args:
            message: Commit message
            author: Author name and email

        Returns:
            Commit hash or None if failed
        """
        try:
            if not self.repo.index.diff('HEAD'):
                logger.warning("No changes to commit")
                return None

            if HAS_GITPYTHON:
                commit = self.repo.index.commit(message, author=git.Actor(author.split('<')[0].strip(), author.split('<')[1].rstrip('>')))
                hash = commit.hexsha[:7]
            else:
                name, email = author.split('<')
                self._run_git(['config', 'user.name', name.strip()])
                self._run_git(['config', 'user.email', email.rstrip('>')])
                self._run_git(['commit', '-m', message])
                hash = self._run_git(['rev-parse', '--short', 'HEAD']).strip()

            logger.info(f"Created commit: {hash} - {message}")
            return hash

        except Exception as e:
            logger.error(f"Could not create commit: {e}")
            return None

    def stage_and_commit(self, files: List[str], message: str) -> Optional[str]:
        """Stage multiple files and create commit.

        Args:
            files: List of file paths to stage
            message: Commit message

        Returns:
            Commit hash or None if failed
        """
        try:
            for file in files:
                self.stage_file(file)

            return self.commit(message)

        except Exception as e:
            logger.error(f"Could not stage and commit: {e}")
            return None

    def _run_git(self, args: List[str]) -> str:
        """Run git command via subprocess.

        Args:
            args: git command arguments

        Returns:
            Command output

        Raises:
            Exception: If command fails
        """
        try:
            result = subprocess.run(
                ['git', '-C', str(self.project_root)] + args,
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode != 0:
                raise Exception(f"git {' '.join(args)} failed: {result.stderr}")

            return result.stdout

        except Exception as e:
            logger.error(f"Git command failed: {e}")
            raise


# Test module usage
if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        project_path = sys.argv[1]
    else:
        project_path = "/home/vali/projects/investing-platform"

    logging.basicConfig(level=logging.INFO)

    try:
        analyzer = GitAnalyzer(project_path)

        print(f"✓ Repository: {project_path}")
        print(f"✓ Branch: {analyzer.get_current_branch()}")
        print(f"✓ Current commit: {analyzer.get_current_commit()}")
        print(f"✓ Is clean: {analyzer.is_repository_clean()}")

        history = analyzer.get_commit_history(3)
        print(f"✓ Recent commits: {len(history)}")
        for commit in history:
            print(f"  - {commit.hash}: {commit.message[:60]}")

        statuses = analyzer.get_file_status()
        print(f"✓ File status: {len(statuses)} changes")

    except Exception as e:
        print(f"✗ Error: {e}")
        sys.exit(1)
