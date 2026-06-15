import datetime
import decimal
import os
import re

from google import genai
from google.cloud import bigquery
from google.genai import types


def _serialize_value(val):
    if isinstance(val, (datetime.date, datetime.datetime, datetime.time)):
        return val.isoformat()
    if isinstance(val, decimal.Decimal):
        return float(val)
    if isinstance(val, (bytes, bytearray)):
        return val.decode("utf-8", errors="ignore")
    return val


def _extract_tables(query: str) -> set[str]:
    query = re.sub(r"--.*$", "", query, flags=re.MULTILINE)
    query = re.sub(r"/\*.*?\*/", "", query, flags=re.DOTALL)
    q = (
        query.lower()
        .replace("`", " ")
        .replace('"', " ")
        .replace("'", " ")
        .replace("\n", " ")
        .replace("\r", " ")
    )
    tables = set()
    matches = re.finditer(r"\b(from|join)\b", q)
    for match in matches:
        start_idx = match.end()
        end_match = re.search(
            r"\b(where|join|group|order|limit|having|union|select|on|left|right|inner|outer|cross|natural|using)\b|\)",
            q[start_idx:],
        )
        if end_match:
            table_str = q[start_idx : start_idx + end_match.start()]
        else:
            table_str = q[start_idx:]
        for part in table_str.split(","):
            part = part.strip()
            if not part:
                continue
            words = part.split()
            if not words:
                continue
            table_name = words[0].strip("()")
            if table_name == "select" or table_name == "":
                continue
            tables.add(table_name)
    return tables


def _extract_ctes(query: str) -> set[str]:
    q = (
        query.lower()
        .replace("`", " ")
        .replace('"', " ")
        .replace("'", " ")
        .replace("\n", " ")
        .replace("\r", " ")
    )
    ctes = set()
    with_match = re.search(r"\bwith\b", q)
    if not with_match:
        return ctes
    cte_matches = re.finditer(r"\b([a-zA-Z0-9_]+)\s+as\s*\(", q)
    for m in cte_matches:
        ctes.add(m.group(1))
    return ctes


def _validate_bigquery_query(sql_query: str) -> bool:
    cleaned_query = sql_query.strip().upper()
    if not cleaned_query.startswith("SELECT") and not cleaned_query.startswith("WITH"):
        return False
    if ";" in sql_query:
        return False
    allowed_tables_basenames = {
        "historical_leases",
        "construction_costs_ti",
        "market_comps",
        "tax_escalations",
    }
    ctes = _extract_ctes(sql_query)
    queried_tables = _extract_tables(sql_query)
    for table in queried_tables:
        if table in ctes:
            continue
        parts = table.split(".")
        table_base = parts[-1]
        if table_base not in allowed_tables_basenames:
            return False
        if len(parts) > 1:
            dataset = parts[-2]
            if dataset != "vornado_realestate":
                return False
        if len(parts) > 2:
            project = parts[-3]
            if project not in (
                "genaillentsearch",
                os.environ.get("GOOGLE_CLOUD_PROJECT", "genaillentsearch"),
            ):
                return False
    return True


def execute_bigquery_query(sql_query: str) -> dict:
    """Executes a SQL query on BigQuery tables under the project 'genaillentsearch' and dataset 'vornado_realestate'.

    The allowed tables are:
    * `vornado_realestate.historical_leases`
    * `vornado_realestate.construction_costs_ti`
    * `vornado_realestate.market_comps`
    * `vornado_realestate.tax_escalations`

    Args:
        sql_query: The SQL SELECT query to execute. It must target only the allowed tables and dataset.

    Returns:
        A dictionary containing the query execution status ('success' or 'error') and either 'data' (list of rows as dicts) or 'error' message.
    """
    if not _validate_bigquery_query(sql_query):
        return {
            "status": "error",
            "error": "Query is not allowed. Only SELECT queries targeting allowed vornado_realestate tables are permitted.",
        }

    try:
        project = os.environ.get("GOOGLE_CLOUD_PROJECT", "genaillentsearch")
        client = bigquery.Client(project=project)
        query_job = client.query(sql_query)
        results = query_job.result()

        rows = []
        for row in results:
            serialized_row = {k: _serialize_value(v) for k, v in row.items()}
            rows.append(serialized_row)

        return {"status": "success", "data": rows}
    except Exception as e:
        return {"status": "error", "error": str(e)}


def analyze_lease_document(file_name: str, query: str) -> dict:
    """Queries Gemini to extract specific clauses/information from unstructured PDF lease agreements/status reports stored in GCS.

    The files are located in the GCS bucket 'vornado-leases-genaillentsearch'.
    The allowed files are:
    * `PENN2_Apex_Fintech_Draft_Lease.pdf`
    * `PENN1_BioMed_Diagnostics_Draft_Lease.pdf`
    * `PENN2_Construction_Status_Report.pdf`

    Args:
        file_name: The name of the PDF file to analyze.
        query: The prompt/question specifying what clauses or information to extract.

    Returns:
        A dictionary containing the analysis status ('success' or 'error') and either 'result' (Gemini extracted text) or 'error' message.
    """
    allowed_files = [
        "PENN2_Apex_Fintech_Draft_Lease.pdf",
        "PENN1_BioMed_Diagnostics_Draft_Lease.pdf",
        "PENN2_Construction_Status_Report.pdf",
    ]
    if file_name not in allowed_files:
        return {
            "status": "error",
            "error": f"File '{file_name}' is not allowed. Choose from: {allowed_files}",
        }

    if not query:
        return {"status": "error", "error": "Query cannot be empty."}

    try:
        # Initialize the GenAI client.
        client = genai.Client()
        gcs_uri = f"gs://vornado-leases-genaillentsearch/{file_name}"

        part = types.Part.from_uri(file_uri=gcs_uri, mime_type="application/pdf")

        # Execute query using the gemini-3.5-flash model
        response = client.models.generate_content(
            model="gemini-3.5-flash", contents=[query, part]
        )

        return {"status": "success", "result": response.text}
    except Exception as e:
        return {"status": "error", "error": str(e)}
