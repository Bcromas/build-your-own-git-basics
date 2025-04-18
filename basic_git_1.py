import argparse
import hashlib
import os
import sys
import time


class BasicGit:
    def __init__(self, root_path="."):
        """
        Set up a new Git-like system to track changes to files.
        This creates a basic folder structure to store versions of our code.
        """
        self.root_path = os.path.abspath(
            root_path
        )  # get the full folder path where our code lives
        self.gitdir = os.path.join(
            self.root_path, ".basicgit"
        )  # create a hidden folder to store all Git data #* add hint & leave incomplete
        self.refs_dir = os.path.join(
            self.gitdir, "refs"
        )  # folder to store information about saved versions #* add hint & leave incomplete
        self.heads_dir = os.path.join(
            self.refs_dir, "heads"
        )  # folder to keep track of different branches #* add hint & leave incomplete
        self.HEAD_file = os.path.join(
            self.gitdir, "HEAD"
        )  # special file that tells us which branch we're currently using
        self.main_branch = "main"  # the default branch name we start with #* add hint & leave incomplete
        self.objects_dir = os.path.join(
            self.gitdir, "objects"
        )  # folder where all saved files and changes are stored

    def init(self):
        """Initialize a new repository."""
        if os.path.exists(self.gitdir):
            print(f"Repository already exists at {self.gitdir}")
            return  # * add hint & leave incomplete

        # Create all the folders we need to store Git data
        os.makedirs(self.gitdir, exist_ok=True)  # * add hint & leave incomplete
        os.makedirs(self.objects_dir, exist_ok=True)  # * add hint & leave incomplete
        os.makedirs(self.heads_dir, exist_ok=True)  # * add hint & leave incomplete

        # Create a HEAD file that points to our main branch - this is like a bookmark showing where we are
        with open(self.HEAD_file, "w") as f:
            f.write(f"refs/heads/{self.main_branch}")  # * add hint & leave incomplete

        # Create an empty main branch file - it's empty because we haven't saved any changes yet
        main_branch_path = os.path.join(self.heads_dir, self.main_branch)
        with open(main_branch_path, "w") as f:
            f.write(
                ""
            )  # Start with no commits - we'll add them when changes are saved #* add hint & leave incomplete

        print(f"Initialized empty repository in {self.gitdir}")

    def _hash_object(self, data):
        """
        Create a unique ID for the data by using SHA-1 hashing.
        This converts any content into a fixed-length string of characters
        used to identify and track files.

        Note: Methods starting with underscore (_) are considered "private" in Python.
        This means they're helper methods called by other public methods without an underscore prefix.
        """
        encoded_data = data.encode(
            "utf-8"
        )  # convert the text to computer-friendly format #* add hint & leave incomplete
        return hashlib.sha1(
            encoded_data
        ).hexdigest()  # create a unique fingerprint for this content #* add hint & leave incomplete

    def _store_object(self, data, sha):
        """
        Save content in Git's storage system using its unique ID (hash).
        We'll organize files into folders based on the first two characters of the hash to avoid having too many files in one place.
        """
        obj_dir = os.path.join(
            self.objects_dir, sha[:2]
        )  # use first 2 characters of hash as folder name #* add hint & leave incomplete
        obj_path = os.path.join(
            obj_dir, sha[2:]
        )  # use rest of hash as the filename #* add hint & leave incomplete
        os.makedirs(obj_dir, exist_ok=True)  # create the folder if it doesn't exist
        with open(obj_path, "w") as f:  # open a file to save the content
            f.write(
                data
            )  # save the actual content to disk for later retrieval #* add hint & leave incomplete

    def add(self, path):
        """Add a file to be tracked."""
        abs_path = os.path.abspath(path)
        if not os.path.exists(abs_path):
            print(f"Error: {path} does not exist")
            return

        # Get the current content of the file
        with open(abs_path, "r") as f:
            content = f.read()  # * add hint & leave incomplete
        # Simply store the content in the staging area
        self.staged_content = {path: content}

        print(f"Added {path}")

    def commit(self, message):
        """Save the staged changes with a message for clarity."""
        # Check if there's anything staged to commit
        if not hasattr(self, "staged_content") or not self.staged_content:
            print("No changes to commit")
            return

        # For simplicity in Stage 1, we're only handling one added file
        if len(self.staged_content) != 1:
            print(
                "Error: Please add exactly one file before committing in this version."
            )
            return

        path, content = list(self.staged_content.items())[0]
        # Create a "blob" by hashing the content
        blob_sha = self._hash_object(content)
        self._store_object(content, blob_sha)  # save the content

        # Create a commit object with message, timestamp, and file information
        commit_data = {
            "message": message,
            "timestamp": int(time.time()),
            "file": {path: blob_sha},
        }

        # Convert the commit data to text and save it with its own unique ID
        commit_string = str(commit_data)
        # Hash the commit string
        commit_sha = self._hash_object(commit_string)
        self._store_object(commit_string, commit_sha)  # save the commit string and hash

        # Update the branch to point to this new commit
        main_branch_path = os.path.join(self.heads_dir, self.main_branch)
        with open(main_branch_path, "w") as f:
            f.write(commit_sha)  # point the branch to the new commit

        # Show a confirmation message with the commit ID and message
        print(f"[{self.main_branch} {commit_sha[:7]}] {message}")
        del self.staged_content  # Clear staging after commit


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="A basic Git-like tool (v1)")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # 'init' command
    init_parser = subparsers.add_parser("init", help="Initialize a new repository")

    # 'add' command
    add_parser = subparsers.add_parser("add", help="Add file to be tracked")
    add_parser.add_argument("path", help="Path to the file")

    # 'commit' command
    commit_parser = subparsers.add_parser(
        "commit", help="Record changes to the repository"
    )
    commit_parser.add_argument("message", help="Commit message")

    args = parser.parse_args()

    # Initialize instance of BasicGit class
    basic_git = BasicGit()

    if args.command == "init":
        basic_git.init()
    elif args.command == "add":
        basic_git.add(args.path)
    elif args.command == "commit":
        basic_git.commit(args.message)
    elif args.command is None:
        parser.print_help()
        sys.exit(1)
    else:
        print(f"Unknown command: {args.command}")
        sys.exit(1)
