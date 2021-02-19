import os
import sys
import subprocess

BACKEND_REPOSITORIES = [
    "MPBX",
    "TransactionService",
    "MediaService",
    "SearchService",
    "Python-Core-SDK",
    "TaxService",
    "RoadRunner",
    "common-be-scripts",
    "pdf-service",
    "FixtureService",
    "TranslationService",
    "MPB-Core-Protos",
    "K8s-LetsEncrypt",
    "SearchService-Helm-Charts",
    "SearchService-Protos",
    "TransactionService-Protos",
    "TransactionService-Protos",
    "TaxService-Protos",
    "TaxService-Helm-Charts",
    "TransactionService-Helm-Charts",
]

FRONTEND_REPOSITORIES = [
    "Flamingo",
    "Toucan",
]

TA_REPOSITORIES = [
    "WebdriverTests",
    "PerformanceTests",
    "Python-Test-SDK",
]

DATA_DIR = "data"
BACKEND_DATA_DIR = os.path.join(DATA_DIR, "backend")
FRONTEND_DATA_DIR = os.path.join(DATA_DIR, "frontend")
TA_DATA_DIR = os.path.join(DATA_DIR, "ta")

if not os.path.isdir("data"):
    os.makedirs("data")

if not os.path.isdir(BACKEND_DATA_DIR):
    os.makedirs(BACKEND_DATA_DIR)

if not os.path.isdir(FRONTEND_DATA_DIR):
    os.makedirs(FRONTEND_DATA_DIR)

if not os.path.isdir(TA_DATA_DIR):
    os.makedirs(TA_DATA_DIR)


for repository in FRONTEND_REPOSITORIES:
    output_file = os.path.join(FRONTEND_DATA_DIR, f"{repository}.json")
    print("Loading PR data for", repository, "to", output_file)
    subprocess.run(
        [
            sys.executable,
            "./download_data.py",
            "-o",
            output_file,
            "mpb-com",
            repository,
        ]
    )


for repository in BACKEND_REPOSITORIES:
    output_file = os.path.join(BACKEND_DATA_DIR, f"{repository}.json")
    print("Loading PR data for", repository, "to", output_file)
    subprocess.run(
        [
            sys.executable,
            "./download_data.py",
            "-o",
            output_file,
            "mpb-com",
            repository,
        ]
    )


for repository in TA_REPOSITORIES:
    output_file = os.path.join(TA_DATA_DIR, f"{repository}.json")
    print("Loading PR data for", repository, "to", output_file)
    subprocess.run(
        [
            sys.executable,
            "./download_data.py",
            "-o",
            output_file,
            "mpb-com",
            repository,
        ]
    )
