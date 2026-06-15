#!/usr/bin/env python3
"""
Python script to load the structured CSV test data into BigQuery.
Make sure to authenticate before running:
gcloud auth application-default login
"""
import os
import argparse
from google.cloud import bigquery

def load_table(client, dataset_id, table_name, csv_path, schema_fields=None):
    dataset_ref = client.dataset(dataset_id)
    table_ref = dataset_ref.table(table_name)
    
    job_config = bigquery.LoadJobConfig()
    job_config.source_format = bigquery.SourceFormat.CSV
    job_config.skip_leading_rows = 1
    job_config.write_disposition = bigquery.WriteDisposition.WRITE_TRUNCATE
    job_config.autodetect = True if not schema_fields else False
    if schema_fields:
        job_config.schema = schema_fields
        
    print(f"Loading {csv_path} into {dataset_id}.{table_name}...")
    with open(csv_path, "rb") as source_file:
        job = client.load_table_from_file(source_file, table_ref, job_config=job_config)
    
    job.result()  # Waits for the job to complete.
    table = client.get_table(table_ref)
    print(f"Loaded {table.num_rows} rows into {dataset_id}.{table_name}.")

def main():
    parser = argparse.ArgumentParser(description="Load Vornado lease demo data into BigQuery")
    parser.add_argument("--project-id", required=True, help="Google Cloud Project ID")
    parser.add_argument("--dataset-id", default="vornado_realestate", help="BigQuery Dataset ID")
    args = parser.parse_args()

    client = bigquery.Client(project=args.project_id)
    
    # Create dataset if it doesn't exist
    dataset_ref = client.dataset(args.dataset_id)
    dataset = bigquery.Dataset(dataset_ref)
    dataset.location = "US"
    try:
        client.get_dataset(dataset_ref)
        print(f"Dataset {args.dataset_id} already exists.")
    except Exception:
        print(f"Creating dataset {args.dataset_id} in region US...")
        client.create_dataset(dataset)
        
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(script_dir, "..", "data", "structured")
    
    tables_to_load = [
        ("historical_leases", os.path.join(data_dir, "historical_leases.csv")),
        ("construction_costs_ti", os.path.join(data_dir, "construction_costs_ti.csv")),
        ("market_comps", os.path.join(data_dir, "market_comps.csv")),
        ("tax_escalations", os.path.join(data_dir, "tax_escalations.csv"))
    ]
    
    for table_name, csv_path in tables_to_load:
        if not os.path.exists(csv_path):
            print(f"Error: {csv_path} does not exist. Run generate_test_data.py first.")
            continue
        load_table(client, args.dataset_id, table_name, csv_path)

if __name__ == "__main__":
    main()
