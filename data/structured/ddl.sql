-- DDL for Real Estate Lease Agent Demo Tables

CREATE OR REPLACE TABLE `vornado_realestate.historical_leases` (
  lease_id STRING OPTIONS(description="Unique identifier for the historical lease"),
  property_name STRING OPTIONS(description="Vornado property name (e.g. PENN 1, PENN 2)"),
  tenant_name STRING OPTIONS(description="Name of the tenant"),
  execution_date DATE OPTIONS(description="Date the lease agreement was signed"),
  commencement_date DATE OPTIONS(description="Date the lease term officially commenced"),
  lease_term_months INT64 OPTIONS(description="Total length of the lease in months"),
  rsf INT64 OPTIONS(description="Rentable square feet leased"),
  initial_base_rent_per_rsf NUMERIC OPTIONS(description="Starting base rent rate per RSF per year"),
  free_rent_months INT64 OPTIONS(description="Number of months of base rent abatement"),
  ti_allowance_per_rsf NUMERIC OPTIONS(description="Tenant Improvement allowance provided per RSF"),
  step_up_percentage NUMERIC OPTIONS(description="Percentage increase during rent step-ups"),
  step_up_interval_months INT64 OPTIONS(description="Number of months between rent step-ups"),
  industry STRING OPTIONS(description="Tenant industry vertical"),
  lease_status STRING OPTIONS(description="Current status: Active, Expired, Terminated")
);

CREATE OR REPLACE TABLE `vornado_realestate.construction_costs_ti` (
  project_id STRING OPTIONS(description="Unique identifier for the construction project"),
  property_name STRING OPTIONS(description="Vornado property name (e.g. PENN 1, PENN 2)"),
  project_type STRING OPTIONS(description="Type of project (e.g. Tenant Fit-Out, Lobby Redevelopment)"),
  contractor_name STRING OPTIONS(description="Name of the general contractor"),
  start_date DATE OPTIONS(description="Project start date"),
  completion_date DATE OPTIONS(description="Project actual or projected completion date"),
  budgeted_cost_per_rsf NUMERIC OPTIONS(description="Underwritten or budgeted cost per RSF"),
  actual_cost_per_rsf NUMERIC OPTIONS(description="Actual cost incurred per RSF"),
  delay_days INT64 OPTIONS(description="Number of calendar days of delay"),
  reason_for_delay STRING OPTIONS(description="Primary driver of construction delay")
);

CREATE OR REPLACE TABLE `vornado_realestate.market_comps` (
  comp_id STRING OPTIONS(description="Unique identifier for the market comparison record"),
  property_name STRING OPTIONS(description="Name of the comp property"),
  submarket STRING OPTIONS(description="Submarket classification (e.g. Penn District, Midtown West)"),
  execution_date DATE OPTIONS(description="Date the lease comp was executed"),
  rsf INT64 OPTIONS(description="Rentable square feet of the comp lease"),
  lease_term_months INT64 OPTIONS(description="Lease term in months"),
  base_rent_per_rsf NUMERIC OPTIONS(description="Base rent per RSF per year"),
  free_rent_months INT64 OPTIONS(description="Number of months of rent abatement"),
  ti_allowance_per_rsf NUMERIC OPTIONS(description="TI allowance per RSF"),
  source STRING OPTIONS(description="Brokerage source of the data (JLL, CBRE, Cushman)")
);

CREATE OR REPLACE TABLE `vornado_realestate.tax_escalations` (
  property_name STRING OPTIONS(description="Vornado property name"),
  year INT64 OPTIONS(description="Calendar year of tax or expense assessment"),
  real_estate_tax_per_rsf NUMERIC OPTIONS(description="Real estate tax rate per RSF"),
  operating_expense_per_rsf NUMERIC OPTIONS(description="Operating expense rate per RSF"),
  base_year_tax NUMERIC OPTIONS(description="Base year real estate tax rate per RSF for escalations"),
  base_year_opex NUMERIC OPTIONS(description="Base year operating expense rate per RSF for escalations")
);
