import argparse
import hashlib
import json
import os
import sys
import time
import zlib


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
            self.root_path, ".basicgit2"
        )  # create a hidden folder to store all Git data
        self.refs_dir = os.path.join(
            self.gitdir, "refs"
        )  # directory for organizing references
        self.heads_dir = os.path.join(
            self.refs_dir, "heads"
        )  # directory to store the tip of the main development line as a file containing its latest commit SHA
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

        This command sets up the necessary directory structure (.basicgit2)
        to begin tracking changes in the current directory. This version uses a
        symbolic HEAD reference, which is a step towards supporting branching.
        """
        if os.path.exists(self.gitdir):
            print(f"Repository already exists at {self.gitdir}")
            return

        # Create all the folders we need to store Git data
        os.makedirs(self.gitdir, exist_ok=True)
        os.makedirs(self.objects_dir, exist_ok=True)
        os.makedirs(self.heads_dir, exist_ok=True)

        # --- Task 1: Create a symbolic HEAD reference ---
        # Create a 'HEAD' file in the repository's directory.
        # Write a symbolic reference within this file that indicates the
        # currently active branch. This reference should point to the
        # head reference of the main branch. The format for a symbolic
        # reference starts with 'ref:' followed by the path to the
        # referenced file.
        with open(self.HEAD_file, "w") as f: # YOUR CODE HERE - Replace None
            f.write(f"ref: refs/heads/{self.main_branch}") # YOUR CODE HERE - Replace None

        # Create an empty main branch file
        main_branch_path = os.path.join(self.heads_dir, self.main_branch)
        with open(main_branch_path, "w") as f:
            f.write("")  # Start with no commits

        # Create an empty index file to track staged files
        with open(self.index_file, "w") as f:
            f.write("")

        print(f"Initialized empty repository in {self.gitdir}")

    def _hash_object(self, data: str, obj_type: str = "blob") -> str:
        """
        Generate a unique ID (SHA-1 hash) for the provided data, including its type.

        This private helper method takes string data and an object type,
        constructs a content string that includes the type and length of the
        data, encodes it, and then computes its SHA-1 hash. This ensures that
        objects of different types with the same content have different IDs.

        Args:
            data (str): The string data to be hashed.
            obj_type (str, optional): The type of the object ('blob' or 'commit').
                Defaults to "blob".

        Returns:
            str: The hexadecimal representation of the SHA-1 hash.
        """
        encoded_data = data.encode(
            "utf-8"
        )  # convert the text to computer-friendly format
        header = f"{obj_type} {len(encoded_data)}\0".encode("utf-8")
        store = header + encoded_data
        return hashlib.sha1(
            store
        ).hexdigest()  # create a unique fingerprint for this content

    def _store_object(self, data: str, sha: str, obj_type: str = "blob") -> None:
        """
        Store data in the object database using its SHA-1 hash, with compression.

        This private helper method saves the provided data into a compressed
        file within the repository's object directory. The file's name is based
        on the SHA-1 hash of the data, and the objects are organized into
        subdirectories based on the first two characters of the hash for
        efficiency. The stored data is prefixed with its type and length and
        then compressed using zlib.

        Args:
            data (str): The string data to be stored.
            sha (str): The SHA-1 hash of the data, used as the filename.
            obj_type (str, optional): The type of the object ('blob' or 'commit').
                Defaults to "blob".
        """
        obj_dir = os.path.join(
            self.objects_dir, sha[:2]
        )  # use first 2 characters of hash as folder name
        obj_path = os.path.join(obj_dir, sha[2:])  # use rest of hash as the filename
        os.makedirs(obj_dir, exist_ok=True)  # create the folder if it doesn't exist
        # storing as blob with header and compressed
        compressed_data = zlib.compress(
            f"{obj_type} {len(data)}\0{data}".encode("utf-8")
        )
        with open(obj_path, "wb") as f:  # open a file to save the compressed content
            f.write(
                compressed_data
            )  # save the compressed content to disk for later retrieval

    def _read_object(self, sha: str) -> tuple[str, str]:
        """
        Read and decompress an object from the object database.

        This private helper method retrieves a compressed object from the
        repository's object directory based on its SHA-1 hash. It decompresses
        the object using zlib and parses the header to determine the object type
        and original size.

        Args:
            sha (str): The SHA-1 hash of the object to retrieve.

        Returns:
            tuple[str, str]: A tuple containing the object type (e.g., 'blob', 'commit')
                            and the decompressed content of the object as a string.

        Raises:
            ValueError: If the object with the given SHA-1 hash is not found
                        in the object database.
        """
        obj_path = os.path.join(self.objects_dir, sha[:2], sha[2:])
        if not os.path.exists(obj_path):
            raise ValueError(f"Object {sha} not found")
        with open(obj_path, "rb") as f:  # use binary read mode
            compressed = f.read()
        decompressed = zlib.decompress(compressed).decode("utf-8")
        null_index = decompressed.find("\0")
        header = decompressed[:null_index]
        content = decompressed[null_index + 1 :]
        obj_type, size = header.split()
        return obj_type, content

    def add(self, paths: list[str] | str) -> None:
        """
        Stage one or more files to be tracked for the next commit.

        This command adds the specified file(s) to the staging area (index).
        This version supports adding multiple files at once.

        Args:
            paths (list[str] | str): A single path (string) or a list of paths
                                    (list of strings) to the files to be added.
        """
        if not isinstance(paths, list):
            paths = [paths]
        with open(self.index_file, "a") as f:
            for path in paths:
                abs_path = os.path.abspath(path)
                if not os.path.exists(abs_path):
                    print(f"Error: {path} does not exist")
                    continue  # Continue to process other paths
                f.write(path + "\n")  # Append the file path and a newline to the index
                print(f"Added {path}")

    def _get_current_commit(self) -> str | None:
        """
        Get the SHA-1 hash of the current commit on the 'main' branch.

        This private helper method reads the content of the 'main' branch file
        in the 'refs/heads' directory, which stores the SHA-1 hash of the
        latest commit on that branch.

        Returns:
            str | None: The SHA-1 hash of the current commit as a string,
                        or None if the 'main' branch file does not exist
                        (e.g., in a newly initialized repository with no commits).
        """
        # Get the full path to the 'main' branch file
        main_branch_path = os.path.join(self.heads_dir, self.main_branch)
        # Check if the 'main' branch file exists
        if os.path.exists(main_branch_path):
            # Open the 'main' branch file in read mode
            with open(main_branch_path, "r") as f:
                # Read the commit SHA from the file and strip leading/trailing whitespace
                return f.read().strip()
        return None

    def commit(self, message: str) -> None:
        """
        Record changes to the repository with a message.

        This operation takes all currently staged files and saves them as a new
        commit in the repository history on the 'main' branch. This version
        tracks multiple files and includes information about the previous commit
        in the history.

        Args:
            message (str): A description of the changes being committed.
        """
        staged_files = []
        # Check if there's anything staged to commit by reading the index file
        try:
            with open(self.index_file, "r") as f:
                # Read all lines from the index file, strip whitespace from each,
                # and keep only the non-empty lines (representing staged files)
                staged_files = [line.strip() for line in f.readlines() if line.strip()]
        except FileNotFoundError:
            print("No changes staged for commit. The staging area is empty or missing.")
            return

        if not staged_files:
            print("No changes to commit")
            return

        files_to_commit = {}
        for staged_path in staged_files:
            abs_staged_path = os.path.abspath(staged_path)
            if not os.path.exists(abs_staged_path):
                print(
                    f"Staged file '{staged_path}' not found. Continuing with next file."
                )
                continue  # Skip missing files, process the rest
            try:
                with open(abs_staged_path, "r") as f:
                    content = f.read()
                # Create a "blob" by hashing the content
                blob_sha = self._hash_object(content)
                self._store_object(content, blob_sha)  # save the content
                files_to_commit[staged_path] = blob_sha
            except Exception as e:
                print(f"Error processing file '{staged_path}': {e}")

        if not files_to_commit:  # Check if any files were actually committed
            print("No valid files to commit.")
            return

        commit_data = {
            "message": message,
            "timestamp": int(time.time()),
            "files": files_to_commit,
            "parent": self._get_current_commit(),
        }

        commit_string = json.dumps(commit_data)
        # Hash the commit string
        commit_sha = self._hash_object(commit_string, obj_type="commit")
        self._store_object(
            commit_string, commit_sha, obj_type="commit"
        )  # save the commit string and hash

        # Update the branch to point to this new commit
        main_branch_path = os.path.join(self.heads_dir, self.main_branch)
        with open(main_branch_path, "w") as f:
            f.write(commit_sha)  # point the branch to the new commit

        # Show a confirmation message with the commit ID and message
        print(f"[{self.main_branch} {commit_sha[:7]}] {message}")

        # Clear the index after a successful commit
        with open(self.index_file, "w") as f:
            f.write("")

    def status(self) -> None:
        """
        Show the status of the working tree and staging area.

        This command displays information about files that have been staged
        for the next commit. It indicates which files are currently in the
        staging area. This version does not yet track unstaged changes or
        list untracked files.
        """
        try:
            with open(self.index_file, "r") as f:
                staged_files = [line.strip() for line in f if line.strip()]
        except FileNotFoundError:
            staged_files = []

        print("Changes to be committed:")
        if staged_files:
            for file in staged_files:
                print(f"  staged:   {file}")
        else:
            print("  (no changes staged)")

        # For simplicity, we're not tracking unstaged changes which would require comparing working directory with last commit
        print("\nUntracked files:")
        print("  (not yet implemented)")

    def _log_commit(self, commit_sha: str) -> str | None:
        """
        Display detailed information for a specific commit SHA-1 hash.

        This private helper method retrieves and displays the details of a commit
        object from the object database. The information includes the commit's
        SHA-1 hash, timestamp, commit message, parent commit (if any), and the
        files changed in this commit along with their blob SHA-1 hashes.

        Args:
            commit_sha (str): The SHA-1 hash of the commit object to display.

        Returns:
            str | None: The SHA-1 hash of the parent commit, or None if there
                        is no parent commit or if the object is not a commit.
        """
        try:
            # Read the object from the database using its SHA-1 hash
            obj_type, commit_content = self._read_object(commit_sha)
            # Check if the retrieved object is a commit
            if obj_type == "commit":
                # Parse the commit content from JSON
                commit_data = json.loads(commit_content)
                print(f"commit {commit_sha}")
                print(f"Timestamp: {commit_data['timestamp']}")
                print(f"Message: {commit_data['message']}")
                # Check if the commit has a parent commit
                if "parent" in commit_data and commit_data["parent"]:
                    print(f"Parent: {commit_data['parent']}")
                print("Files:")
                # Iterate through the files included in this commit
                for file, sha in commit_data.get("files", {}).items():
                    print(f"  {file}: {sha[:7]}")
                print("")
                # Return the SHA-1 hash of the parent commit
                return commit_data.get("parent")
            else:
                # If the object is not a commit, print an error message
                print(f"Expected commit object, got {obj_type}")
                return None
        except ValueError:
            # Handle the case where the commit object could not be read
            print(f"Error reading commit object {commit_sha}")
            return None

    def log(self) -> None:
        """
        Display the commit history of the 'main' branch.

        This command traverses the commit history starting from the most recent
        commit on the 'main' branch and displays the details of each commit
        by calling the '_log_commit' method. It continues until the initial
        commit or the beginning of the history is reached.
        """
        # Get the SHA-1 hash of the most recent commit on the 'main' branch
        current_commit = self._get_current_commit()
        # If there are no commits yet, inform the user and exit
        if not current_commit:
            print("No commits yet.")
            return

        # Loop through the commit history, starting from the current commit
        while current_commit:
            # Display the details of the current commit and get the SHA-1 hash of its parent
            current_commit = self._log_commit(current_commit)
            # The loop continues with the parent commit until there are no more parents (None is returned)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="A basic Git-like tool (v2 - multiple files, compression)"
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    init_parser = subparsers.add_parser("init", help="Initialize a new repository")

    add_parser = subparsers.add_parser("add", help="Add file(s) to be tracked")
    add_parser.add_argument("path", nargs="+", help="Path to the file(s) to add")

    commit_parser = subparsers.add_parser(
        "commit", help="Record changes to the repository with a message."
    )
    commit_parser.add_argument("message", help="Commit message")

    status_parser = subparsers.add_parser("status", help="Show the working tree status")

    log_parser = subparsers.add_parser("log", help="Show commit logs")

    args = parser.parse_args()

    basic_git = BasicGit()

    if args.command == "init":
        basic_git.init()
    elif args.command == "add":
        basic_git.add(args.path)
    elif args.command == "commit":
        basic_git.commit(args.message)
    elif args.command == "status":
        basic_git.status()
    elif args.command == "log":
        basic_git.log()
    elif args.command is None:
        parser.print_help()
        sys.exit(1)
    else:
        print(f"Unknown command: {args.command}")
        sys.exit(1)
