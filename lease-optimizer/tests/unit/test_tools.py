# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from app.tools import _validate_bigquery_query


def test_validate_allowed_table_basenames():
    assert _validate_bigquery_query("SELECT * FROM historical_leases") is True
    assert (
        _validate_bigquery_query("SELECT * FROM vornado_realestate.historical_leases")
        is True
    )
    assert (
        _validate_bigquery_query(
            "SELECT * FROM genaillentsearch.vornado_realestate.historical_leases"
        )
        is True
    )
    assert (
        _validate_bigquery_query("SELECT * FROM `vornado_realestate.historical_leases`")
        is True
    )
    assert (
        _validate_bigquery_query("""
        WITH cte AS (SELECT * FROM vornado_realestate.historical_leases)
        SELECT * FROM cte
    """)
        is True
    )


def test_validate_disallowed_table_basenames():
    assert _validate_bigquery_query("SELECT * FROM other_table") is False
    assert (
        _validate_bigquery_query("SELECT * FROM vornado_realestate.other_table")
        is False
    )


def test_validate_disallowed_dataset_and_project():
    assert (
        _validate_bigquery_query("SELECT * FROM other_dataset.historical_leases")
        is False
    )
    assert (
        _validate_bigquery_query(
            "SELECT * FROM other_project.vornado_realestate.historical_leases"
        )
        is False
    )
    assert (
        _validate_bigquery_query(
            "SELECT * FROM genaillentsearch.other_dataset.historical_leases"
        )
        is False
    )


def test_validate_information_schema_valid():
    assert (
        _validate_bigquery_query(
            "SELECT * FROM vornado_realestate.INFORMATION_SCHEMA.COLUMNS"
        )
        is True
    )
    assert (
        _validate_bigquery_query(
            "SELECT * FROM `vornado_realestate.INFORMATION_SCHEMA.COLUMNS`"
        )
        is True
    )
    assert (
        _validate_bigquery_query(
            "SELECT * FROM genaillentsearch.vornado_realestate.INFORMATION_SCHEMA.COLUMNS"
        )
        is True
    )
    assert (
        _validate_bigquery_query(
            "SELECT * FROM `genaillentsearch.vornado_realestate.INFORMATION_SCHEMA.TABLES`"
        )
        is True
    )
    assert (
        _validate_bigquery_query(
            "SELECT * FROM vornado_realestate.INFORMATION_SCHEMA.TABLES"
        )
        is True
    )
    assert (
        _validate_bigquery_query(
            "SELECT * FROM vornado_realestate.INFORMATION_SCHEMA.SCHEMATA"
        )
        is True
    )
    assert (
        _validate_bigquery_query(
            "WITH info AS (SELECT * FROM vornado_realestate.INFORMATION_SCHEMA.COLUMNS) SELECT * FROM info"
        )
        is True
    )


def test_validate_information_schema_invalid_dataset():
    assert (
        _validate_bigquery_query(
            "SELECT * FROM other_dataset.INFORMATION_SCHEMA.COLUMNS"
        )
        is False
    )
    assert _validate_bigquery_query("SELECT * FROM INFORMATION_SCHEMA.COLUMNS") is False


def test_validate_information_schema_invalid_project():
    assert (
        _validate_bigquery_query(
            "SELECT * FROM other_project.vornado_realestate.INFORMATION_SCHEMA.COLUMNS"
        )
        is False
    )


def test_validate_security_restrictions():
    assert (
        _validate_bigquery_query(
            "INSERT INTO vornado_realestate.historical_leases VALUES (1)"
        )
        is False
    )
    assert (
        _validate_bigquery_query(
            "DELETE FROM vornado_realestate.historical_leases WHERE id=1"
        )
        is False
    )
    assert (
        _validate_bigquery_query("SELECT * FROM vornado_realestate.historical_leases;")
        is False
    )
    assert (
        _validate_bigquery_query("DROP TABLE vornado_realestate.historical_leases")
        is False
    )
    assert (
        _validate_bigquery_query(
            "SELECT * FROM vornado_realestate.historical_leases; DROP TABLE historical_leases"
        )
        is False
    )
