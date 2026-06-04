import hashlib
import json
import time

# Simulate a Kubernetes manifest stored in Git
GIT_MANIFEST = {
    "apiVersion": "apps/v1",
    "kind": "Deployment",
    "metadata": {"name": "my-app", "labels": {"app": "my-app"}},
    "spec": {
        "replicas": 3,
        "selector": {"matchLabels": {"app": "my-app"}},
        "template": {"metadata": {"labels": {"app": "my-app"}}, "spec": {"containers": [{"name": "nginx", "image": "nginx:1.21"}]}}
    }
}

# Simulate the current state of an application in Kubernetes
# This might drift from the desired state in Git
K8S_LIVE_STATE = {
    "apiVersion": "apps/v1",
    "kind": "Deployment",
    "metadata": {"name": "my-app", "labels": {"app": "my-app"}},
    "spec": {
        "replicas": 2,  # Drift detected here! Desired is 3
        "selector": {"matchLabels": {"app": "my-app"}},
        "template": {"metadata": {"labels": {"app": "my-app"}}, "spec": {"containers": [{"name": "nginx", "image": "nginx:1.21"}]}}
    }
}

class ArgoCDSimulator:
    def __init__(self, git_manifest_data, k8s_live_state_data):
        self.git_desired_state = git_manifest_data
        self.k8s_live_state = k8s_live_state_data
        self.last_sync_time = None

    def _calculate_manifest_hash(self, manifest):
        """Calculates a consistent hash for a manifest."""
        return hashlib.sha256(json.dumps(manifest, sort_keys=True).encode('utf-8')).hexdigest()

    def detect_drift(self):
        """Compares the desired state from Git with the live state in Kubernetes."""
        git_hash = self._calculate_manifest_hash(self.git_desired_state)
        k8s_hash = self._calculate_manifest_hash(self.k8s_live_state)

        if git_hash != k8s_hash:
            print(f"Drift Detected! Git hash: {git_hash}, Live K8s hash: {k8s_hash}")
            return True
        else:
            print("No drift detected. Live state matches Git desired state.")
            return False

    def reconcile(self):
        """Applies the Git desired state to Kubernetes, resolving drift."""
        if self.detect_drift():
            print("Reconciling: Applying Git desired state to Kubernetes...")
            # In a real scenario, this would involve sending API calls to Kubernetes
            # to update resources. Here, we simulate by updating the live state.
            self.k8s_live_state = json.loads(json.dumps(self.git_desired_state)) # Deep copy
            print("Reconciliation complete. Live state updated.")
            self.last_sync_time = time.time()
        else:
            print("No reconciliation needed. State is synchronized.")

# --- Simulation ---
print("--- Initial State ---")
argo_simulator = ArgoCDSimulator(GIT_MANIFEST, K8S_LIVE_STATE)
argo_simulator.detect_drift()

print("\n--- After Reconciliation ---")
argo_simulator.reconcile()

print("\n--- Verify State After Reconciliation ---")
argo_simulator.detect_drift()

# Simulate a new change in Git (e.g., update image version)
print("\n--- Simulating a new change in Git ---")
new_git_manifest = json.loads(json.dumps(GIT_MANIFEST)) # Deep copy
new_git_manifest["spec"]["template"]["spec"]["containers"][0]["image"] = "nginx:1.22"
argo_simulator.git_desired_state = new_git_manifest

print("\n--- Detecting drift after Git change ---")
argo_simulator.reconcile()

print("\n--- Final State ---")
argo_simulator.detect_drift()
