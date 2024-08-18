import os
import subprocess

def update_gitignore():
    """Update the .gitignore file in the current directory with all files and directories except the script file."""
    current_dir = os.getcwd()
    script_name = os.path.basename(__file__)
    gitignore_path = os.path.join(current_dir, ".gitignore")

    # Read the existing .gitignore entries, if it exists
    if os.path.exists(gitignore_path):
        with open(gitignore_path, 'r') as f:
            gitignore_entries = set(f.read().splitlines())
    else:
        gitignore_entries = set()

    # List all files and directories in the current directory
    items = os.listdir(current_dir)

    # Initialize a set to track new entries
    new_entries = set()

    for item in items:
        # Skip the script file and .gitignore file
        if item == script_name or item == ".gitignore" or item == "update_repos.py" or item == "README.md":
            continue

        # Add directory names with a trailing slash
        if os.path.isdir(item):
            item_entry = f"{item}/"
        else:
            item_entry = item

        # If the item is not already in .gitignore, add it to new_entries
        if item_entry not in gitignore_entries:
            new_entries.add(item_entry)

    # If there are new entries, append them to the .gitignore file
    if new_entries:
        with open(gitignore_path, 'a') as f:
            for entry in new_entries:
                f.write(f"{entry}\n")

        print(f"Added {len(new_entries)} new entries to .gitignore.")
    else:
        print("No new entries to add to .gitignore.")

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
        print(status_output)
        local_commits = subprocess.check_output(["git", "rev-list", "HEAD...@{u}", "--left-right"], cwd=repo_path).decode("utf-8").splitlines()
        print(local_commits)

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