import yaml

def generate_gitrepository(cluster_name, repo_url, branch="main", secret_ref="fleet-repo-creds"):
    """
    Generates a GitRepository manifest for a given cluster.
    This manifest tells Flux where to find the cluster's configuration.
    """
    return {
        "apiVersion": "source.toolkit.fluxcd.io/v1beta2",
        "kind": "GitRepository",
        "metadata": {"name": f"{cluster_name}-repo", "namespace": "flux-system"},
        "spec": {
            "interval": "1m0s",
            "url": repo_url,
            "ref": {"branch": branch},
            "secretRef": {"name": secret_ref},
            "ignore": [
                f"!/{cluster_name}/**",  # Include only files specific to this cluster
                "!.cluster-common/**" # Include common files
            ]
        },
    }


def generate_kustomization(cluster_name, interval="10m0s", timeout="5m0s"):
    """
    Generates a Kustomization manifest for a given cluster.
    This manifest tells Flux which Kustomize paths to apply from the GitRepository.
    """
    return {
        "apiVersion": "kustomize.toolkit.fluxcd.io/v1beta2",
        "kind": "Kustomization",
        "metadata": {"name": f"{cluster_name}-kustomization", "namespace": "flux-system"},
        "spec": {
            "interval": interval,
            "timeout": timeout,
            "sourceRef": {"kind": "GitRepository", "name": f"{cluster_name}-repo"},
            "path": f"./{cluster_name}",  # Path to cluster-specific configurations
            "prune": True,
            "wait": True,
            "commonMetadata": {"labels": {"cluster": cluster_name}},
        },
    }

def main():
    fleet_config_repo = "git@github.com:your-org/fleet-config.git"
    clusters = ["dev-cluster-01", "prod-cluster-01", "staging-cluster-01"]

    print("# --- Flux CD Fleet Management Configuration ---")
    print("# This output represents the manifests that would be applied to a management cluster")
    print("# to configure Flux to manage multiple target clusters.")
    print("# Each GitRepository and Kustomization targets a specific cluster's configuration.")

    for cluster in clusters:
        # Each target cluster will have its own GitRepository resource
        # pointing to a specific path within the fleet configuration repository.
        git_repo_manifest = generate_gitrepository(cluster, fleet_config_repo)
        print(yaml.dump(git_repo_manifest, sort_keys=False, indent=2))
        print("---")

        # Each target cluster will have its own Kustomization resource
        # defining what to apply from its dedicated GitRepository.
        kustomization_manifest = generate_kustomization(cluster)
        print(yaml.dump(kustomization_manifest, sort_keys=False, indent=2))
        print("---")

if __name__ == "__main__":
    main()
