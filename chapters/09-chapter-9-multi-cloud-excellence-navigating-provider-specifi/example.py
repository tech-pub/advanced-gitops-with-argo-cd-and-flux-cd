# This Python script demonstrates how to define common application configurations
# and abstract provider-specific resources using a structured approach.
# It simulates generating provider-specific manifests based on a generic definition.

import yaml

# Generic application configuration
app_config = {
    'name': 'my-web-app',
    'namespace': 'production',
    'replicas': 3,
    'image': 'registry.example.com/my-app:v1.0.0',
    'port': 80,
    'resource_requests': {
        'cpu': '100m',
        'memory': '128Mi'
    }
}

# Provider-specific configurations (templates describing how to map generic config)
provider_configs = {
    'aws': {
        'service_type': 'LoadBalancer',
        'ingress_annotation': 'service.beta.kubernetes.io/aws-load-balancer-internal: "true"'
    },
    'gcp': {
        'service_type': 'LoadBalancer',
        'ingress_annotation': 'cloud.google.com/load-balancer-type: "Internal"'
    },
    'azure': {
        'service_type': 'LoadBalancer',
        'ingress_annotation': 'service.beta.kubernetes.io/azure-load-balancer-internal: "true"'
    }
}

def generate_kubernetes_manifest(app_data: dict, provider_data: dict) -> str:
    """
    Generates a simplified Kubernetes Deployment and Service manifest
    for a given application and provider.
    """
    deployment = {
        'apiVersion': 'apps/v1',
        'kind': 'Deployment',
        'metadata': {
            'name': app_data['name'],
            'namespace': app_data['namespace']
        },
        'spec': {
            'replicas': app_data['replicas'],
            'selector': {'matchLabels': {'app': app_data['name']}},
            'template': {
                'metadata': {'labels': {'app': app_data['name']}},
                'spec': {
                    'containers': [{
                        'name': app_data['name'],
                        'image': app_data['image'],
                        'ports': [{'containerPort': app_data['port']}],
                        'resources': {
                            'requests': app_data['resource_requests']
                        }
                    }]
                }
            }
        }
    }

    service = {
        'apiVersion': 'v1',
        'kind': 'Service',
        'metadata': {
            'name': app_data['name'],
            'namespace': app_data['namespace'],
            'annotations': {
                'description': f"Internal LoadBalancer for {app_data['name']}",
                provider_data['ingress_annotation'].split(':')[0]: provider_data['ingress_annotation'].split(':')[1].strip()
            }
        },
        'spec': {
            'selector': {'app': app_data['name']},
            'ports': [{'protocol': 'TCP', 'port': 80, 'targetPort': app_data['port']}],
            'type': provider_data['service_type']
        }
    }
    
    return yaml.dump(deployment) + '---\n' + yaml.dump(service)

# Generate manifests for different providers
for provider, provider_specific_config in provider_configs.items():
    print(f"--- Manifests for {provider.upper()} ---")
    manifest = generate_kubernetes_manifest(app_config, provider_specific_config)
    print(manifest)
    print("\n" + "="*50 + "\n")
