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
        Set up a new Git-like system to track changes to files.
        This creates a basic folder structure to store versions of our code.
        """
        self.root_path = os.path.abspath(
            root_path
        )  # get the full folder path where our code lives
        self.gitdir = os.path.join(
            self.root_path, ".basicgit2"
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
        self.index_file = os.path.join(
            self.gitdir, "index"
        )  # file to track staged files

    def init(self):
        """Initialize a new repository."""
        if os.path.exists(self.gitdir):
            print(f"Repository already exists at {self.gitdir}")
            return

        # Create all the folders we need to store Git data
        os.makedirs(self.gitdir, exist_ok=True)
        os.makedirs(self.objects_dir, exist_ok=True)
        os.makedirs(self.heads_dir, exist_ok=True)

        # Create a HEAD file that points to our main branch
        with open(self.HEAD_file, "w") as f:
            f.write(f"ref: refs/heads/{self.main_branch}")

        # Create an empty main branch file
        main_branch_path = os.path.join(self.heads_dir, self.main_branch)
        with open(main_branch_path, "w") as f:
            f.write("")  # Start with no commits

        # Create an empty index file
        with open(self.index_file, "w") as f:
            f.write("")

        print(f"Initialized empty repository in {self.gitdir}")

    def _hash_object(self, data, obj_type="blob"):  # * [Step 2]: Added object type
        """
        Create a unique ID for the data using SHA-1 hashing, including object type.
        """
        encoded_data = data.encode("utf-8")
        header = f"{obj_type} {len(encoded_data)}\0".encode(
            "utf-8"
        )  # * [Step 2]: Added header
        store = header + encoded_data
        return hashlib.sha1(store).hexdigest()

    def _store_object(self, data, sha):  # * [Step 2]: Now compresses data
        """
        Save content in Git's storage system using its unique ID (hash), compressed.
        """
        obj_dir = os.path.join(self.objects_dir, sha[:2])
        obj_path = os.path.join(obj_dir, sha[2:])
        os.makedirs(obj_dir, exist_ok=True)
        compressed_data = zlib.compress(
            f"blob {len(data)}\0{data}".encode("utf-8")
        )  # * [Step 2]: Storing as blob with header and compressed
        with open(obj_path, "wb") as f:  # * [Step 2]: Use binary write mode
            f.write(compressed_data)

    def _read_object(
        self, sha
    ):  # * [Step 2]: New method to read and decompress objects
        """Read and decompress an object from the objects database."""
        obj_path = os.path.join(self.objects_dir, sha[:2], sha[2:])
        if not os.path.exists(obj_path):
            raise ValueError(f"Object {sha} not found")
        with open(obj_path, "rb") as f:  # * [Step 2]: Use binary read mode
            compressed = f.read()
        decompressed = zlib.decompress(compressed).decode("utf-8")
        null_index = decompressed.find("\0")
        header = decompressed[:null_index]
        content = decompressed[null_index + 1 :]
        obj_type, size = header.split()
        return obj_type, content

    def add(self, path):
        """Add a file to be tracked."""
        abs_path = os.path.abspath(path)
        if not os.path.exists(abs_path):
            print(f"Error: {path} does not exist")
            return

        # For simplicity, still just storing the path in the index for now
        with open(self.index_file, "w") as f:
            f.write(path)

        print(f"Added {path}")

    def _get_current_commit(self):  # * [Step 2]: Helper to get the current commit SHA
        """Get the SHA of the current commit on the main branch."""
        main_branch_path = os.path.join(self.heads_dir, self.main_branch)
        if os.path.exists(main_branch_path):
            with open(main_branch_path, "r") as f:
                return f.read().strip()
        return None

    def commit(self, message):
        """Save the staged changes with a message and link to previous commit."""
        # Check if there's anything staged (path in index file)
        try:
            with open(self.index_file, "r") as f:
                staged_path = f.read().strip()
        except FileNotFoundError:
            print("No changes to commit")
            return

        if not staged_path:
            print("No changes to commit")
            return

        abs_staged_path = os.path.abspath(staged_path)
        if not os.path.exists(abs_staged_path):
            print(f"Error: Staged file '{staged_path}' not found.")
            with open(self.index_file, "w") as f:
                f.write("")
            return

        with open(abs_staged_path, "r") as f:
            content = f.read()
        # Create a "blob" object
        blob_sha = self._hash_object(content)
        self._store_object(content, blob_sha)  # save the content as a blob

        # Create commit metadata
        commit_data = {
            "message": message,
            "timestamp": int(time.time()),
            "file": {staged_path: blob_sha},
            "parent": self._get_current_commit(),  # * [Step 2]: Add parent commit
        }

        # Convert commit data to JSON
        commit_string = json.dumps(commit_data)
        # Hash the commit object
        commit_sha = self._hash_object(
            commit_string, obj_type="commit"
        )  # * [Step 2]: Commit is also an object
        self._store_object(commit_string, commit_sha)  # save the commit object

        # Update the main branch to point to this new commit
        main_branch_path = os.path.join(self.heads_dir, self.main_branch)
        with open(main_branch_path, "w") as f:
            f.write(commit_sha)

        print(f"[{self.main_branch} {commit_sha[:7]}] {message}")

        # Clear the index after commit
        with open(self.index_file, "w") as f:
            f.write("")

    def status(self):  # * [Step 2]: Implement the status command
        """Show the working tree status."""
        try:
            with open(self.index_file, "r") as f:
                staged_file = f.read().strip()
        except FileNotFoundError:
            staged_file = None

        print("Changes to be committed:")
        if staged_file:
            print(f"  staged:   {staged_file}")
        else:
            print("  (no changes staged)")

        # For simplicity in Stage 2, we're not tracking unstaged changes yet.
        print("\nUntracked files:")
        # This would require comparing working directory with last commit, which is for later stages.
        print("  (not yet implemented)")

    def _log_commit(self, commit_sha):  # * [Step 2]: Helper to display a single commit
        """Display information for a given commit SHA."""
        try:
            obj_type, commit_content = self._read_object(commit_sha)
            if obj_type == "commit":
                commit_data = json.loads(commit_content)
                print(f"commit {commit_sha}")
                print(f"Timestamp: {commit_data['timestamp']}")
                print(f"Message: {commit_data['message']}")
                if "parent" in commit_data and commit_data["parent"]:
                    print(f"Parent: {commit_data['parent']}")
                print("")
                return commit_data.get("parent")
            else:
                print(f"Error: Expected commit object, got {obj_type}")
                return None
        except ValueError:
            print(f"Error reading commit object {commit_sha}")
            return None

    def log(self):  # * [Step 2]: Implement the log command
        """Display commit history."""
        current_commit = self._get_current_commit()
        if not current_commit:
            print("No commits yet.")
            return

        while current_commit:
            current_commit = self._log_commit(current_commit)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="A basic Git-like tool (Stage 2)")
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

    # 'status' command
    status_parser = subparsers.add_parser("status", help="Show the working tree status")

    # 'log' command
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
