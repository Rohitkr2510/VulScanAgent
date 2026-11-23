import os
import shutil
import tempfile
import logging
from pathlib import Path
from typing import Optional, Tuple
import git

logger = logging.getLogger(__name__)


class RepoConnector:
    """Manages cloning, branch isolation, and git operations for public & private GitHub repos."""

    def __init__(self, repo_url: str, base_branch: str = "main", token: Optional[str] = None):
        self.repo_url = repo_url
        self.base_branch = base_branch
        self.token = token
        self.repo: Optional[git.Repo] = None
        self.local_dir: Optional[Path] = None

    def _get_authenticated_url(self) -> str:
        """Injects authentication token for private repositories."""
        if not self.token:
            return self.repo_url

        url = self.repo_url.strip()
        if url.startswith("https://"):
            # Format: https://x-access-token:<token>@github.com/org/repo.git
            clean_url = url.replace("https://", "")
            return f"https://x-access-token:{self.token}@{clean_url}"

        return self.repo_url

    def clone(self, target_dir: Optional[Path] = None) -> Path:
        """Clones repository into a target directory or temporary working directory."""
        if target_dir:
            self.local_dir = Path(target_dir)
            if self.local_dir.exists():
                shutil.rmtree(self.local_dir, ignore_errors=True)
            self.local_dir.mkdir(parents=True, exist_ok=True)
        else:
            self.local_dir = Path(tempfile.mkdtemp(prefix="vulscan_repo_"))

        auth_url = self._get_authenticated_url()
        logger.info(f"Cloning {self.repo_url} (branch: {self.base_branch}) into {self.local_dir}")

        self.repo = git.Repo.clone_from(
            url=auth_url,
            to_path=str(self.local_dir),
            branch=self.base_branch,
            depth=1
        )
        return self.local_dir

    def create_fix_branch(self, branch_name: str) -> str:
        """Creates and checks out an isolated fix branch."""
        if not self.repo:
            raise RuntimeError("Repository not cloned yet.")

        current_branches = [h.name for h in self.repo.heads]
        if branch_name in current_branches:
            self.repo.heads[branch_name].checkout()
        else:
            new_head = self.repo.create_head(branch_name)
            new_head.checkout()

        logger.info(f"Checked out new branch: {branch_name}")
        return branch_name

    def commit_changes(self, message: str, files_to_add: Optional[list[str]] = None) -> str:
        """Stages and commits changes."""
        if not self.repo:
            raise RuntimeError("Repository not cloned yet.")

        if files_to_add:
            self.repo.index.add(files_to_add)
        else:
            self.repo.git.add(A=True)

        commit = self.repo.index.commit(message)
        logger.info(f"Committed changes: {commit.hexsha[:7]} - {message}")
        return commit.hexsha

    def push(self, branch_name: str) -> None:
        """Pushes branch to remote origin."""
        if not self.repo:
            raise RuntimeError("Repository not cloned yet.")

        logger.info(f"Pushing branch {branch_name} to origin")
        origin = self.repo.remote(name="origin")
        origin.push(refspec=f"{branch_name}:{branch_name}")

    def cleanup(self) -> None:
        """Removes temporary local clone."""
        if self.local_dir and self.local_dir.exists():
            try:
                shutil.rmtree(self.local_dir, ignore_errors=True)
                logger.info(f"Cleaned up local clone at {self.local_dir}")
            except Exception as e:
                logger.warning(f"Error cleaning up {self.local_dir}: {e}")
