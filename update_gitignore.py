import os

def update_gitignore():
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
