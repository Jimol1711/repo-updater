import os
import subprocess
from update_gitignore import update_gitignore

def is_git_repo(path):
    """Check if a directory is a Git repository."""
    return os.path.isdir(os.path.join(path, '.git'))

def has_upstream(repo_path):
    """Check if the current branch has an upstream branch set."""
    try:
        subprocess.check_output(["git", "rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{u}"], cwd=repo_path)
        return True
    except subprocess.CalledProcessError:
        return False

def check_status(repo_path):
    """Fetch and pull changes from the remote repository, and check for potential conflicts."""
    try:
        print(f"Fetching and checking status in {repo_path}...")
        subprocess.run(["git", "fetch"], cwd=repo_path, check=True)

        if not has_upstream(repo_path):
            print(f"Repository '{repo_path}' does not have an upstream branch set.")
            return

        status_output = subprocess.check_output(["git", "status", "-uno"], cwd=repo_path).decode("utf-8")
        local_commits = subprocess.check_output(["git", "rev-list", "HEAD...@{u}", "--left-right"], cwd=repo_path).decode("utf-8").splitlines()

        ahead = behind = False
        for commit in local_commits:
            if commit.startswith("<"):
                ahead = True  # Local is ahead of the remote
            elif commit.startswith(">"):
                behind = True  # Local is behind the remote

        if ahead and behind:
            print(f"Repository '{repo_path}' has diverged from the remote. Manual update required.")
        elif ahead:
            print(f"Repository '{repo_path}' is ahead of the remote. Pushing updates...")
            # Check if there are changes to commit
            if "Changes to be committed:" in status_output:
                subprocess.run(["git", "add", "."], cwd=repo_path, check=True)
                subprocess.run(["git", "commit", "-m", "automatic commit message"], cwd=repo_path, check=True)
            subprocess.run(["git", "push"], cwd=repo_path, check=True)
        elif behind:
            print(f"Repository '{repo_path}' is behind the remote. Pulling updates...")
            subprocess.run(["git", "pull"], cwd=repo_path, check=True)
        else:
            print(f"No changes detected in {repo_path}.")
    except subprocess.CalledProcessError as e:
        print(f"Failed to fetch/pull in {repo_path}: {e}")

def update_directories(base_dir):
    """Recursively check directories."""
    for root, dirs, _ in os.walk(base_dir):
        for d in dirs:
            dir_path = os.path.join(root, d)
            if is_git_repo(dir_path):
                check_status(dir_path)

if __name__ == "__main__":
    update_gitignore()
    base_directory = os.path.dirname(os.path.abspath(__file__))  # Replace with your base directory
    update_directories(base_directory)