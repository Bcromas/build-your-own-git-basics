import argparse
import hashlib
import os
import sys
import time


class BasicGit:
    def __init__(self, root_path="."):
        """
        Set up a Git-like system to track changes to files.
        This creates a basic folder structure to store versions of our code.
        """
        self.root_path = os.path.abspath(
            root_path
        )  # get the full folder path where our code lives
        self.gitdir = os.path.join(
            self.root_path, ".basicgit1"
        )  # create a hidden folder to store all Git data
        self.refs_dir = os.path.join(
            self.gitdir, "refs"
        )  # directory for organizing references
        self.heads_dir = os.path.join(
            self.refs_dir, "heads"
        )  # directory to store the tip of the main development line
        self.HEAD_file = os.path.join(
            self.gitdir, "HEAD"
        )  # file indicating the currently active branch
        self.main_branch = "main"  # the default name for the initial branch
        self.objects_dir = os.path.join(
            self.gitdir, "objects"
        )  # directory to store all committed objects
        self.index_file = os.path.join(
            self.gitdir, "index"
        )  # file to (temporarily) track staged files

    def init(self) -> None:
        """
        Initialize a new repository.

        This command sets up the necessary directory structure (.basicgit1)
        to begin tracking changes in the current directory.
        """
        # --- Task 1.1: Check if the repository directory exists ---
        # Check if the main repository directory already exists
        # If it does, print a message and stop the initialization.
        gitdir_exists = os.path.exists(self.gitdir) # YOUR CODE HERE
        if gitdir_exists is None:
            raise NotImplementedError(
                "Task 1.1: Checking if the main repository directory exists is not implemented."
            )
        if gitdir_exists:
            print(f"Repository already exists at {self.gitdir}")
            return

        # --- Task 1.2: Create repository directories ---
        # Establish the foundational directory structure for the repository, ensuring that if a directory already exists, no error is raised.
        # Hint: reference the __init__ method
        os.makedirs(self.gitdir, exist_ok=True)  # YOUR CODE HERE - Create the main repository directory
        os.makedirs(self.objects_dir, exist_ok=True)  # YOUR CODE HERE - Create the objects directory
        os.makedirs(self.heads_dir, exist_ok=True)  # YOUR CODE HERE - Create the heads directory

        # --- Task 1.3: Create the HEAD file ---
        # Create a 'HEAD' file in the repository's directory.
        # Write the path to the main branch's head reference (e.g., "refs/heads/<main/master branch name>") into this file.
        with open(self.HEAD_file, "w") as f: # YOUR CODE HERE - Replace None
            f.write(f"refs/heads/{self.main_branch}") # YOUR CODE HERE - Replace None

        # --- Task 1.4: Create the main branch file ---
        # Create a file representing the main branch (e.g., 'main' or 'master')
        # within the branch references directory ('self.heads_dir'). This file
        # will eventually store the commit hash of the latest commit on this branch.
        # Initialize this file as empty, indicating no commits yet.
        main_branch_path = os.path.join(self.heads_dir, self.main_branch) # YOUR CODE HERE - Construct the path to the main branch file
        try:
            with open(main_branch_path, "w") as f: # YOUR CODE HERE - Open the main branch file in write mode
                f.write("")  # Start with no commits
        except Exception as e:
            raise NotImplementedError(
                f"Task 1.4: Creating the main branch file encountered an error: {e}"
            )

        # Create an empty index file to track staged files
        with open(self.index_file, "w") as f:
            f.write("")

        print(f"Initialized empty repository in {self.gitdir}")

    def _hash_object(self, data: str) -> str:
        """
        Generate a unique ID (SHA-1 hash) for the provided data.

        This private helper method takes string data, encodes it, and then
        computes its SHA-1 hash, returning the hexadecimal representation
        of the hash.

        Args:
            data (str): The string data to be hashed.

        Returns:
            str: The hexadecimal representation of the SHA-1 hash.
        """
        encoded_data = data.encode(
            "utf-8"
        )  # convert the text to computer-friendly format
        return hashlib.sha1(
            encoded_data
        ).hexdigest()  # create a unique fingerprint for this content

    def _store_object(self, data: str, sha: str) -> None:
        """
        Store data in the object database using its SHA-1 hash.

        This private helper method saves the provided data into a file within
        the repository's object directory. The file's name is based on the
        SHA-1 hash of the data, and the objects are organized into subdirectories
        based on the first two characters of the hash for efficiency.

        Args:
            data (str): The string data to be stored.
            sha (str): The SHA-1 hash of the data, used as the filename.
        """
        obj_dir = os.path.join(
            self.objects_dir, sha[:2]
        )  # use first 2 characters of hash as folder name
        obj_path = os.path.join(obj_dir, sha[2:])  # use rest of hash as the filename
        os.makedirs(obj_dir, exist_ok=True)  # create the folder if it doesn't exist
        with open(obj_path, "w") as f:  # open a file to save the content
            f.write(data)  # save the actual content to disk for later retrieval

    def add(self, path: str) -> None:
        """
        Stage a file to be tracked for the next commit.

        This command adds the specified file to the staging area (index).
        In this version, only a single file can be staged at a time.

        Args:
            path (str): The path to the file to be added.
        """
        abs_path = os.path.abspath(path)
        if not os.path.exists(abs_path):
            print(f"Error: {path} does not exist")
            return

        with open(self.index_file, "w") as f:
            f.write(path)  # Write the file path to the index

        print(f"Added {path}")

    def commit(self, message: str) -> None:
        """
        Record changes to the repository with a message.

        This operation takes the currently staged file (only a single file is
        tracked in this version) and saves it as a new commit in the repository
        history on the 'main' branch.

        Args:
            message (str): A description of the changes being committed.
        """
        # Check if there's anything staged to commit by reading the index file
        try:
            with open(self.index_file, "r") as f:
                # Read the content of the index file and remove any leading/trailing whitespace
                staged_path = f.read().strip()
        except FileNotFoundError:
            print("No changes staged for commit. The staging area is empty or missing.")
            return

        if not staged_path:
            print("No changes to commit")
            return

        abs_staged_path = os.path.abspath(staged_path)
        if not os.path.exists(abs_staged_path):
            print(f"Staged file '{staged_path}' not found. Clearing the index.")
            # Clear the index
            with open(self.index_file, "w") as f:
                f.write("")
            return

        with open(abs_staged_path, "r") as f:
            content = f.read()
        # Create a "blob" by hashing the content
        blob_sha = self._hash_object(content)
        self._store_object(content, blob_sha)  # save the content

        # Create a commit object with message, timestamp, and file information
        commit_data = {
            "message": message,
            "timestamp": int(time.time()),
            "file": {staged_path: blob_sha},
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

        # Clear the index after a successful commit
        with open(self.index_file, "w") as f:
            f.write("")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="A basic Git-like tool (v1 - single file tracking)"
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    init_parser = subparsers.add_parser("init", help="Initialize a new repository")

    add_parser = subparsers.add_parser("add", help="Add file to be tracked")
    add_parser.add_argument("path", help="Path to the file")

    commit_parser = subparsers.add_parser(
        "commit", help="Record changes to the repository with a message."
    )
    commit_parser.add_argument("message", help="Commit message")

    args = parser.parse_args()

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
