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
            self.root_path, ".basicgit3"
        )  # create a hidden folder to store all Git data
        self.refs_dir = os.path.join(
            self.gitdir, "refs"
        )  # directory for organizing references
        self.heads_dir = os.path.join(
            self.refs_dir, "heads"
        )  # directory to store the tips of development lines (branches) as files with their latest commit SHAs
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

    def init(self):
        """Initialize a new BasicGit repository."""
        if os.path.exists(self.gitdir):
            print(f"Repository already exists at {self.gitdir}")
            return  # * add hint: What should happen if the repository already exists?

        os.makedirs(self.gitdir, exist_ok=True)
        os.makedirs(self.objects_dir, exist_ok=True)
        os.makedirs(self.heads_dir, exist_ok=True)

        # Initialize HEAD to point to the main branch
        head_path = self.HEAD_file
        with open(head_path, "w") as f:
            f.write(f"ref: refs/heads/{self.main_branch}")  # Symbolic reference

        # Create the main branch file (initially empty as no commits yet)
        main_branch_path = os.path.join(self.heads_dir, self.main_branch)
        with open(main_branch_path, "w") as f:
            f.write(
                ""
            )  # * remove this line & add hint: What should the main branch file contain initially?

        # Create an empty index file
        with open(self.index_file, "w") as f:
            f.write("")

        print(f"Initialized empty repository in {self.gitdir}")

    def _hash_object(self, data, obj_type="blob"):
        """Generate a SHA-1 hash for the given data, including the object type."""
        encoded_data = data.encode("utf-8")
        header = f"{obj_type} {len(encoded_data)}\0".encode("utf-8")
        store = header + encoded_data
        return hashlib.sha1(store).hexdigest()

    def _store_object(self, data, sha, obj_type="blob"):
        """Store an object (data with its type) in the object database, compressed."""
        obj_dir = os.path.join(self.objects_dir, sha[:2])
        obj_path = os.path.join(obj_dir, sha[2:])
        os.makedirs(obj_dir, exist_ok=True)
        compressed_data = zlib.compress(
            f"{obj_type} {len(data)}\0{data}".encode("utf-8")
        )
        with open(obj_path, "wb") as f:
            f.write(compressed_data)

    def _read_object(self, sha):
        """Read and decompress an object from the object database."""
        obj_path = os.path.join(self.objects_dir, sha[:2], sha[2:])
        if not os.path.exists(obj_path):
            raise ValueError(f"Object {sha} not found")
        with open(obj_path, "rb") as f:
            compressed = f.read()
        decompressed = zlib.decompress(compressed).decode("utf-8")
        null_index = decompressed.find("\0")
        header = decompressed[:null_index]
        content = decompressed[null_index + 1 :]
        obj_type, size = header.split()
        return obj_type, content

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
                f.write(path + "\n")  # * add hint & leave incomplete
                print(f"Added {path}")

    def _get_current_branch(self):
        """Determine the currently active branch by reading the HEAD file."""
        try:
            with open(self.HEAD_file, "r") as f:
                content = f.read().strip()
                if content.startswith("ref: refs/heads/"):
                    return content[len("ref: refs/heads/") :]
        except FileNotFoundError:
            return None
        return None

    def _get_current_commit(self):
        """Get the SHA-1 of the commit that the current branch points to."""
        current_branch = self._get_current_branch()
        if not current_branch:
            return None  # In a detached HEAD state (not implemented fully here)
        branch_path = os.path.join(self.heads_dir, current_branch)
        if os.path.exists(branch_path):
            with open(branch_path, "r") as f:
                return f.read().strip()
        return None

    def commit(self, message):
        """Record changes to the repository."""
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
        blob_sha = self._hash_object(content)
        self._store_object(content, blob_sha)

        commit_data = {
            "message": message,
            "timestamp": int(time.time()),
            "file": {staged_path: blob_sha},
            "parent": self._get_current_commit(),
        }

        commit_string = json.dumps(commit_data)
        commit_sha = self._hash_object(commit_string, obj_type="commit")
        self._store_object(commit_string, commit_sha, obj_type="commit")

        current_branch = self._get_current_branch()
        if current_branch:
            branch_path = os.path.join(self.heads_dir, current_branch)
            with open(branch_path, "w") as f:
                f.write(commit_sha)  # Update the branch to point to the new commit
            print(f"[{current_branch} {commit_sha[:7]}] {message}")
        else:
            print(
                f"[detached HEAD {commit_sha[:7]}] {message}"
            )  # Handle detached HEAD state

        with open(self.index_file, "w") as f:
            f.write("")  # Clear the index after commit

    def branch(self, name=None, delete=None):
        """List, create, or delete branches."""
        if delete:
            branch_to_delete = delete
            branch_path = os.path.join(self.heads_dir, branch_to_delete)
            if os.path.exists(branch_path):
                if self._get_current_branch() == branch_to_delete:
                    print(
                        f"Cannot delete the currently checked-out branch '{branch_to_delete}'."
                    )
                    return
                os.remove(branch_path)
                print(f"Deleted branch '{branch_to_delete}'.")
            else:
                print(f"Branch '{branch_to_delete}' not found.")
            return

        if name:
            new_branch_name = name
            branch_path = os.path.join(self.heads_dir, new_branch_name)
            if os.path.exists(branch_path):
                print(f"Branch '{new_branch_name}' already exists.")
                return
            current_commit_sha = self._get_current_commit()
            with open(branch_path, "w") as f:
                f.write(current_commit_sha if current_commit_sha else "")
            print(f"Created branch '{new_branch_name}'.")
            return

        # List branches
        current_branch = self._get_current_branch()
        branches = []
        if os.path.exists(self.heads_dir):
            for filename in os.listdir(self.heads_dir):
                branches.append(filename)
        if branches:
            for branch in sorted(branches):
                prefix = "* " if branch == current_branch else "  "
                print(f"{prefix}{branch}")
        else:
            print(
                "No branches yet."
            )  # * remove this line & add hint: What is the default branch?

    def checkout(self, branch_name):
        """Switch to a different branch."""
        branch_path = os.path.join(self.heads_dir, branch_name)
        if os.path.exists(branch_path):
            head_path = self.HEAD_file
            with open(head_path, "w") as f:
                f.write(f"ref: refs/heads/{branch_name}")
            print(f"Switched to branch '{branch_name}'.")
            # * remove the next line & add hint: What else needs to happen during checkout?
            print(
                "(Note: Working directory update is not fully implemented in this version.)"
            )
        else:
            print(f"Error: Branch '{branch_name}' not found.")

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
        print(
            "  (not yet implemented)"
        )  # * add hint: How would you identify untracked files?

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
                print(f"Files:")
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
    parser = argparse.ArgumentParser(
        description="A basic Git-like tool (v3 - branching)"
    )
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

    # 'branch' command
    branch_parser = subparsers.add_parser(
        "branch", help="List, create, or delete branches"
    )
    branch_parser.add_argument("name", nargs="?", help="New branch name")
    branch_parser.add_argument(
        "-d", "--delete", dest="delete_branch", help="Delete a branch"
    )

    # 'checkout' command
    checkout_parser = subparsers.add_parser(
        "checkout", help="Switch branches or restore working tree files"
    )
    checkout_parser.add_argument("branch_name", help="Branch to checkout")

    # 'status' command
    status_parser = subparsers.add_parser("status", help="Show the working tree status")

    # 'log' command
    log_parser = subparsers.add_parser("log", help="Show commit logs")

    args = parser.parse_args()

    raise Exception('resolve issue with commit command')

    basic_git = BasicGit()

    if args.command == "init":
        basic_git.init()
    elif args.command == "add":
        basic_git.add(args.path)
    elif args.command == "commit":
        basic_git.commit(args.message)
    elif args.command == "branch":
        basic_git.branch(
            name=args.name, delete=args.delete_branch
        )  # * list branches, create a new one or delete a given branch
    elif args.command == "checkout":
        basic_git.checkout(args.branch_name)  # * switch to another branch
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
