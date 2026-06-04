# multi_cluster_env_manager.py

import os
import json

# --- Core Idea: Simulate managing application deployments across multiple clusters/environments ---
# GitOps brings order to this by synchronizing desired state (defined in Git)
# to diverse environments automatically.

class DeploymentManager:
    def __init__(self, config_repo_path="./gitops_config"):
        """
        Initializes the deployment manager.
        In a real GitOps scenario, 'config_repo_path' would be a local clone
        of the Git repository holding all environment/cluster configurations.
        """
        self.config_repo_path = config_repo_path
        self._ensure_config_repo_exists()

    def _ensure_config_repo_exists(self):
        """Ensures the simulated GitOps config repository directory exists."""
        os.makedirs(self.config_repo_path, exist_ok=True)
        print(f"Initialized GitOps config repository at: {self.config_repo_path}")

    def create_env_config(self, env_name, cluster_name, app_name, version, namespace="default", replicas=1):
        """
        Simulates creating a configuration file for a specific application
        in a specific environment and cluster.
        In GitOps, this would be a commit to the Git repository.
        """
        env_dir = os.path.join(self.config_repo_path, env_name)
        cluster_dir = os.path.join(env_dir, cluster_name)
        os.makedirs(cluster_dir, exist_ok=True)

        config_file_path = os.path.join(cluster_dir, f"{app_name}.json")
        app_config = {
            "application": app_name,
            "version": version,
            "namespace": namespace,
            "replicas": replicas,
            "managed_by": "gitops_controller_simulated",
            "environment": env_name,
            "cluster": cluster_name
        }

        with open(config_file_path, 'w') as f:
            json.dump(app_config, f, indent=2)
        print(f"Created/Updated config for {app_name} in {env_name}/{cluster_name}: {config_file_path}")
        return config_file_path

    def get_desired_state(self, env_name, cluster_name, app_name):
        """
        Simulates a GitOps controller reading the desired state for an application
        from the Git repository.
        """
        config_file_path = os.path.join(self.config_repo_path, env_name, cluster_name, f"{app_name}.json")
        if not os.path.exists(config_file_path):
            return None, f"Error: Config for {app_name} not found in {env_name}/{cluster_name}"

        with open(config_file_path, 'r') as f:
            return json.load(f), None

    def simulate_git_sync(self):
        """
        Placeholder for a GitOps tool (Argo CD/Flux) synchronizing the desired state.
        In reality, this involves watching the Git repo and applying K8s manifests.
        """
        print("\n--- Simulating GitOps Controller Sync ---")
        for root, dirs, files in os.walk(self.config_repo_path):
            if "gitops_config" in root: # Skip root config directory check
                for file_name in files:
                    if file_name.endswith(".json"):
                        # Extract env, cluster, app_name from path
                        parts = root.split(os.sep)
                        try:
                            # Assuming path structure: ./gitops_config/ENV/CLUSTER/app.json
                            env_name = parts[-2]
                            cluster_name = parts[-1]
                            app_name = file_name.replace(".json", "")

                            desired_state, error = self.get_desired_state(env_name, cluster_name, app_name)
                            if desired_state:
                                print(f"  [SYNC] Applying desired state for {app_name} to {env_name}/{cluster_name}:")
                                print(f"    - Version: {desired_state['version']}, Replicas: {desired_state['replicas']}")
                            else:
                                print(f"  [ERROR SYNC] {error}")
                        except IndexError:
                            print(f"  [WARNING] Skipping unrecognized config path: {root}/{file_name}")

if __name__ == "__main__":
    # Clean up previous runs for a fresh start
    import shutil
    if os.path.exists("./gitops_config"):
        shutil.rmtree("./gitops_config")

    manager = DeploymentManager()

    # --- Illustrate managing multiple clusters and environments ---

    # 1. Development Environment on a local Kind cluster
    manager.create_env_config("dev", "kind-cluster-01", "webapp-backend", "v1.0.0", replicas=1)
    manager.create_env_config("dev", "kind-cluster-01", "frontend-ui", "v1.0.0", replicas=1)

    # 2. Staging Environment on AWS EKS
    manager.create_env_config("staging", "aws-eks-us-east-1", "webapp-backend", "v1.0.1", replicas=2)
    manager.create_env_config("staging", "aws-eks-us-east-1", "frontend-ui", "v1.0.0", replicas=1, namespace="staging-ns")
    manager.create_env_config("staging", "aws-eks-us-east-1", "monitoring-agent", "v2.0.0", namespace="kube-system", replicas=1)


    # 3. Production Environment on Google GKE
    manager.create_env_config("prod", "gke-europe-west-1", "webapp-backend", "v1.1.0", replicas=5)
    manager.create_env_config("prod", "gke-europe-west-1", "frontend-ui", "v1.0.1", replicas=3)

    # 4. Another Production Environment on Azure AKS (different cloud provider)
    manager.create_env_config("prod", "azure-aks-eastus", "webapp-backend", "v1.1.0", replicas=4) # Same version, different replica count
    manager.create_env_config("prod", "azure-aks-eastus", "cache-service", "v3.2.0", replicas=2, namespace="data-services")

    # Simulate GitOps controllers picking up these changes
    manager.simulate_git_sync()

    # --- Demonstrate what GitOps tools do: read desired state and ensure it's applied ---
    print("\n--- Verifying Desired States ---")
    dev_backend_state, _ = manager.get_desired_state("dev", "kind-cluster-01", "webapp-backend")
    prod_backend_gke_state, _ = manager.get_desired_state("prod", "gke-europe-west-1", "webapp-backend")
    prod_backend_aks_state, _ = manager.get_desired_state("prod", "azure-aks-eastus", "webapp-backend")

    print(f"Dev Backend state (kind): {dev_backend_state['version']} with {dev_backend_state['replicas']} replicas")
    print(f"Prod Backend state (GKE): {prod_backend_gke_state['version']} with {prod_backend_gke_state['replicas']} replicas")
    print(f"Prod Backend state (AKS): {prod_backend_aks_state['version']} with {prod_backend_aks_state['replicas']} replicas")

    # Cleanup config repo for subsequent runs
    # shutil.rmtree("./gitops_config")
