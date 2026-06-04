import hashlib
import json
import os
import time

class GitLikeRepository:
    """
    Simulates a Git repository with basic version control functionality
    to illustrate Git as the 'single source of truth'.
    """
    def __init__(self, repo_path="mock_repo"):
        self.repo_path = repo_path
        os.makedirs(os.path.join(self.repo_path, "objects"), exist_ok=True)
        os.makedirs(os.path.join(self.repo_path, "branches"), exist_ok=True)
        self.head = os.path.join(self.repo_path, "branches", "main")
        if not os.path.exists(self.head):
            with open(self.head, "w") as f:
                f.write("") # Main branch initially points to no commit

    def _hash_content(self, content):
        """Generates a SHA-1 hash for content."""
        return hashlib.sha1(content.encode('utf-8')).hexdigest()

    def _write_object(self, content_type, content):
        """Writes an object (e.g., commit, blob) to the object store."""
        full_content = f"{content_type} {len(content)}\0{content}"
        obj_hash = self._hash_content(full_content)
        obj_path = os.path.join(self.repo_path, "objects", obj_hash)
        with open(obj_path, "w") as f:
            f.write(full_content)
        return obj_hash

    def _read_object(self, obj_hash):
        """Reads an object from the object store."""
        obj_path = os.path.join(self.repo_path, "objects", obj_hash)
        with open(obj_path, "r") as f:
            full_content = f.read()
        header_end = full_content.find('\0')
        header = full_content[:header_end]
        content_type, size = header.split()
        return content_type, full_content[header_end + 1:]

    def commit(self, config_data, message):
        """
        Records a new version of the configuration.
        This simulates committing changes to Git.
        """
        # Simulate a 'blob' for the configuration file
        config_json = json.dumps(config_data, indent=2)
        config_blob_hash = self._write_object("blob", config_json)

        # Create a 'tree' object (simplified: just points to the config blob)
        tree_content = f"100644 blob {config_blob_hash}\tapp_config.json"
        tree_hash = self._write_object("tree", tree_content)

        # Create a 'commit' object
        parent_commit_hash = ""
        if os.path.exists(self.head):
            with open(self.head, "r") as f:
                parent_commit_hash = f.read().strip()
        
        commit_content = {
            "tree": tree_hash,
            "parent": parent_commit_hash,
            "author": "GitOps Bot <bot@example.com>",
            "committer": "GitOps Bot <bot@example.com>",
            "timestamp": int(time.time()),
            "message": message
        }
        commit_hash = self._write_object("commit", json.dumps(commit_content))

        # Update the branch to point to the new commit
        with open(self.head, "w") as f:
            f.write(commit_hash)
        print(f"Commit [{commit_hash[:7]}] created: {message}")
        print(f"  Configuration blob: {config_blob_hash[:7]}")
        return commit_hash

    def get_current_config(self):
        """
        Retrieves the configuration from the HEAD of the main branch.
        This represents the 'single source of truth' for the current state.
        """
        if not os.path.exists(self.head):
            return None, "No commits yet."

        with open(self.head, "r") as f:
            current_commit_hash = f.read().strip()
        if not current_commit_hash:
            return None, "No commits yet."

        commit_type, commit_data_str = self._read_object(current_commit_hash)
        commit_data = json.loads(commit_data_str)

        tree_hash = commit_data["tree"]
        tree_type, tree_content = self._read_object(tree_hash)
        
        # Parse tree content to find the config blob hash
        # Example format: "100644 blob <hash>\tapp_config.json"
        parts = tree_content.strip().split('\t')
        blob_info = parts[0].split()
        config_blob_hash = blob_info[2]

        blob_type, config_json_str = self._read_object(config_blob_hash)
        return json.loads(config_json_str), f"Retrieved from commit {current_commit_hash[:7]}"

    def _cleanup(self):
        """Removes the mock repository directory."""
        import shutil
        if os.path.exists(self.repo_path):
            shutil.rmtree(self.repo_path)

# --- Demonstration of Git as the Source of Truth ---
if __name__ == "__main__":
    repo = GitLikeRepository()

    try:
        # Initial application configuration
        initial_config = {
            "application": "my-app",
            "version": "1.0.0",
            "replicas": 2,
            "environment": "dev"
        }
        print("--- Initial Deployment ---")
        repo.commit(initial_config, "Initial deployment of my-app v1.0.0")
        current_config, _ = repo.get_current_config()
        print(f"Current Config (from Git): {current_config}")
        print("-" * 30)

        # Simulate a change required for production
        prod_config = {
            "application": "my-app",
            "version": "1.0.0",
            "replicas": 5, # Scaled up for production
            "environment": "prod"
        }
        print("\n--- Scaling Up for Production ---")
        repo.commit(prod_config, "Scale replicas to 5 for production environment")
        current_config, _ = repo.get_current_config()
        print(f"Current Config (from Git): {current_config}")
        print("-" * 30)

        # Simulate a bug fix and new version deployment
        bugfix_config = {
            "application": "my-app",
            "version": "1.0.1", # New version
            "replicas": 5,
            "environment": "prod",
            "hotfix_applied": True
        }
        print("\n--- Deploying Hotfix v1.0.1 ---")
        repo.commit(bugfix_config, "Deploying v1.0.1 with critical bugfix")
        current_config, _ = repo.get_current_config()
        print(f"Current Config (from Git): {current_config}")
        print("-" * 30)

        # Imagine an attempt to manually change a running system outside Git.
        # GitOps mandates that only Git can truly change the desired state.
        # If the system were to drift, it would be reconciled back to Git's state.
        print("\n--- System Drift (manual change OUTSIDE Git) ---")
        drifted_config = {
            "application": "my-app",
            "version": "1.0.1",
            "replicas": 3, # Manually scaled down, not reflected in Git
            "environment": "prod",
            "hotfix_applied": True,
            "manual_override": True
        }
        print(f"Manual 'system state' (drifted): {drifted_config}")

        # GitOps agent constantly compares actual state to Git's desired state
        print("\n--- GitOps Reconciliation ---")
        desired_config, msg = repo.get_current_config()
        print(f"Desired State (from Git): {desired_config} ({msg})")

        if desired_config != drifted_config:
            print("Detected drift! System state does not match Git's desired state.")
            # In a real GitOps system, this would trigger an automated remediation.
            print("Reconciling system to match Git's desired state (e.g., revert replicas to 5).")
            # The system would be automatically brought back to {'replicas': 5}
        else:
            print("System state matches Git's desired state. No reconciliation needed.")

    finally:
        repo._cleanup()
