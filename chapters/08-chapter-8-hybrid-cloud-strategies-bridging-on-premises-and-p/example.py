# hybrid_cloud_gitops_representation.py
# This script simulates a simplified GitOps approach for hybrid cloud
# deployments. It represents the state of applications across on-premises
# and cloud environments, based on a single source of truth (Git repository).

import json
import hashlib

# Simulate a Git repository for infrastructure and application definitions
# In a real scenario, this would be fetched from GitHub, GitLab, etc.
git_repo_state = {
    "on_premise/nginx_app/deployment.yaml": """
        apiVersion: apps/v1
        kind: Deployment
        metadata:
          name: nginx-onprem
        spec:
          replicas: 3
          template:
            spec:
              containers:
              - name: nginx
                image: nginx:1.21.3
        """,
    "cloud_provider_a/api_service/deployment.yaml": """
        apiVersion: apps/v1
        kind: Deployment
        metadata:
          name: api-service-cloud
        spec:
          replicas: 5
          template:
            spec:
              containers:
              - name: api
                image: myrepo/api:v2.1
                env:
                - name: ENV_TYPE
                  value: "CLOUD_A"
        """,
    "cloud_provider_b/data_processor/deployment.yaml": """
        apiVersion: apps/v1
        kind: Deployment
        metadata:
          name: data-processor-b
        spec:
          replicas: 2
          template:
            spec:
              containers:
              - name: processor
                image: myrepo/data-processor:v1.0
                resources:
                  limits:
                    cpu: "1"
        """
}

# --- Simulate On-Premises and Cloud Clusters ---
# In a real setup, these would be discovered or registered clusters
# Each cluster has an 'agent' (Argo CD/Flux) that pulls from Git
class Cluster:
    def __init__(self, name, environment_type):
        self.name = name
        self.environment_type = environment_type # e.g., "on_premise", "cloud_a"
        self.deployed_manifests = {} # Stores hashes of currently deployed manifests

    def sync_from_git(self, git_state):
        """
        Simulates the GitOps agent on a cluster pulling and applying
        configurations relevant to its environment.
        """
        print(f"\n[{self.name} - {self.environment_type}] Syncing from Git...")
        for path, content in git_state.items():
            if path.startswith(self.environment_type):
                content_hash = hashlib.sha256(content.encode()).hexdigest()
                if self.deployed_manifests.get(path) != content_hash:
                    # Simulate applying the manifest
                    print(f"  Applying/Updating: {path.split('/')[-1]}")
                    self.deployed_manifests[path] = content_hash
                else:
                    print(f"  {path.split('/')[-1]} is up-to-date.")
        # Remove any manifests no longer present in Git for this environment
        for deployed_path in list(self.deployed_manifests.keys()):
            if deployed_path.startswith(self.environment_type) and deployed_path not in git_state:
                print(f"  Removing/Deleting: {deployed_path.split('/')[-1]} (no longer in Git)")
                del self.deployed_manifests[deployed_path]


# Initialize our simulated hybrid cloud environment
on_prem_cluster = Cluster("OnPrem-Prod", "on_premise")
cloud_a_cluster = Cluster("CloudA-Dev", "cloud_provider_a")
cloud_b_cluster = Cluster("CloudB-Prod", "cloud_provider_b")

# Initial sync of all clusters
on_prem_cluster.sync_from_git(git_repo_state)
cloud_a_cluster.sync_from_git(git_repo_state)
cloud_b_cluster.sync_from_git(git_repo_state)

print("\n--- Current Deployed State (Simulated Inventories) ---")
print(f"On-Premise Cluster '{on_prem_cluster.name}': {list(p.split('/')[-1] for p in on_prem_cluster.deployed_manifests.keys())}")
print(f"Cloud A Cluster '{cloud_a_cluster.name}': {list(p.split('/')[-1] for p in cloud_a_cluster.deployed_manifests.keys())}")
print(f"Cloud B Cluster '{cloud_b_cluster.name}': {list(p.split('/')[-1] for p in cloud_b_cluster.deployed_manifests.keys())}")

# --- Simulate a change in the Git repository ---
print("\n--- Simulating a Git commit: Updating Cloud A and adding On-Premises ---")
git_repo_state["cloud_provider_a/api_service/deployment.yaml"] = """
    apiVersion: apps/v1
    kind: Deployment
    metadata:
      name: api-service-cloud
    spec:
      replicas: 7 # Scaling up
      template:
        spec:
          containers:
          - name: api
            image: myrepo/api:v2.2 # New image version
            env:
            - name: ENV_TYPE
              value: "CLOUD_A"
            - name: LOG_LEVEL
              value: "INFO" # New environment variable
    """
git_repo_state["on_premise/db_migration/job.yaml"] = """
    apiVersion: batch/v1
    kind: Job
    metadata:
      name: db-migration-onprem
    spec:
      template:
        spec:
          containers:
          - name: migrator
            image: myrepo/db-migrator:v1.0
          restartPolicy: OnFailure
    """

# Re-sync clusters after the "Git commit"
on_prem_cluster.sync_from_git(git_repo_state)
cloud_a_cluster.sync_from_git(git_repo_state)
cloud_b_cluster.sync_from_git(git_repo_state) # Cloud B remains unchanged in Git

print("\n--- Updated Deployed State (Simulated Inventories) ---")
print(f"On-Premise Cluster '{on_prem_cluster.name}': {list(p.split('/')[-1] for p in on_prem_cluster.deployed_manifests.keys())}")
print(f"Cloud A Cluster '{cloud_a_cluster.name}': {list(p.split('/')[-1] for p in cloud_a_cluster.deployed_manifests.keys())}")
print(f"Cloud B Cluster '{cloud_b_cluster.name}': {list(p.split('/')[-1] for p in cloud_b_cluster.deployed_manifests.keys())}")

# Expected output demonstrates how changes in the central Git state
# are propagated to the relevant clusters, maintaining consistency
# and enabling distinct configurations for different environments.
