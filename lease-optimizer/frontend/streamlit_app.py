import asyncio
import os

import pandas as pd
import plotly.express as px
import streamlit as st
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.cloud import bigquery
from google.genai import types

from app.agent import create_agent

# Page config
st.set_page_config(
    page_title="Vornado Penn District Lease Optimizer",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded",
)


# Set environment project just in case
os.environ["GOOGLE_CLOUD_PROJECT"] = "genaillentsearch"
os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "True"

st.title("🏢 Vornado Penn District Lease Optimizer")
st.markdown(
    "Asset Management & Revenue Optimization Agent for the Penn District redevelopment (PENN 1, PENN 2, PENN 11)."
)

# Storylines configuration
STORYLINES = {
    "1. Cash NOI Inflection & Slippage (CFO Focus)": {
        "description": "Evaluate the financial slippage and shifts in Cash NOI inflection points when construction delays floor delivery.",
        "default_query": "Does the execution of Section 14 (Tenant Improvement Allowance) in this draft lease delay our Cash NOI inflection point beyond Q3 2027? Review the PENN2_Apex_Fintech_Draft_Lease.pdf and the PENN2_Construction_Status_Report.pdf.",
        "data_tables": ["construction_costs_ti"],
    },
    "2. Concession & Penalty Liability Audit (AM Focus)": {
        "description": "Analyze tiered penalty rent abatements (1-for-1 vs 2-for-1 abatement days) to calculate total delayed cash revenue exposure.",
        "default_query": "Read Section 3.3 of the Apex lease draft to extract the tiered penalty triggers and parse the construction report to find the delay duration. Calculate the penalty exposure by multiplying the delay penalty days by the daily base rent rate.",
        "data_tables": ["construction_costs_ti"],
    },
    "3. Contractor Risk & Budget Overrun Audit (COO Focus)": {
        "description": "Assess general contractor performance (Turner Construction) and run comparative overrun analytics across historical projects.",
        "default_query": "Pull Turner Construction's current progress on PENN 2 from the construction costs database. Look up their historical project overruns and delays, and synthesize an operational risk assessment on contractor reliability.",
        "data_tables": ["construction_costs_ti"],
    },
    "4. Market Benchmarking (AM Focus)": {
        "description": "Benchmark proposed lease terms (base rent, free rent, TI allowance) against Penn District market comps.",
        "default_query": "Query the market comps database to average comps in the Penn District submarket. Contrast the Apex draft terms ($110.00/RSF rent, 12 months free rent, $150.00/RSF TI) and benchmark Vornado's premium positioning.",
        "data_tables": ["market_comps"],
    },
    "5. Additional Rent Escalation Forecasting (CFO Focus)": {
        "description": "Forecast opex and real estate tax escalations billed to the tenant based on base-year indices and proportionate share.",
        "default_query": "Parse Section 22 of the Apex lease to extract the proportionate share and base year. Query the opex/tax history database to compute the 2028 projected additional rent billed to the tenant.",
        "data_tables": ["tax_escalations"],
    },
}

# Initialize session states
if "is_running" not in st.session_state:
    st.session_state.is_running = False
if "agent_response" not in st.session_state:
    st.session_state.agent_response = ""
if "intermediate_steps" not in st.session_state:
    st.session_state.intermediate_steps = []

# Sidebar Scenario Selection
st.sidebar.header("Demo Scenario Explorer")
selected_story_name = st.sidebar.selectbox(
    "Choose a Scenario",
    list(STORYLINES.keys()),
    disabled=st.session_state.is_running,
)
scenario = STORYLINES[selected_story_name]

# Reset states when scenario changes
if "last_story_name" not in st.session_state:
    st.session_state.last_story_name = selected_story_name

if st.session_state.last_story_name != selected_story_name:
    st.session_state.last_story_name = selected_story_name
    st.session_state.user_query = scenario["default_query"]
    st.session_state.agent_response = ""
    st.session_state.intermediate_steps = []
    st.session_state.is_running = False

# Check for custom prompt query parameter
custom_prompt = st.query_params.get("prompt")
if custom_prompt:
    st.session_state.user_query = custom_prompt
elif "user_query" not in st.session_state:
    st.session_state.user_query = scenario["default_query"]

st.sidebar.markdown("---")
st.sidebar.markdown("### 📊 Live Data Viewer")


# Fetch table data helper
def fetch_table_data(table_name):
    client = bigquery.Client(project="genaillentsearch")
    query = f"SELECT * FROM `genaillentsearch.vornado_realestate.{table_name}`"
    return client.query(query).to_dataframe()


# Show dataset helper
for table in scenario["data_tables"]:
    try:
        df = fetch_table_data(table)
        st.sidebar.subheader(f"Table: {table}")
        st.sidebar.dataframe(df.head(5), hide_index=True)
    except Exception as e:
        st.sidebar.error(f"Error fetching {table}: {e}")

