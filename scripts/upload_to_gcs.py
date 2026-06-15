#!/usr/bin/env python3
"""
Python script to upload unstructured lease PDF test data to Google Cloud Storage.
Make sure to authenticate before running:
gcloud auth application-default login
"""
import os
import argparse
from google.cloud import storage

def main():
    parser = argparse.ArgumentParser(description="Upload Vornado lease PDFs to GCS")
    parser.add_argument("--project-id", required=True, help="Google Cloud Project ID")
    parser.add_argument("--bucket-name", required=True, help="GCS Bucket Name")
    args = parser.parse_args()

    client = storage.Client(project=args.project_id)
    
    try:
        bucket = client.get_bucket(args.bucket_name)
        print(f"Bucket {args.bucket_name} already exists.")
    except Exception:
        print(f"Creating bucket {args.bucket_name} in project {args.project_id}...")
        bucket = client.create_bucket(args.bucket_name)
        
    script_dir = os.path.dirname(os.path.abspath(__file__))
    unstructured_dir = os.path.join(script_dir, "..", "data", "unstructured")
    
    for filename in os.listdir(unstructured_dir):
        if filename.endswith(".pdf"):
            local_path = os.path.join(unstructured_dir, filename)
            blob = bucket.blob(filename)
            print(f"Uploading {filename} to gs://{args.bucket_name}/{filename}...")
            blob.upload_from_filename(local_path)
            
    print("All unstructured files uploaded successfully.")

if __name__ == "__main__":
    main()
