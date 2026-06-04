# This example simulates Flux CD's reconciliation loop for a GitOps repository.
# It demonstrates how Flux would detect changes in a simulated Git repository
# and apply them to a "cluster" (represented by a dictionary).

import json
import hashlib
import time

class FluxSimulator:
    def __init__(self, git_repo_path):
        """
        Initializes the Flux simulator with a path to the simulated Git repository.
        """
        self.git_repo_path = git_repo_path
        self.cluster_state = {}  # Represents the Kubernetes cluster state
        self.last_applied_manifest_hash = None
        print(f"Flux Simulator initialized for Git repo: {self.git_repo_path}")

    def _read_git_manifests(self):
        """
        Simulates reading manifest files from a Git repository.
        In a real scenario, Flux would clone/pull the repo.
        """
        try:
            with open(self.git_repo_path, 'r') as f:
                manifests_content = f.read()
            return manifests_content
        except FileNotFoundError:
            return ""

    def _generate_manifest_hash(self, content):
        """Generates a SHA256 hash of the manifest content."""
        return hashlib.sha256(content.encode('utf-8')).hexdigest()

    def _apply_manifests_to_cluster(self, manifests_content):
        """
        Simulates applying K8s manifests to the cluster.
        In a real Flux setup, this would involve 'kubectl apply' or Kustomize.
        """
        if not manifests_content:
            print("No manifests to apply.")
            return

        try:
            # For simplicity, we assume the content is a JSON representation
            # of desired cluster resources.
            new_state = json.loads(manifests_content)
            self.cluster_state.update(new_state)
            print(f"Applied manifests to cluster. New state: {self.cluster_state}")
        except json.JSONDecodeError as e:
            print(f"Error parsing manifests (simulated Kustomize or YAML error): {e}")

    def reconcile(self):
        """
        Performs a single reconciliation loop:
        1. Reads current state from Git.
        2. Compares with the last applied state.
        3. Applies changes if a diff is detected.
        """
        print("\n--- Starting Flux Reconciliation Loop ---")
        current_git_manifests = self._read_git_manifests()
        current_git_hash = self._generate_manifest_hash(current_git_manifests)

        if current_git_hash != self.last_applied_manifest_hash:
            print("Detected change in Git repository.")
            self._apply_manifests_to_cluster(current_git_manifests)
            self.last_applied_manifest_hash = current_git_hash
            print("Reconciliation successful: Changes applied.")
        else:
            print("No changes detected in Git repository. Cluster is in sync.")
        print("--- Reconciliation Loop Finished ---")

# --- Simulation Setup ---
# Create a dummy Git repository file
GIT_REPO_FILE = "simulated_git_repo.json"

# Initial application state in Git
initial_manifests = {
    "deployment/myapp-v1": {"image": "myapp:v1.0.0", "replicas": 2},
    "service/myapp": {"port": 80},
}
with open(GIT_REPO_FILE, 'w') as f:
    json.dump(initial_manifests, f, indent=2)

# Initialize and run Flux simulator
flux = FluxSimulator(GIT_REPO_FILE)

# First reconciliation - should apply initial manifests
flux.reconcile()
print(f"Current cluster state after initial apply: {flux.cluster_state}")

time.sleep(1) # Simulate a delay

# Second reconciliation - no changes, should do nothing
flux.reconcile()

time.sleep(1) # Simulate a delay

# Modify the "Git repository" file to simulate a new commit
updated_manifests = {
    "deployment/myapp-v2": {"image": "myapp:v2.0.0", "replicas": 3},
    "service/myapp": {"port": 80},
    "ingress/myapp": {"host": "myapp.example.com"}
}
with open(GIT_REPO_FILE, 'w') as f:
    json.dump(updated_manifests, f, indent=2)
print("\n--- Simulated Git repo update ---")

time.sleep(1) # Simulate a delay

# Third reconciliation - should detect and apply the update
flux.reconcile()
print(f"Current cluster state after update: {flux.cluster_state}")
