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
            f.write(
                f"ref: refs/heads/{self.main_branch}"
            )  # * implement symbolic reference where the commit SHA is stored in a branch's file, helpful for implementing branching later

        # Create an empty main branch file
        main_branch_path = os.path.join(self.heads_dir, self.main_branch)
        with open(main_branch_path, "w") as f:
            f.write("")  # Start with no commits

        # Create an empty index file to track staged files
        with open(self.index_file, "w") as f:
            f.write("")

        print(f"Initialized empty repository in {self.gitdir}")

    def _hash_object(self, data, obj_type="blob"):  # * add hint & leave incomplete re: new obj_type param
        """
        Create a unique ID for the data using SHA-1 hashing, including object type.
        This converts any content into a fixed-length string of characters
        used to identify and track files.

        Note: Methods starting with underscore (_) are considered "private" in Python.
        This means they're helper methods called by other public methods without an underscore prefix.
        """
        encoded_data = data.encode(
            "utf-8"
        )  # convert the text to computer-friendly format
        header = f"{obj_type} {len(encoded_data)}\0".encode(
            "utf-8"
        )  # * add hint & leave incomplete
        store = header + encoded_data
        return hashlib.sha1(
            store
        ).hexdigest()  # create a unique fingerprint for this content #* add hint & leave incomplete

    def _store_object(self, data, sha):
        """
        Save content in Git's storage system using its unique ID (hash), compressed.
        We'll organize files into folders based on the first two characters of the hash to avoid having too many files in one place.
        """
        obj_dir = os.path.join(
            self.objects_dir, sha[:2]
        )  # use first 2 characters of hash as folder name
        obj_path = os.path.join(obj_dir, sha[2:])  # use rest of hash as the filename
        os.makedirs(obj_dir, exist_ok=True)  # create the folder if it doesn't exist
        compressed_data = zlib.compress(
            f"blob {len(data)}\0{data}".encode("utf-8")
        )  # storing as blob with header and compressed #* add hint & leave incomplete
        with open(obj_path, "wb") as f:  # use binary write mode
            f.write(
                compressed_data
            )  # save the compressed content to disk for later retrieval #* add hint & leave incomplete

    def _read_object(self, sha):
        """Read and decompress an object from the objects database."""
        obj_path = os.path.join(self.objects_dir, sha[:2], sha[2:])
        if not os.path.exists(obj_path):
            raise ValueError(f"Object {sha} not found")
        with open(obj_path, "rb") as f:  # use binary read mode
            compressed = f.read()
        decompressed = zlib.decompress(compressed).decode(
            "utf-8"
        )  # * add hint & leave incomplete
        null_index = decompressed.find("\0")  # * add hint & leave incomplete
        header = decompressed[:null_index]  # * add hint & leave incomplete
        content = decompressed[null_index + 1 :]  # * add hint & leave incomplete
        obj_type, size = header.split()
        return obj_type, content

    # def add(self, path):
    #     """Add a file to be tracked."""
    #     abs_path = os.path.abspath(path)
    #     if not os.path.exists(abs_path):
    #         print(f"Error: {path} does not exist")
    #         return

    #     # Store the path of the added file in the index file
    #     with open(self.index_file, "w") as f:
    #         f.write(path)

    #     print(f"Added {path}")
    def add(self, paths):
        """Add one or more files to be tracked."""
        if not isinstance(paths, list):
            paths = [paths]
        with open(self.index_file, "a") as f:
            for path in paths:
                abs_path = os.path.abspath(path)
                if not os.path.exists(abs_path):
                    print(f"Error: {path} does not exist")
                    continue
                f.write(path + "\n")
                print(f"Added {path}")

    def _get_current_commit(self):
        """Get the SHA of the current commit on the main branch."""
        main_branch_path = os.path.join(
            self.heads_dir, self.main_branch
        )  # * add hint & leave incomplete
        if os.path.exists(main_branch_path):
            with open(main_branch_path, "r") as f:
                return f.read().strip()
        return None

    # def commit(self, message):
    #     """Save the staged changes with a message and link to previous commit."""
    #     # Check if there's anything staged (path in index file)
    #     try:
    #         with open(self.index_file, "r") as f:
    #             staged_path = f.read().strip()
    #     except FileNotFoundError:
    #         print("No changes to commit")
    #         return

    #     if not staged_path:
    #         print("No changes to commit")
    #         return

    #     abs_staged_path = os.path.abspath(staged_path)
    #     if not os.path.exists(abs_staged_path):
    #         print(f"Error: Staged file '{staged_path}' not found.")
    #         # Clear the index
    #         with open(self.index_file, "w") as f:
    #             f.write("")
    #         return

    #     with open(abs_staged_path, "r") as f:
    #         content = f.read()
    #     # Create a "blob" by hashing the content
    #     blob_sha = self._hash_object(content)
    #     self._store_object(content, blob_sha)  # save the content

    #     # Create commit metadata
    #     commit_data = {
    #         "message": message,
    #         "timestamp": int(time.time()),
    #         "file": {staged_path: blob_sha},
    #         "parent": self._get_current_commit(),  # * add hint & leave incomplete
    #     }

    #     # Convert commit data to JSON
    #     commit_string = json.dumps(commit_data)
    #     # Hash the commit string
    #     commit_sha = self._hash_object(
    #         commit_string, obj_type="commit"
    #     )  # * add hint & leave incomplete
    #     self._store_object(commit_string, commit_sha)  # save the commit string and hash

    #     # Update the main branch to point to this new commit
    #     main_branch_path = os.path.join(self.heads_dir, self.main_branch)
    #     with open(main_branch_path, "w") as f:
    #         f.write(commit_sha)  # point the branch to the new commit

    #     print(f"[{self.main_branch} {commit_sha[:7]}] {message}")

    #     # Clear the index after a successful commit
    #     with open(self.index_file, "w") as f:
    #         f.write("")
    def commit(self, message):
        """Save the staged changes with a message and link to previous commit."""
        try:
            with open(self.index_file, "r") as f:
                staged_paths = [line.strip() for line in f if line.strip()]
        except FileNotFoundError:
            print("No changes to commit")
            return

        if not staged_paths:
            print("No changes to commit")
            return

        commit_files = {}
        for staged_path in staged_paths:
            abs_staged_path = os.path.abspath(staged_path)
            if not os.path.exists(abs_staged_path):
                print(f"Error: Staged file '{staged_path}' not found.")
                continue

            with open(abs_staged_path, "r") as f:
                content = f.read()
            blob_sha = self._hash_object(content)
            self._store_object(content, blob_sha)
            commit_files[staged_path] = blob_sha

        if not commit_files:
            print("No valid staged files to commit.")
            with open(self.index_file, "w") as f:
                f.write("")
            return

        commit_data = {
            "message": message,
            "timestamp": int(time.time()),
            "files": commit_files,
            "parent": self._get_current_commit(),
        }

        commit_string = json.dumps(commit_data)
        commit_sha = self._hash_object(commit_string, obj_type="commit")
        self._store_object(commit_string, commit_sha)

        main_branch_path = os.path.join(self.heads_dir, self.main_branch)
        with open(main_branch_path, "w") as f:
            f.write(commit_sha)

        print(f"[{self.main_branch} {commit_sha[:7]}] {message}")

        with open(self.index_file, "w") as f:
            f.write("")


    # def status(self):
    #     """Show the working tree status."""
    #     try:
    #         with open(self.index_file, "r") as f:
    #             staged_file = f.read().strip()  # * add hint & leave incomplete
    #     except FileNotFoundError:
    #         staged_file = None

    #     print("Changes to be committed:")
    #     if staged_file:
    #         print(f"  staged:   {staged_file}")
    #     else:
    #         print("  (no changes staged)")

    #     # For simplicity, we're not tracking unstaged changes which would require comparing working directory with last commit
    #     print("\nUntracked files:")
    #     print("  (not yet implemented)")
    def status(self):
        """Show the working tree status."""
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

        print("\nUntracked files:")
        print("  (not yet implemented)")

    # def _log_commit(self, commit_sha):
    #     """Display information for a given commit SHA."""
    #     try:
    #         obj_type, commit_content = self._read_object(commit_sha)
    #         if obj_type == "commit":
    #             commit_data = json.loads(commit_content)
    #             print(f"commit {commit_sha}")
    #             print(f"Timestamp: {commit_data['timestamp']}")
    #             print(f"Message: {commit_data['message']}")
    #             if "parent" in commit_data and commit_data["parent"]:
    #                 print(f"Parent: {commit_data['parent']}")
    #             print("")
    #             return commit_data.get("parent")  # * add hint & leave incomplete
    #         else:
    #             print(f"Error: Expected commit object, got {obj_type}")
    #             return None
    #     except ValueError:
    #         print(f"Error reading commit object {commit_sha}")
    #         return None
    def _log_commit(self, commit_sha):
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
                print("Files:")
                for file, sha in commit_data.get("files", {}).items():
                    print(f"  {file}: {sha[:7]}")
                print("")
                return commit_data.get("parent")
            else:
                print(f"Error: Expected commit object, got {obj_type}")
                return None
        except ValueError:
            print(f"Error reading commit object {commit_sha}")
            return None

    def log(self):
        """Display commit history."""
        current_commit = self._get_current_commit()
        if not current_commit:
            print("No commits yet.")
            return

        while current_commit:
            current_commit = self._log_commit(current_commit)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="A basic Git-like tool (v2)")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # 'init' command
    init_parser = subparsers.add_parser("init", help="Initialize a new repository")

    # 'add' command
    add_parser = subparsers.add_parser("add", help="Add file to be tracked")
    add_parser.add_argument(
        "path", nargs="+", help="Path to the file(s) to add"
    )  # Allow multiple paths

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

    raise Exception('remove commented out code but ensure helpful comments are copied over to the code replacing it before deleting')

    basic_git = BasicGit()

    if args.command == "init":
        basic_git.init()
    elif args.command == "add":
        basic_git.add(args.path)
    elif args.command == "commit":
        basic_git.commit(args.message)
    elif args.command == "status":
        basic_git.status() # * shows the current state of uncommitted/staged changes in index & unimplemented untracked files details
    elif args.command == "log":
        basic_git.log() # *
    elif args.command is None:
        parser.print_help()
        sys.exit(1)
    else:
        print(f"Unknown command: {args.command}")
        sys.exit(1)