# Main Layout
col1, col2 = st.columns([3, 2])

with col1:
    st.subheader("💡 Scenario Background")
    st.info(scenario["description"])

    st.subheader("💬 Ask the AI Agent")
    st.text_area(
        "User Prompt",
        key="user_query",
        height=120,
        disabled=st.session_state.is_running,
    )

    session_service = InMemorySessionService()

    def render_intermediate_step(container, step):
        if step["type"] == "tool_call":
            container.write(f"🛠️ **Calling Tool**: `{step['name']}`")
            if step["args"]:
                container.json(step["args"])
        elif step["type"] == "tool_response":
            container.write(f"📥 **Tool Response** from `{step['name']}`:")
            container.json(step["response"])
        elif step["type"] == "code_exec":
            container.write("💻 **Executing Python Code**:")
            container.code(step["code"], language="python")
        elif step["type"] == "code_exec_result":
            container.write("📤 **Code Execution Output**:")
            container.code(step["result"])

    async def run_agent_async(prompt):
        if st.query_params.get("mock") == "true":
            yield {
                "type": "tool_call",
                "name": "analyze_lease_document",
                "args": {
                    "document_path": "gs://vornado-leases/PENN2_Apex_Fintech_Draft_Lease.pdf",
                    "query": "Extract Section 3.3 penalty triggers",
                },
            }
            await asyncio.sleep(1)
            yield {
                "type": "tool_response",
                "name": "analyze_lease_document",
                "response": {
                    "status": "success",
                    "extracted_text": "Section 3.3: Tiered Penalty triggers if delivery is delayed. Abatement: 1-for-1 for the first 30 days, 2-for-1 for days 31-90. Daily base rent rate: $30,000.",
                },
            }
            await asyncio.sleep(1)
            yield {
                "type": "code_exec",
                "code": "delay_days = 45\npenalty_days = 30 * 1 + (delay_days - 30) * 2\ndaily_rate = 30000\ntotal_penalty = penalty_days * daily_rate\nprint(f'Penalty days: {penalty_days}, Total: ${total_penalty}')",
            }
            await asyncio.sleep(1)
            yield {
                "type": "code_exec_result",
                "result": "Penalty days: 60, Total: $1800000\n",
            }
            await asyncio.sleep(1)
            yield {
                "type": "text",
                "content": "Hello! I am the Vornado Penn District Lease Optimizer Agent.\n\n",
            }
            await asyncio.sleep(0.5)
            yield {
                "type": "text",
                "content": "Based on Section 3.3 of the Apex lease draft and a 45-day delivery delay, the penalty rent abatement calculation is as follows:\n- First 30 delay days: 30 days abatement (1-for-1)\n- Remaining 15 delay days: 30 days abatement (2-for-1)\n- Total Abatement Days: **60 days**\n- Daily Base Rent: **$30,000**\n- Total Penalty Exposure: **$1,800,000**\n",
            }
            return

        session = await session_service.create_session(
            user_id="demo-user", app_name="app"
        )
        runner = Runner(
            agent=create_agent(), session_service=session_service, app_name="app"
        )
        message = types.Content(role="user", parts=[types.Part.from_text(text=prompt)])
        # Capture streaming events
        async for event in runner.run_async(
            new_message=message, user_id="demo-user", session_id=session.id
        ):
            if event.content and event.content.parts:
                for part in event.content.parts:
                    if part.function_call:
                        yield {
                            "type": "tool_call",
                            "name": part.function_call.name,
                            "args": part.function_call.args,
                        }
                    elif part.function_response:
                        yield {
                            "type": "tool_response",
                            "name": part.function_response.name,
                            "response": part.function_response.response,
                        }
                    elif part.executable_code:
                        yield {"type": "code_exec", "code": part.executable_code.code}
                    elif part.code_execution_result:
                        yield {
                            "type": "code_exec_result",
                            "result": part.code_execution_result.output,
                        }
                    elif part.text:
                        yield {"type": "text", "content": part.text}

    autorun = st.query_params.get("autorun") == "true"

    run_clicked = st.button(
        "🚀 Run Analysis",
        type="primary",
        disabled=st.session_state.is_running,
    )

    if (
        (run_clicked or autorun)
        and not st.session_state.is_running
        and not st.session_state.agent_response
    ):
        st.session_state.is_running = True
        st.session_state.agent_response = ""
        st.session_state.intermediate_steps = []
        st.rerun()

    if st.session_state.is_running:
        st.subheader("🤖 Agent Response")
        status_container = st.status(
            "Analyzing legal clauses and financial databases...", expanded=True
        )
        response_box = st.empty()
        response_box.markdown(st.session_state.agent_response)

        # Pre-render any steps already logged
        for step in st.session_state.intermediate_steps:
            render_intermediate_step(status_container, step)

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        async def main_run():
            full_response = ""
            async for event_info in run_agent_async(st.session_state.user_query):
                if event_info["type"] == "text":
                    full_response += event_info["content"]
                    st.session_state.agent_response = full_response
                    response_box.markdown(full_response)
                else:
                    st.session_state.intermediate_steps.append(event_info)
                    render_intermediate_step(status_container, event_info)
            status_container.update(
                label="Analysis complete!", state="complete", expanded=False
            )

        try:
            loop.run_until_complete(main_run())
        except Exception as e:
            st.error(f"Execution failed: {e}")
            status_container.update(label="Execution failed", state="error")
        finally:
            st.session_state.is_running = False
            st.rerun()

    elif st.session_state.agent_response:
        st.subheader("🤖 Agent Response")
        if st.session_state.intermediate_steps:
            with st.status(
                "Analysis complete!", state="complete", expanded=False
            ) as status_container:
                for step in st.session_state.intermediate_steps:
                    render_intermediate_step(status_container, step)
        st.markdown(st.session_state.agent_response)
        st.success("Analysis Complete!")

