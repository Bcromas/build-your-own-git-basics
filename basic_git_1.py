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
        gitdir_exists = None # YOUR CODE HERE
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
        os.makedirs(None, exist_ok=True)  # YOUR CODE HERE - Create the main repository directory
        os.makedirs(None, exist_ok=True)  # YOUR CODE HERE - Create the objects directory
        os.makedirs(None, exist_ok=True)  # YOUR CODE HERE - Create the heads directory

        # --- Task 1.3: Create the HEAD file ---
        # Create a 'HEAD' file in the repository's directory.
        # Write the path to the main branch's head reference (e.g., "refs/heads/<main/master branch name>") into this file.
        with open(None, "w") as f: # YOUR CODE HERE - Replace None
            f.write(None) # YOUR CODE HERE - Replace None

        # --- Task 1.4: Create the main branch file ---
        # Create a file representing the main branch (e.g., 'main' or 'master')
        # within the branch references directory ('self.heads_dir'). This file
        # will eventually store the commit hash of the latest commit on this branch.
        # Initialize this file as empty, indicating no commits yet.
        main_branch_path = os.path.join(None, None) # YOUR CODE HERE - Construct the path to the main branch file
        try:
            with open(None, "w") as f: # YOUR CODE HERE - Open the main branch file in write mode
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
        # --- Task 3.1: Encode data to bytes ---
        # The 'hashlib' library requires bytes. Encode the input 'data' using UTF-8
        # and store the result in 'encoded_data'.
        encoded_data = None # YOUR CODE HERE
        if encoded_data is None:
            raise NotImplementedError(
                "Task 3.1: Encode the data to bytes using UTF-8."
            )

        # --- Task 3.2: Compute SHA-1 hash as hexadecimal ---
        # Use 'hashlib.sha1()' to hash 'encoded_data'. Then, get the hex digest
        # using '.hexdigest()' and store it in 'hex_hash'.
        hash_object = None # YOUR CODE HERE
        hex_hash = None # YOUR CODE HERE
        if hex_hash is None:
            raise NotImplementedError(
                "Task 3.2: Compute the SHA-1 hash and return its hexadecimal representation."
            )
        return hex_hash

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
        # --- Task 4.1: Construct the object directory path ---
        # Use 'self.objects_dir' and the first two characters of 'sha'.
        obj_dir = None # YOUR CODE HERE
        if obj_dir is None:
            raise NotImplementedError("Task 4.1: Constructing the object directory path is not implemented.")

        # --- Task 4.2: Construct the object file path ---
        # Use the 'obj_dir' and the remaining characters of 'sha'.
        obj_path = None # YOUR CODE HERE
        if obj_path is None:
            raise NotImplementedError("Task 4.2: Constructing the object file path is not implemented.")

        os.makedirs(obj_dir, exist_ok=True)
        with open(obj_path, "w") as f:
            f.write(data)

    def add(self, path: str) -> None:
        """
        Stage a file to be tracked for the next commit.

        This command adds the specified file to the staging area (index).
        In this version, only a single file can be staged at a time.

        Args:
            path (str): The path to the file to be added.
        """
        abs_path = os.path.abspath(path)

        # --- Task 2.1: Check if the absolute path exists ---
        # Check if the file specified by the absolute path ('abs_path') exists.
        # If it does not exist, print an error message and return.
        path_exists = None # YOUR CODE HERE
        if path_exists is None:
            raise NotImplementedError(
                "Task 2.1: Checking if the specified path exists is not implemented."
            )
        if not path_exists:
            print(f"Error: {path} does not exist")
            return

        # --- Task 2.2: Write the absolute path to the index file ---
        # Open the index file and write the absolute path of the staged file into it.
        try:
            with open(None, "w") as f: # YOUR CODE HERE
                f.write(None) # YOUR CODE HERE
        except Exception as e:
            raise NotImplementedError(
                f"Task 2.2: Writing the path to the index file encountered an error: {e}"
            )

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

        # --- Task 5.1: Represent and store the commit ---
        # Obtain a string representation of the commit data. Generate a unique
        # identifier for this string using a hashing function.
        commit_string = None # YOUR CODE HERE - Get string representation of commit_data
        if commit_string is None:
            raise NotImplementedError("Task 5.1: Getting string representation of commit data is not implemented.")

        commit_sha = None # YOUR CODE HERE - Hash the commit string
        if commit_sha is None:
            raise NotImplementedError("Task 5.1: Hashing the commit string is not implemented.")

        self._store_object(commit_string, commit_sha)  # save the commit string and hash

        # --- Task 5.2: Update the branch pointer ---
        # Construct the reference to the current branch. Open this reference
        # and update it to point to the newly created commit.
        main_branch_path = os.path.join(None, None) # YOUR CODE HERE - Construct branch reference path
        try:
            with open(None, "w") as f: # YOUR CODE HERE - Open branch reference for writing
                f.write(None)  # YOUR CODE HERE - Write the new commit hash
        except Exception as e:
            raise NotImplementedError(f"Task 5.2: Updating the branch pointer encountered an error: {e}")

        # Show a confirmation message with the commit ID and message
        print(f"[{self.main_branch} {commit_sha[:7]}] {message}")

        # --- Task 5.3: Clear the staging area ---
        # Open the index file and write an empty string to clear it.
        try:
            with open(None, "w") as f: # YOUR CODE HERE - Open index file for writing
                f.write("") # Clear index by writing empty string
        except Exception as e:
            raise NotImplementedError(f"Task 5.3: Clearing the staging area encountered an error: {e}")


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
