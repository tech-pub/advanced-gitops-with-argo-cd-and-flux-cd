import yaml

def generate_argocd_applicationset(clusters, app_name, source_repo, source_path, destination_namespace):
    """
    Generates an Argo CD ApplicationSet YAML definition for multiple clusters.

    Args:
        clusters (list): A list of dictionaries, where each dictionary represents
                         a cluster with 'name' and 'server' keys.
        app_name (str): The name of the application to deploy.
        source_repo (str): The Git repository URL containing the application manifests.
        source_path (str): The path within the repository to the application manifests.
        destination_namespace (str): The Kubernetes namespace for the application.

    Returns:
        str: A YAML string representing the Argo CD ApplicationSet.
    """

    generators = []
    # Use a List generator to specify clusters dynamically
    generators.append({
        "list": {
            "elements": [{"clusterName": cluster['name'], "clusterServer": cluster['server']}
                         for cluster in clusters]
        }
    })

    # Define the template for each Argo CD Application
    template = {
        "metadata": {
            "name": f"{app_name}-{{{{clusterName}}}}"  # Unique name per cluster
        },
        "spec": {
            "project": "default",
            "source": {
                "repoURL": source_repo,
                "targetRevision": "HEAD",
                "path": source_path,
                # Example for Kustomize in a real scenario:
                # "kustomize": {"commonLabels": {"cluster": "{{clusterName}}"}}
            },
            "destination": {
                "server": "{{clusterServer}}",  # Destination server from generator
                "namespace": destination_namespace
            },
            "syncPolicy": {
                "automated": {
                    "prune": True,
                    "selfHeal": True
                },
                "syncOptions": [
                    "CreateNamespace=true"
                ]
            }
        }
    }

    # Construct the full ApplicationSet object
    applicationset = {
        "apiVersion": "argoproj.io/v1alpha1",
        "kind": "ApplicationSet",
        "metadata": {
            "name": f"{app_name}-multicluster-set"
        },
        "spec": {
            "generators": generators,
            "template": template
        }
    }

    return yaml.dump(applicationset, sort_keys=False)

if __name__ == "__main__":
    # Example usage:
    defined_clusters = [
        {"name": "dev-cluster", "server": "https://kubernetes.default.svc"},
        {"name": "prod-cluster-us", "server": "https://prod-us.k8s.example.com"},
        {"name": "prod-cluster-eu", "server": "https://prod-eu.k8s.example.com"},
    ]

    application_name = "my-nginx"
    git_repo = "https://github.com/argoproj/argocd-example-apps.git"
    repo_path = "guestbook"  # Path to the Kubernetes manifests within the repo
    target_namespace = "guestbook"

    # Generate the ApplicationSet YAML
    applicationset_yaml = generate_argocd_applicationset(
        defined_clusters, application_name, git_repo, repo_path, target_namespace
    )

    print("--- Argo CD ApplicationSet for Multi-Cluster Deployment ---")
    print(applicationset_yaml)
    print("\n# To apply this, save it as a .yaml file and run:")
    print("# kubectl apply -f your-applicationset.yaml")