with col2:
    st.subheader("📈 Interactive Visualisations")

    if "construction_costs_ti" in scenario["data_tables"]:
        st.markdown("#### Contractor Timelines & Cost Overruns")
        try:
            df_costs = fetch_table_data("construction_costs_ti")

            # Bar chart for delays
            fig_delay = px.bar(
                df_costs,
                x="contractor_name",
                y="delay_days",
                color="property_name",
                title="Construction Delays (Days) by Contractor",
                labels={"delay_days": "Delay (Days)", "contractor_name": "Contractor"},
                barmode="group",
            )
            st.plotly_chart(fig_delay, use_container_width=True)

            # Scatter plot budget vs actual cost per RSF
            df_costs["cost_variance_rsf"] = (
                df_costs["actual_cost_per_rsf"] - df_costs["budgeted_cost_per_rsf"]
            )
            fig_cost = px.bar(
                df_costs,
                x="contractor_name",
                y="cost_variance_rsf",
                color="property_name",
                title="TI Cost Variance ($/RSF) from Budget",
                labels={
                    "cost_variance_rsf": "Variance ($/RSF)",
                    "contractor_name": "Contractor",
                },
            )
            st.plotly_chart(fig_cost, use_container_width=True)

        except Exception as e:
            st.write("Could not render construction charts:", e)

    if "market_comps" in scenario["data_tables"]:
        st.markdown("#### Submarket Benchmarking (Base Rent vs TI)")
        try:
            df_comps = fetch_table_data("market_comps")

            # Let's add Apex Fintech as a pseudo-row for visual benchmarking
            apex_row = pd.DataFrame(
                [
                    {
                        "comp_id": "APEX DRAFT",
                        "property_name": "PENN 2 (Apex Fintech)",
                        "submarket": "Penn District",
                        "execution_date": "2027-01-01",
                        "rsf": 130000,
                        "lease_term_months": 180,
                        "base_rent_per_rsf": 110.0,
                        "free_rent_months": 12,
                        "ti_allowance_per_rsf": 150.0,
                        "source": "Draft Lease",
                    }
                ]
            )
            df_all = pd.concat([df_comps, apex_row], ignore_index=True)

            fig_scatter = px.scatter(
                df_all,
                x="base_rent_per_rsf",
                y="ti_allowance_per_rsf",
                size="rsf",
                color="property_name",
                symbol="submarket",
                title="Market Comps: Base Rent vs TI Allowance (Bubble Size = RSF)",
                labels={
                    "base_rent_per_rsf": "Base Rent ($/RSF)",
                    "ti_allowance_per_rsf": "TI Allowance ($/RSF)",
                },
            )
            st.plotly_chart(fig_scatter, use_container_width=True)

        except Exception as e:
            st.write("Could not render comps charts:", e)

    if "tax_escalations" in scenario["data_tables"]:
        st.markdown("#### Historical & Projected Taxes & OpEx")
        try:
            df_esc = fetch_table_data("tax_escalations")
            df_penn2 = df_esc[df_esc["property_name"] == "PENN 2"].sort_values("year")

            fig_line = px.line(
                df_penn2,
                x="year",
                y=["real_estate_tax_per_rsf", "operating_expense_per_rsf"],
                title="PENN 2 Escalation Components ($/RSF)",
                labels={
                    "value": "Cost ($/RSF)",
                    "year": "Year",
                    "variable": "Index Type",
                },
                markers=True,
            )
            st.plotly_chart(fig_line, use_container_width=True)

        except Exception as e:
            st.write("Could not render escalation charts:", e)
