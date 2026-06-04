import time
import json
import os

# --- Simulate Kubernetes API Model (Simplified) ---
class K8sObject:
    def __init__(self, api_version, kind, metadata, spec):
        self.apiVersion = api_version
        self.kind = kind
        self.metadata = metadata
        self.spec = spec
        self.status = {}

    def to_dict(self):
        return {
            "apiVersion": self.apiVersion,
            "kind": self.kind,
            "metadata": self.metadata,
            "spec": self.spec,
            "status": self.status
        }

# --- Simulate an Argo CD/Flux CD Application Model (Simplified) ---
class GitOpsApplication(K8sObject):
    def __init__(self, name, namespace, source_repo, source_path, target_revision):
        super().__init__(
            apiVersion="argoproj.io/v1alpha1",
            kind="Application",
            metadata={"name": name, "namespace": namespace},
            spec={
                "source": {"repoURL": source_repo, "path": source_path, "targetRevision": target_revision},
                "destination": {"server": "https://kubernetes.default.svc", "namespace": namespace}
            }
        )
        # Simulate GitOps specific status fields
        self.status["sync"] = {"status": "OutOfSync"}
        self.status["health"] = {"status": "Unknown"}

# --- Custom Resource Definition (CRD) Example: 'ScheduledJob' ---
class ScheduledJob(K8sObject):
    def __init__(self, name, namespace, schedule, command_image, command_args):
        super().__init__(
            apiVersion="custom.example.com/v1",
            kind="ScheduledJob",
            metadata={"name": name, "namespace": namespace},
            spec={
                "schedule": schedule,
                "commandImage": command_image,
                "commandArgs": command_args
            }
        )
        self.status["lastScheduleTime"] = None
        self.status["activeJobs"] = []

# --- Custom Controller Logic (Reconciliation Loop) ---
class ScheduledJobController:
    def __init__(self, namespace="default"):
        self.namespace = namespace
        self.scheduled_jobs = {} # In a real controller, this would query K8s API

    def add_scheduled_job(self, scheduled_job_obj):
        self.scheduled_jobs[scheduled_job_obj.metadata["name"]] = scheduled_job_obj
        print(f"[Controller] Added ScheduledJob: {scheduled_job_obj.metadata['name']}")

    def reconcile(self):
        print(f"\n[Controller] Starting reconciliation loop for namespace: {self.namespace}...")
        for name, job in self.scheduled_jobs.items():
            print(f"  Reconciling ScheduledJob: {name}")
            current_time = time.time()
            schedule = job.spec["schedule"] # e.g., "*/10 * * * *" (cron format)

            # Simplified cron parsing: if current time % 10 seconds == 0, execute
            # In a real controller, you'd use a cron library (e.g., croniter)
            if int(current_time) % 10 == 0 and \
               (job.status["lastScheduleTime"] is None or (current_time - job.status["lastScheduleTime"]) > 9):
                print(f"    -> Schedule triggered! Executing command: {job.spec['commandImage']} {job.spec['commandArgs']}")
                # In a real scenario, this would create a Kubernetes Job resource
                # for the specified image and arguments.
                job.status["lastScheduleTime"] = current_time
                job.status["activeJobs"].append(f"job-{int(current_time)}") # Simulate a new job
                print(f"    -> Updated status: {job.status}")
            else:
                remaining_time = 10 - (int(current_time) % 10)
                print(f"    -> Not yet time to run. Next run in approx {remaining_time} seconds.")
        print("[Controller] Reconciliation loop finished.")

# --- Main simulation ---
if __name__ == "__main__":
    controller = ScheduledJobController()

    # Define a custom ScheduledJob
    my_scheduled_job = ScheduledJob(
        name="my-daily-backup",
        namespace="default",
        schedule="0 2 * * *", # Daily at 2 AM (simplified for demo)
        command_image="my-backup-image:v1.0",
        command_args=["--path", "/data", "--dest", "s3://my-bucket"]
    )

    controller.add_scheduled_job(my_scheduled_job)

    # Simulate the GitOps reconciliation loop
    # In a real GitOps system, Argo CD/Flux would detect changes
    # to the ScheduledJob CRD and the custom controller would react.
    print(f"\n--- Simulating GitOps Application state ---")
    gitops_app = GitOpsApplication(
        name="my-custom-workloads",
        namespace="default",
        source_repo="https://github.com/my-org/gitops-repo.git",
        source_path="kubernetes/custom-jobs",
        target_revision="HEAD"
    )
    print(f"GitOps System sees Application '{gitops_app.metadata['name']}' status: {gitops_app.status['sync']['status']}, {gitops_app.status['health']['status']}")
    print(f"Applying custom resource {my_scheduled_job.kind}/{my_scheduled_job.metadata['name']} via GitOps...")
    # Assume the GitOps system has reconciled this object into the cluster
    # and the custom controller is watching for it.

    # Simulate controller running over time
    for i in range(25):
        print(f"\n--- Simulating control loop iteration {i+1} ---")
        controller.reconcile()
        time.sleep(1) # Simulate a reconciliation interval
