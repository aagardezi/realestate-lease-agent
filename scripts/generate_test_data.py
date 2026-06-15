#!/usr/bin/env python3
"""
Self-bootstrapping script to generate highly detailed unstructured (PDF) and
structured (CSV) test data for the Real Estate Lease Agent Demo.
Represents a institutional-grade commercial office lease dataset.
"""

import os
import sys
import subprocess

# Self-bootstrap virtualenv if reportlab or pandas is missing
try:
    import reportlab
    import pandas
except ImportError:
    print("Required libraries (reportlab or pandas) not found. Setting up virtual environment...")
    venv_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".venv"))
    if not os.path.exists(venv_dir):
        print(f"Creating virtual environment in {venv_dir}...")
        subprocess.run([sys.executable, "-m", "venv", venv_dir], check=True)
    
    # Identify the python executable in the venv
    if os.name == "nt":
        venv_python = os.path.join(venv_dir, "Scripts", "python.exe")
        venv_pip = os.path.join(venv_dir, "Scripts", "pip.exe")
    else:
        venv_python = os.path.join(venv_dir, "bin", "python")
        venv_pip = os.path.join(venv_dir, "bin", "pip")
        
    print("Installing reportlab and pandas in virtual environment...")
    subprocess.run([venv_pip, "install", "--upgrade", "pip"], check=True)
    subprocess.run([venv_pip, "install", "--index-url", "https://pypi.org/simple", "reportlab", "pandas"], check=True)
    
    print("Re-executing script with virtual environment python...")
    subprocess.run([venv_python] + sys.argv, check=True)
    sys.exit(0)

# The rest of the script executes only when libraries are available
import csv
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas

# Define directories
workspace_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
structured_dir = os.path.join(workspace_dir, "data", "structured")
unstructured_dir = os.path.join(workspace_dir, "data", "unstructured")
scripts_dir = os.path.join(workspace_dir, "scripts")

for d in [structured_dir, unstructured_dir, scripts_dir]:
    os.makedirs(d, exist_ok=True)

# ---------------------------------------------------------
# Dynamic Page Numbering and Running Header/Footer
# ---------------------------------------------------------
class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        canvas.Canvas.__init__(self, *args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_number(num_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_page_number(self, page_count):
        if self._pageNumber == 1:
            return  # Skip first page (title/cover page)
        self.saveState()
        self.setFont("Helvetica-Bold", 8)
        self.setFillColor(colors.HexColor("#4A5568"))
        
        # Header
        self.drawString(54, 750, "THE NEW PENN DISTRICT OFFICE LEASE OPTIMIZER - DEMO DATA DRAFT")
        self.setStrokeColor(colors.HexColor("#CBD5E1"))
        self.setLineWidth(0.5)
        self.line(54, 742, 558, 742)
        
        # Footer
        text = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(558, 40, text)
        self.drawString(54, 40, "CONFIDENTIAL - PROPERTY OF VORNADO REALTY TRUST - FOR DEMONSTRATION ONLY")
        self.line(54, 52, 558, 52)
        self.restoreState()


# ---------------------------------------------------------
# Structured Data Files Generation
# ---------------------------------------------------------
def create_csv_files():
    print("Generating structured CSV datasets...")
    
    # Historical Leases
    historical_leases = [
        ["lease_id", "property_name", "tenant_name", "execution_date", "commencement_date", "lease_term_months", "rsf", "initial_base_rent_per_rsf", "free_rent_months", "ti_allowance_per_rsf", "step_up_percentage", "step_up_interval_months", "industry", "lease_status"],
        ["L-1001", "PENN 1", "Cisco Systems Inc.", "2023-04-12", "2023-11-01", 120, 100000, 90.00, 8, 120.00, 10.0, 60, "Technology", "Active"],
        ["L-1002", "PENN 1", "Empire State Development", "2022-09-15", "2023-03-01", 180, 115000, 85.00, 10, 130.00, 10.0, 60, "Government", "Active"],
        ["L-1003", "PENN 2", "MSG Entertainment Corp.", "2024-02-18", "2024-10-01", 240, 120000, 105.00, 12, 160.00, 10.0, 60, "Entertainment", "Active"],
        ["L-1004", "770 Broadway", "Meta Platforms Inc.", "2021-06-30", "2022-01-01", 120, 300000, 115.00, 9, 110.00, 10.0, 60, "Technology", "Active"],
        ["L-1005", "1290 Ave of the Americas", "Neuberger Berman", "2018-05-10", "2019-01-01", 180, 350000, 98.00, 12, 140.00, 12.5, 60, "Finance", "Active"],
        ["L-1006", "PENN 11", "Dell Technologies", "2023-10-05", "2024-04-01", 84, 50000, 88.00, 6, 100.00, 10.0, 36, "Technology", "Active"],
        ["L-1007", "PENN 1", "Samsung Electronics", "2021-11-12", "2022-05-01", 120, 75000, 92.00, 6, 110.00, 10.0, 60, "Technology", "Active"],
        ["L-1008", "770 Broadway", "Macy's Inc.", "2015-08-20", "2016-02-01", 180, 150000, 75.00, 8, 80.00, 10.0, 60, "Retail", "Active"],
        ["L-1009", "1500 Broadway", "Disney Store", "2017-03-14", "2017-10-01", 120, 40000, 120.00, 4, 70.00, 12.0, 60, "Retail", "Expired"],
        ["L-1010", "PENN 11", "Spinola Legal", "2019-12-01", "2020-05-01", 60, 15000, 80.00, 3, 40.00, 10.0, 36, "Legal", "Active"]
    ]
    with open(os.path.join(structured_dir, "historical_leases.csv"), "w", newline="") as f:
        csv.writer(f).writerows(historical_leases)

    # Construction Costs & TI
    construction_costs = [
        ["project_id", "property_name", "project_type", "contractor_name", "start_date", "completion_date", "budgeted_cost_per_rsf", "actual_cost_per_rsf", "delay_days", "reason_for_delay"],
        ["P-2001", "PENN 1", "Tenant Fit-Out", "Turner Construction", "2023-05-01", "2023-10-25", 120.00, 128.50, 25, "HVAC equipment delivery delays"],
        ["P-2002", "PENN 1", "Tenant Fit-Out", "Structure Tone", "2022-10-01", "2023-02-28", 130.00, 131.20, 0, "None"],
        ["P-2003", "PENN 2", "Lobby Redevelopment", "Skanska USA", "2022-03-01", "2024-08-30", 250.00, 278.00, 120, "Structural steel fabrication delays"],
        ["P-2004", "770 Broadway", "Tenant Fit-Out", "L&K Partners", "2021-07-01", "2021-12-15", 110.00, 109.80, 0, "None"],
        ["P-2005", "1290 Ave of Americas", "Infrastructure Upgrade", "Gilbane Building Co", "2018-06-01", "2018-12-20", 140.00, 146.50, 20, "Permitting delays with DOB"],
        ["P-2006", "PENN 11", "Lobby Upgrade", "Structure Tone", "2023-11-01", "2024-03-15", 100.00, 102.00, 15, "Subcontractor labor shortage"],
        ["P-2007", "PENN 2", "Tenant Fit-Out", "Turner Construction", "2026-06-01", "2027-07-15", 150.00, 158.00, 44, "HVAC air handling unit delays"],
        ["P-2008", "PENN 1", "Tenant Fit-Out", "Structure Tone", "2026-08-15", "2026-12-30", 130.00, 130.00, 0, "None"]
    ]
    with open(os.path.join(structured_dir, "construction_costs_ti.csv"), "w", newline="") as f:
        csv.writer(f).writerows(construction_costs)

    # Market Comps
    market_comps = [
        ["comp_id", "property_name", "submarket", "execution_date", "rsf", "lease_term_months", "base_rent_per_rsf", "free_rent_months", "ti_allowance_per_rsf", "source"],
        ["C-3001", "One Penn Plaza", "Penn District", "2025-05-10", 50000, 120, 92.00, 7, 125.00, "JLL"],
        ["C-3002", "Two Penn Plaza", "Penn District", "2025-11-15", 80000, 180, 108.00, 11, 145.00, "CBRE"],
        ["C-3003", "11 Penn Plaza", "Penn District", "2025-08-01", 60000, 120, 85.00, 6, 100.00, "Cushman & Wakefield"],
        ["C-3004", "330 West 34th St", "Midtown West", "2025-12-20", 40000, 120, 82.00, 5, 95.00, "JLL"],
        ["C-3005", "One Penn Plaza", "Penn District", "2026-02-18", 30000, 120, 89.00, 6, 115.00, "Cushman & Wakefield"],
        ["C-3006", "1290 Ave of Americas", "Midtown", "2025-09-05", 100000, 120, 96.00, 8, 120.00, "Newmark"],
        ["C-3007", "770 Broadway", "Midtown South", "2025-06-12", 85000, 120, 110.00, 10, 105.00, "CBRE"]
    ]
    with open(os.path.join(structured_dir, "market_comps.csv"), "w", newline="") as f:
        csv.writer(f).writerows(market_comps)

    # Tax Escalations
    tax_escalations = [
        ["property_name", "year", "real_estate_tax_per_rsf", "operating_expense_per_rsf", "base_year_tax", "base_year_opex"],
        ["PENN 1", 2021, 18.50, 22.00, None, None],
        ["PENN 1", 2022, 19.10, 23.10, None, None],
        ["PENN 1", 2023, 19.80, 24.50, None, None],
        ["PENN 1", 2024, 20.40, 25.20, None, None],
        ["PENN 1", 2025, 21.10, 26.00, None, None],
        ["PENN 1", 2026, 21.80, 26.80, 21.80, 26.80],
        ["PENN 1", 2027, 22.50, 27.50, 21.80, 26.80],
        ["PENN 1", 2028, 23.20, 28.30, 21.80, 26.80],
        ["PENN 2", 2021, 20.00, 24.00, None, None],
        ["PENN 2", 2022, 20.80, 25.20, None, None],
        ["PENN 2", 2023, 21.50, 26.50, None, None],
        ["PENN 2", 2024, 22.20, 27.30, None, None],
        ["PENN 2", 2025, 23.00, 28.20, None, None],
        ["PENN 2", 2026, 23.80, 29.10, None, None],
        ["PENN 2", 2027, 24.60, 30.00, 24.60, 30.00],
        ["PENN 2", 2028, 25.40, 31.00, 24.60, 30.00]
    ]
    with open(os.path.join(structured_dir, "tax_escalations.csv"), "w", newline="") as f:
        csv.writer(f).writerows(tax_escalations)
    print("CSV files generated successfully.")


# ---------------------------------------------------------
# PDF Document Generation Logic
# ---------------------------------------------------------
def build_apex_lease_pdf():
    pdf_path = os.path.join(unstructured_dir, "PENN2_Apex_Fintech_Draft_Lease.pdf")
    print(f"Generating PDF: {pdf_path}...")
    doc = SimpleDocTemplate(pdf_path, pagesize=letter, leftMargin=54, rightMargin=54, topMargin=72, bottomMargin=72)
    story = []
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'TitleStyle', parent=styles['Heading1'], fontName='Helvetica-Bold', fontSize=22, leading=26, textColor=colors.HexColor('#0F172A'), alignment=1, spaceAfter=15
    )
    subtitle_style = ParagraphStyle(
        'SubTitleStyle', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=10, leading=14, textColor=colors.HexColor('#1E293B'), alignment=1, spaceAfter=20
    )
    heading_style = ParagraphStyle(
        'HeadingStyle', parent=styles['Heading2'], fontName='Helvetica-Bold', fontSize=11, leading=15, textColor=colors.HexColor('#0F172A'), spaceBefore=14, spaceAfter=6, keepWithNext=True
    )
    body_style = ParagraphStyle(
        'BodyStyle', parent=styles['BodyText'], fontName='Helvetica', fontSize=9, leading=13.5, textColor=colors.HexColor('#334155'), spaceAfter=5
    )
    table_hdr = ParagraphStyle(
        'TableHdr', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=8, leading=10, textColor=colors.white
    )
    table_cell = ParagraphStyle(
        'TableCell', parent=styles['Normal'], fontName='Helvetica', fontSize=8, leading=10, textColor=colors.HexColor('#1E293B')
    )

    # Title Page
    story.append(Spacer(1, 100))
    story.append(Paragraph("OFFICE LEASE AGREEMENT", title_style))
    story.append(Spacer(1, 15))
    story.append(Paragraph("LANDLORD: PENN 2 OWNER LLC<br/>(A Subsidiary of Vornado Realty Trust)", subtitle_style))
    story.append(Paragraph("TENANT: APEX FINTECH SOLUTIONS LLC", subtitle_style))
    story.append(Spacer(1, 30))
    story.append(Paragraph("Premises: Fourteenth (14th) & Fifteenth (15th) Floors<br/>Two Penn Plaza (PENN 2), New York, NY", subtitle_style))
    story.append(Paragraph("Execution Date: November 1, 2026 (Draft for Negotiation)", subtitle_style))
    story.append(PageBreak())
    
    # Lease Agreement Core
    story.append(Paragraph("LEASE AGREEMENT", title_style))
    story.append(Spacer(1, 10))
    story.append(Paragraph("THIS LEASE AGREEMENT (the \"Lease\") is made and entered into as of the Execution Date, by and between Landlord and Tenant, as identified above. Landlord is a Delaware limited liability company with principal offices at c/o Vornado Realty Trust, 888 Seventh Avenue, New York, New York. Tenant is a Delaware limited liability company with principal offices at 140 Broadway, New York, New York.", body_style))
    story.append(Paragraph("WITNESSETH: In consideration of the mutual covenants and agreements herein contained, Landlord and Tenant hereby covenant and agree as follows:", body_style))
    
    # Section 1
    story.append(Paragraph("SECTION 1: DEMISED PREMISES AND TERM", heading_style))
    story.append(Paragraph("1.1. <b>Demised Premises.</b> Landlord hereby leases to Tenant, and Tenant hereby hires from Landlord, the entire rentable area of the fourteenth (14th) and fifteenth (15th) floors (the \"Premises\") of the building located at Two Penn Plaza, New York, NY (the \"Building\"). The Premises are stipulated to contain a total rentable square footage of 130,000 Rentable Square Feet (RSF), divided equally as 65,000 RSF on the fourteenth floor and 65,000 RSF on the fifteenth floor. Measurements are conducted pursuant to the 2017 BOMA Standard for Office Buildings, and are not subject to re-measurement by either party.", body_style))
    story.append(Paragraph("1.2. <b>Lease Term.</b> The term of this Lease (the \"Term\") shall be fifteen (15) years and six (6) months, commencing on the Commencement Date (as defined in Section 3) and expiring on the last day of the 186th full calendar month following the Commencement Date, unless earlier terminated or extended pursuant to the terms hereof. Tenant shall have no right to occupy the Premises prior to the Commencement Date except under a signed License Agreement.", body_style))
    
    # Section 2
    story.append(Paragraph("SECTION 2: BASE RENT AND ADDITIONAL RENT", heading_style))
    story.append(Paragraph("2.1. <b>Base Rent Payments.</b> Tenant covenants and agrees to pay to Landlord annual base rent (\"Base Rent\") in equal monthly installments, in advance, on the first day of each calendar month during the Term, except that the first twelve (12) months of Base Rent shall be abated as set forth in Section 4. If the Commencement Date occurs on a day other than the first day of a calendar month, the Rent for the partial month shall be prorated on a per diem basis, and the initial abatement period shall begin on the first day of the next full calendar month. Rent shall be paid via wire transfer in immediately available funds to the bank account designated in writing by Landlord, without any setoff, deduction, or abatement whatsoever except as explicitly provided herein.", body_style))
    story.append(Paragraph("2.2. <b>Rent Schedule.</b> The schedule of Base Rent during the Term is established as follows:", body_style))
    
    rent_data = [
        [Paragraph("Lease Month Range", table_hdr), Paragraph("Base Rent Rate / RSF / Yr", table_hdr), Paragraph("Annualized Base Rent", table_hdr), Paragraph("Monthly Base Rent", table_hdr)],
        [Paragraph("Months 1 - 12 (Abated)", table_cell), Paragraph("$0.00", table_cell), Paragraph("$0.00", table_cell), Paragraph("$0.00", table_cell)],
        [Paragraph("Months 13 - 72", table_cell), Paragraph("$110.00", table_cell), Paragraph("$14,300,000.00", table_cell), Paragraph("$1,191,666.67", table_cell)],
        [Paragraph("Months 73 - 132", table_cell), Paragraph("$121.00", table_cell), Paragraph("$15,730,000.00", table_cell), Paragraph("$1,310,833.33", table_cell)],
        [Paragraph("Months 133 - 186", table_cell), Paragraph("$133.10", table_cell), Paragraph("$17,303,000.00", table_cell), Paragraph("$1,441,916.67", table_cell)]
    ]
    t1 = Table(rent_data, colWidths=[130, 120, 120, 134])
    t1.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0F172A')),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#F8FAFC')])
    ]))
    story.append(t1)
    story.append(Spacer(1, 8))
    
    story.append(Paragraph("2.3. <b>Late Payments & Interest.</b> If Tenant fails to pay any installment of Base Rent or Additional Rent within five (5) days after the due date, Tenant shall pay Landlord a late charge equal to five percent (5%) of the overdue amount. In addition, any overdue amount shall bear interest from the due date until paid at a rate equal to the lesser of: (i) prime rate as published in the Wall Street Journal plus four percent (4%) per annum, or (ii) the maximum legal rate allowable under New York law.", body_style))
    story.append(Paragraph("2.4. <b>Additional Rent.</b> All amounts other than Base Rent payable by Tenant under this Lease, including Operating Expense and Real Estate Tax escalations, shall be deemed \"Additional Rent\" and Landlord shall have all rights and remedies for nonpayment of Additional Rent as are available for nonpayment of Base Rent.", body_style))
    
    # Section 3
    story.append(Paragraph("SECTION 3: COMMENCEMENT DATE AND LANDLORD DELAY", heading_style))
    story.append(Paragraph("3.1. <b>Commencement Date.</b> The \"Commencement Date\" shall be defined as the date on which Landlord delivers the Premises to Tenant with the Landlord's Work (defined in Exhibit B) Substantially Completed (the \"Delivery Date\"). The anticipated Delivery Date is January 1, 2027 (the \"Target Commencement Date\").", body_style))
    story.append(Paragraph("3.2. <b>Substantial Completion.</b> Landlord's Work shall be deemed \"Substantially Completed\" when (i) the core mechanical, electrical, plumbing, HVAC, and life-safety systems serving the Premises are functional and ready for connection by Tenant's contractors, (ii) the double-height perimeter glass facade is closed and weatherproofed, (iii) core restrooms on floors 14 and 15 are completed to building standards, and (iv) Landlord's architect certifies that the work has been completed in compliance with plans and a temporary or permanent Certificate of Occupancy has been issued for the Premises.", body_style))
    story.append(Paragraph("3.3. <b>Landlord Delay Concessions.</b>", body_style))
    story.append(Paragraph("3.3.1. <b>Initial Delay (1-for-1 Penalty).</b> If the Delivery Date has not occurred on or before June 1, 2027 (the \"Target Delivery Date\"), then as Tenant's sole and exclusive remedy (except as provided in Sections 3.3.2 and 3.3.3 below), Tenant shall receive one (1) day of additional Base Rent abatement (to be applied immediately following the initial 12-month abatement period) for each calendar day of delay in delivery from June 1, 2027, through and including September 1, 2027.", body_style))
    story.append(Paragraph("3.3.2. <b>Severe Delay (2-for-1 Penalty).</b> If the Delivery Date has not occurred on or before September 1, 2027, then starting on September 2, 2027, and continuing until the actual Delivery Date, the penalty shall increase to two (2) days of additional Base Rent abatement for each calendar day of delay in delivery. (For the avoidance of doubt, if delivery occurs on September 15, the total abatement would equal 93 days under the 1-for-1 tier + 28 days under the 2-for-1 tier, representing 121 total penalty days).", body_style))
    story.append(Paragraph("3.3.3. <b>Outside Date and Termination Right.</b> If the Delivery Date has not occurred on or before December 31, 2027 (the \"Outside Delivery Date\"), Tenant shall have the right, exercisable by giving ten (10) days' written notice to Landlord at any time prior to the occurrence of the Delivery Date, to terminate this Lease. If Tenant elects to terminate, Landlord shall immediately refund the security deposit, and neither party shall have further obligation to the other.", body_style))
    story.append(Paragraph("3.4. <b>Force Majeure Delay.</b> Any delay in Substantial Completion of Landlord's Work caused by acts of God, war, civil commotion, strikes, lockouts, or industry-wide material shortages shall constitute \"Force Majeure Delay\" and shall extend the Target Delivery Date and Outside Delivery Date day-for-day, up to a maximum extension of sixty (60) days, provided Landlord gives Tenant written notice of such event within five (5) days of its occurrence. Force Majeure Delay shall not include general contractor delays, delays in subcontractor scheduling, or financial inability.", body_style))
    
    story.append(PageBreak())
    
    # Section 14
    story.append(Paragraph("SECTION 14: TENANT IMPROVEMENT ALLOWANCE", heading_style))
    story.append(Paragraph("14.1. <b>TI Allowance.</b> Landlord shall provide Tenant with a one-time tenant improvement allowance (the \"Tenant Improvement Allowance\" or \"TI Allowance\") in the amount of $150.00 per RSF of the Premises, representing a total sum of $19,500,000.00, which shall be used solely for the design, permitting, construction, and installation of Tenant's initial alterations and leasehold improvements (the \"Tenant's Work\") in accordance with plans approved by Landlord. Under no circumstances shall Landlord be obligated to disburse more than the total TI Allowance.", body_style))
    story.append(Paragraph("14.2. <b>Disbursement Schedule.</b> Landlord shall disburse the TI Allowance in progress payments to Tenant's general contractor or directly to Tenant, within twenty (20) business days following Tenant's submission of a written draw request accompanied by contractor invoices, partial lien waivers from the general contractor and all subcontractors, architect's certifications, and inspection logs, in accordance with the following milestones:", body_style))
    
    ti_data = [
        [Paragraph("Milestone Phase", table_hdr), Paragraph("% Release", table_hdr), Paragraph("Disbursement Amount", table_hdr), Paragraph("Required Documentation / Progress", table_hdr)],
        [Paragraph("Milestone 1: Structural Demolition & Demising Walls", table_cell), Paragraph("20%", table_cell), Paragraph("$3,900,000.00", table_cell), Paragraph("Complete demolition of existing layout, structural slab repairs, and erection of boundary demising walls.", table_cell)],
        [Paragraph("Milestone 2: Rough-In Mechanical & Electrical (MEP)", table_cell), Paragraph("30%", table_cell), Paragraph("$5,850,000.00", table_cell), Paragraph("Installation of primary horizontal ductwork, electrical conduits, and plumbing lines inside the ceiling and floor cavities.", table_cell)],
        [Paragraph("Milestone 3: Sheetrock & Drywall Close-In", table_cell), Paragraph("30%", table_cell), Paragraph("$5,850,000.00", table_cell), Paragraph("Installation of drywall studs and sheetrock, framing of individual rooms, and primary inspections signed off.", table_cell)],
        [Paragraph("Milestone 4: Final CO & Certificate of Occupancy", table_cell), Paragraph("20%", table_cell), Paragraph("$3,900,000.00", table_cell), Paragraph("Issuance of temporary or permanent Certificate of Occupancy, delivery of final lien waivers, and final sign-off.", table_cell)]
    ]
    t2 = Table(ti_data, colWidths=[140, 50, 110, 204])
    t2.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0F172A')),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#F8FAFC')])
    ]))
    story.append(t2)
    story.append(Spacer(1, 8))
    story.append(Paragraph("14.3. <b>Unused Allowance.</b> If any portion of the TI Allowance remains undisbursed after the completion of Tenant's Work and final sign-off, Tenant may apply up to ten percent (10%) of the unused portion (not to exceed $195,000.00) as a credit against monthly Base Rent next coming due, and any remaining balance thereafter shall revert to Landlord's benefit.", body_style))

    # Section 22
    story.append(Paragraph("SECTION 22: TAXES AND OPERATING EXPENSES", heading_style))
    story.append(Paragraph("22.1. <b>Tenant's Proportionate Share.</b> Tenant shall pay to Landlord, as Additional Rent, Tenant's Proportionate Share of any increases in Real Estate Taxes (RET) and Operating Expenses (OpEx) over the respective Base Year amounts.", body_style))
    story.append(Paragraph("22.2. <b>Definitions.</b>", body_style))
    story.append(Paragraph("22.2.1. <b>Tenant's Proportionate Share.</b> The percentage calculated by dividing the rentable square footage of the Premises (130,000 RSF) by the total rentable office area of the Building (stipulated as 1,733,333 RSF), which represents <b>7.50%</b>.", body_style))
    story.append(Paragraph("22.2.2. <b>Base Tax Year.</b> The Base Tax Year shall be the Real Estate Tax Fiscal Year 2027 (commencing July 1, 2026 and ending June 30, 2027). The Base Tax amount shall be the actual real estate taxes levied against the Building's office portion during said fiscal year.", body_style))
    story.append(Paragraph("22.2.3. <b>Base Operating Year.</b> The Base Operating Year shall be the Operating Expense Calendar Year 2027 (January 1, 2027 to December 31, 2027). The Base Operating Expense amount shall be the actual, audited Operating Expenses incurred by Landlord in the operation of the Building.", body_style))
    story.append(Paragraph("22.3. <b>Exclusions from Operating Expenses.</b> Operating Expenses shall not include: (a) capital expenditures, (b) leasing commissions and advertising costs, (c) salaries of officers or directors above the grade of building manager, (d) legal fees incurred in disputes with other tenants, (e) expenses resulting from Landlord's negligence or violation of law, and (f) any cost reimbursed by insurance or other third parties.", body_style))
    story.append(Paragraph("22.4. <b>Estimation and Reconciliation.</b> Landlord shall provide Tenant with a monthly estimate of Tenant's share of escalations, which Tenant shall pay as Additional Rent. Within one hundred twenty (120) days after the end of each calendar year, Landlord shall deliver an audited statement of actual expenses. If Tenant's payments exceeded actual liability, Landlord shall credit the difference against next rent due. If payments were short, Tenant shall pay the balance within thirty (30) days. Tenant shall have the right to audit Landlord's books and records upon ten (10) days' notice, which audit must be performed by a certified public accountant on a non-contingency basis.", body_style))

    # Section 6: Use, Repairs, and Maintenance
    story.append(Paragraph("SECTION 6: USE, REPAIRS, AND MAINTENANCE", heading_style))
    story.append(Paragraph("6.1. <b>Permitted Use.</b> Tenant shall use and occupy the Premises solely for high-end professional administrative office purposes and general business services. No retail, medical, training facility, or public government agency uses shall be permitted without Landlord's prior written consent.", body_style))
    story.append(Paragraph("6.2. <b>Landlord's Maintenance Obligations.</b> Landlord shall maintain and repair the structural elements of the Building (including foundations, load-bearing walls, roof, exterior windows, and elevators) and the core building mechanical, electrical, plumbing, and HVAC systems. Landlord shall provide cleaning services to standard office floors five days per week.", body_style))
    story.append(Paragraph("6.3. <b>Tenant's Maintenance Obligations.</b> Tenant shall, at its sole cost, maintain and repair the non-structural interior elements of the Premises (including partitions, interior doors, floor cover, local wiring, plumbing fixtures installed by Tenant, and supplemental HVAC systems). Tenant shall not make any major structural changes or alterations without Landlord's prior written consent.", body_style))

    # Section 7: Subleasing and Assignment
    story.append(Paragraph("SECTION 7: SUBLEASING AND ASSIGNMENT", heading_style))
    story.append(Paragraph("7.1. <b>Landlord Consent Required.</b> Tenant shall not assign, sublease, mortgage, or otherwise transfer its interest under this Lease without Landlord's prior written consent, which consent shall not be unreasonably withheld, delayed, or conditioned. Any unauthorized transfer shall be void and constitute a material Default.", body_style))
    story.append(Paragraph("7.2. <b>Permitted Transfers.</b> Notwithstanding Section 7.1, Tenant may assign or sublet the Premises without Landlord's consent to: (a) any parent or subsidiary corporation, (b) any entity resulting from a merger or consolidation with Tenant, or (c) any entity acquiring all or substantially all of Tenant's assets, provided that (i) Tenant is not in default, (ii) the successor entity has a tangible net worth equal to or greater than Tenant's net worth at the execution of this Lease, and (iii) the transferee continues the permitted office use.", body_style))

    # Section 8: Insurance
    story.append(Paragraph("SECTION 8: INSURANCE AND INDEMNIFICATION", heading_style))
    story.append(Paragraph("8.1. <b>Tenant Insurance.</b> Tenant shall maintain throughout the Term: (a) Commercial General Liability Insurance with limits of not less than $5,000,000.00 per occurrence, (b) Property Insurance covering all tenant improvements and personal property for full replacement value, and (c) Worker's Compensation insurance. Landlord and Vornado Realty Trust shall be named as additional insureds.", body_style))
    story.append(Paragraph("8.2. <b>Waiver of Subrogation.</b> Landlord and Tenant hereby waive any rights of recovery against each other for loss or damage to property to the extent covered by valid and collectible insurance policies, and each shall obtain waivers of subrogation from their respective insurers.", body_style))

    # Section 9: Holdover
    story.append(Paragraph("SECTION 9: HOLDOVER", heading_style))
    story.append(Paragraph("9.1. <b>Holdover Rent.</b> If Tenant remains in possession of the Premises after the expiration of the Term, Tenant shall occupy the space as a tenant-at-sufferance. Tenant shall pay Base Rent during the holdover period at a rate equal to: (i) one hundred fifty percent (150%) of the Base Rent in effect immediately prior to expiration for the first thirty (30) days, and (ii) two hundred percent (200%) of such Base Rent thereafter, plus all Additional Rent escalations. Tenant shall also indemnify Landlord against all claims resulting from Tenant's delay in surrendering the Premises.", body_style))

    # Section 10: Miscellaneous
    story.append(Paragraph("SECTION 10: NOTICES AND GOVERNING LAW", heading_style))
    story.append(Paragraph("10.1. <b>Notices.</b> All notices under this Lease shall be in writing and delivered via certified mail or overnight national courier (e.g. FedEx) to Landlord c/o Vornado Realty Trust, 888 Seventh Avenue, New York, NY, and to Tenant at the Premises.", body_style))
    story.append(Paragraph("10.2. <b>Governing Law.</b> This Lease shall be governed by, construed, and enforced in accordance with the laws of the State of New York. Any litigation arising under this Lease shall be brought exclusively in the state or federal courts located in New York County, New York.", body_style))
    
    story.append(Spacer(1, 20))
    story.append(Paragraph("IN WITNESS WHEREOF, Landlord and Tenant have executed this Lease as of the date first written above.", body_style))
    story.append(Spacer(1, 10))
    
    sig_data = [
        [Paragraph("<b>LANDLORD:</b><br/>PENN 2 OWNER LLC<br/>By: Vornado Realty Trust, agent<br/><br/>By: ___________________________<br/>Name: Steven Roth<br/>Title: Chairman & CEO", body_style),
         Paragraph("<b>TENANT:</b><br/>APEX FINTECH SOLUTIONS LLC<br/><br/><br/>By: ___________________________<br/>Name: William Capuzzi<br/>Title: Chief Executive Officer", body_style)]
    ]
    t_sig = Table(sig_data, colWidths=[252, 252])
    t_sig.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 10)
    ]))
    story.append(t_sig)
    
    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"PDF generated: {pdf_path}")


def build_biomed_lease_pdf():
    pdf_path = os.path.join(unstructured_dir, "PENN1_BioMed_Diagnostics_Draft_Lease.pdf")
    print(f"Generating PDF: {pdf_path}...")
    doc = SimpleDocTemplate(pdf_path, pagesize=letter, leftMargin=54, rightMargin=54, topMargin=72, bottomMargin=72)
    story = []
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'TitleStyle', parent=styles['Heading1'], fontName='Helvetica-Bold', fontSize=22, leading=26, textColor=colors.HexColor('#0F172A'), alignment=1, spaceAfter=15
    )
    subtitle_style = ParagraphStyle(
        'SubTitleStyle', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=10, leading=14, textColor=colors.HexColor('#1E293B'), alignment=1, spaceAfter=20
    )
    heading_style = ParagraphStyle(
        'HeadingStyle', parent=styles['Heading2'], fontName='Helvetica-Bold', fontSize=11, leading=15, textColor=colors.HexColor('#0F172A'), spaceBefore=14, spaceAfter=6, keepWithNext=True
    )
    body_style = ParagraphStyle(
        'BodyStyle', parent=styles['BodyText'], fontName='Helvetica', fontSize=9, leading=13.5, textColor=colors.HexColor('#334155'), spaceAfter=5
    )
    table_hdr = ParagraphStyle(
        'TableHdr', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=8, leading=10, textColor=colors.white
    )
    table_cell = ParagraphStyle(
        'TableCell', parent=styles['Normal'], fontName='Helvetica', fontSize=8, leading=10, textColor=colors.HexColor('#1E293B')
    )

    story.append(Spacer(1, 100))
    story.append(Paragraph("OFFICE LEASE AGREEMENT", title_style))
    story.append(Spacer(1, 15))
    story.append(Paragraph("LANDLORD: PENN 1 OWNER LLC<br/>(A Subsidiary of Vornado Realty Trust)", subtitle_style))
    story.append(Paragraph("TENANT: BIOMED DIAGNOSTICS INC.", subtitle_style))
    story.append(Spacer(1, 30))
    story.append(Paragraph("Premises: Twenty-Second (22nd) Floor<br/>One Penn Plaza (PENN 1), New York, NY", subtitle_style))
    story.append(Paragraph("Execution Date: August 1, 2026 (Draft for Negotiation)", subtitle_style))
    story.append(PageBreak())
    
    story.append(Paragraph("LEASE AGREEMENT", title_style))
    story.append(Spacer(1, 10))
    story.append(Paragraph("THIS LEASE AGREEMENT (the \"Lease\") is made and entered into by and between Landlord and Tenant, as defined above. Landlord is a Delaware limited liability company with principal offices at c/o Vornado Realty Trust, 888 Seventh Avenue, New York, New York. Tenant is a Delaware corporation with principal offices at 500 Plaza Drive, Secaucus, New Jersey.", body_style))
    
    story.append(Paragraph("SECTION 1: DEMISED PREMISES AND TERM", heading_style))
    story.append(Paragraph("1.1. <b>Demised Premises.</b> Landlord leases to Tenant the entire rentable area of the twenty-second (22nd) floor (the \"Premises\") of the building located at One Penn Plaza, New York, NY. The Premises contain a total rentable square footage of 45,000 Rentable Square Feet (RSF) measured to BOMA 2017 standards.", body_style))
    story.append(Paragraph("1.2. <b>Lease Term.</b> The term of this Lease shall be ten (10) years, commencing on the Commencement Date and expiring on the last day of the 120th full calendar month following the Commencement Date.", body_style))
    
    story.append(Paragraph("SECTION 2: BASE RENT", heading_style))
    story.append(Paragraph("2.1. <b>Base Rent Payments.</b> Tenant shall pay Base Rent in equal monthly installments, except that the first six (6) months of Base Rent shall be abated as set forth in Section 4.", body_style))
    
    rent_data = [
        [Paragraph("Lease Month Range", table_hdr), Paragraph("Base Rent Rate / RSF / Yr", table_hdr), Paragraph("Annualized Base Rent", table_hdr), Paragraph("Monthly Base Rent", table_hdr)],
        [Paragraph("Months 1 - 6 (Abated)", table_cell), Paragraph("$0.00", table_cell), Paragraph("$0.00", table_cell), Paragraph("$0.00", table_cell)],
        [Paragraph("Months 7 - 60", table_cell), Paragraph("$95.00", table_cell), Paragraph("$4,275,000.00", table_cell), Paragraph("$356,250.00", table_cell)],
        [Paragraph("Months 61 - 120", table_cell), Paragraph("$104.50", table_cell), Paragraph("$4,702,500.00", table_cell), Paragraph("$391,875.00", table_cell)]
    ]
    t1 = Table(rent_data, colWidths=[130, 120, 120, 134])
    t1.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0F172A')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#F8FAFC')])
    ]))
    story.append(t1)
    story.append(Spacer(1, 10))
    
    story.append(Paragraph("SECTION 3: COMMENCEMENT DATE AND LANDLORD DELAY", heading_style))
    story.append(Paragraph("3.1. <b>Commencement Date.</b> The \"Commencement Date\" shall be the date on which Landlord delivers the Premises to Tenant Substantially Completed. The target Commencement Date is September 1, 2026.", body_style))
    story.append(Paragraph("3.2. <b>Landlord Delay Penalties.</b> If Landlord fails to deliver the Premises by October 1, 2026, Tenant shall receive one (1) day of additional Base Rent abatement (to be applied after the initial 6-month abatement period) for each day of delay. If delivery is delayed beyond December 1, 2026, Tenant may terminate this Lease.", body_style))
    
    story.append(Paragraph("SECTION 14: TENANT IMPROVEMENT ALLOWANCE", heading_style))
    story.append(Paragraph("14.1. <b>TI Allowance.</b> Landlord shall provide Tenant with a TI Allowance of $130.00 per RSF, representing a total sum of $5,850,000.00, to be applied toward Tenant's initial alterations.", body_style))
    story.append(Paragraph("14.2. <b>Disbursement.</b> Landlord shall disburse the TI Allowance in progress payments: 50% ($2,925,000.00) upon 50% completion of Tenant's Work, and 50% ($2,925,000.00) upon substantial completion of Tenant's Work and Certificate of Occupancy issuance.", body_style))

    story.append(Paragraph("SECTION 22: TAXES AND OPERATING EXPENSES", heading_style))
    story.append(Paragraph("22.1. <b>Tenant's Proportionate Share.</b> Tenant's Proportionate Share is <b>2.50%</b> (based on 45,000 RSF / 1,800,000 total Building office RSF).", body_style))
    story.append(Paragraph("22.2. <b>Base Year.</b> The Base Year for Taxes and Operating Expenses shall be Calendar Year 2026.", body_style))
    
    # Adding miscellaneous sections to Penn 1 lease to make it rich too
    story.append(Paragraph("SECTION 6: USE AND SUBLEASING", heading_style))
    story.append(Paragraph("6.1. <b>Use.</b> Permitted office and corporate administrative workspace use. Subleasing requires Landlord's consent, not to be unreasonably withheld, delayed or conditioned.", body_style))
    story.append(Paragraph("SECTION 10: NOTICES AND MISCELLANEOUS", heading_style))
    story.append(Paragraph("10.1. Notices via overnight courier. Governing law of the State of New York, County of New York.", body_style))
    
    story.append(Spacer(1, 20))
    story.append(Paragraph("IN WITNESS WHEREOF, Landlord and Tenant have executed this Lease as of the date first written above.", body_style))
    story.append(Spacer(1, 10))
    
    sig_data = [
        [Paragraph("<b>LANDLORD:</b><br/>PENN 1 OWNER LLC<br/>By: Vornado Realty Trust, agent<br/><br/>By: ___________________________<br/>Name: Steven Roth<br/>Title: Chairman & CEO", body_style),
         Paragraph("<b>TENANT:</b><br/>BIOMED DIAGNOSTICS INC.<br/><br/><br/>By: ___________________________<br/>Name: Jane Doe<br/>Title: Chief Operating Officer", body_style)]
    ]
    t_sig = Table(sig_data, colWidths=[252, 252])
    t_sig.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 10)
    ]))
    story.append(t_sig)
    
    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"PDF generated: {pdf_path}")


def build_construction_report_pdf():
    pdf_path = os.path.join(unstructured_dir, "PENN2_Construction_Status_Report.pdf")
    print(f"Generating PDF: {pdf_path}...")
    doc = SimpleDocTemplate(pdf_path, pagesize=letter, leftMargin=54, rightMargin=54, topMargin=72, bottomMargin=72)
    story = []
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'TitleStyle', parent=styles['Heading1'], fontName='Helvetica-Bold', fontSize=18, leading=22, textColor=colors.HexColor('#8B0000'), alignment=1, spaceAfter=15
    )
    subtitle_style = ParagraphStyle(
        'SubTitleStyle', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=10, leading=14, textColor=colors.HexColor('#1E293B'), alignment=1, spaceAfter=20
    )
    heading_style = ParagraphStyle(
        'HeadingStyle', parent=styles['Heading2'], fontName='Helvetica-Bold', fontSize=11, leading=15, textColor=colors.HexColor('#0F172A'), spaceBefore=12, spaceAfter=5, keepWithNext=True
    )
    body_style = ParagraphStyle(
        'BodyStyle', parent=styles['BodyText'], fontName='Helvetica', fontSize=9, leading=13.5, textColor=colors.HexColor('#334155'), spaceAfter=5
    )
    table_hdr = ParagraphStyle(
        'TableHdr', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=8, leading=10, textColor=colors.white
    )
    table_cell = ParagraphStyle(
        'TableCell', parent=styles['Normal'], fontName='Helvetica', fontSize=8, leading=10, textColor=colors.HexColor('#1E293B')
    )

    story.append(Spacer(1, 20))
    story.append(Paragraph("PENN DISTRICT DEVELOPMENT PROJECT STATUS REPORT", title_style))
    story.append(Paragraph("INTERNAL MEMORANDUM - VORNADO REALTY TRUST", subtitle_style))
    story.append(Spacer(1, 10))
    
    meta_data = [
        [Paragraph("<b>TO:</b>", body_style), Paragraph("Executive Committee & Asset Management Division", body_style)],
        [Paragraph("<b>FROM:</b>", body_style), Paragraph("John Vance, Senior Vice President of Development", body_style)],
        [Paragraph("<b>DATE:</b>", body_style), Paragraph("October 15, 2026", body_style)],
        [Paragraph("<b>RE:</b>", body_style), Paragraph("PENN 2 Redevelopment Project Status & Lease Liability Analysis (Apex Fintech)", body_style)]
    ]
    t_meta = Table(meta_data, colWidths=[60, 444])
    t_meta.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LINEBELOW', (0,-1), (-1,-1), 1, colors.HexColor('#CBD5E1'))
    ]))
    story.append(t_meta)
    story.append(Spacer(1, 15))
    
    story.append(Paragraph("1. Executive Summary", heading_style))
    story.append(Paragraph("This report provides an update on the progress of the PENN 2 Redevelopment Project (Two Penn Plaza Modernization) managed by our general contractor, <b>Turner Construction</b>, and evaluates schedule and budget impacts on pending tenancy milestones. Overall project progress is at 88%. While base-building structural renovations, the Seventh Avenue cantilever canopy, and core facade glazing are completed, significant interior fit-out delays and TI cost overruns have emerged. Specifically, the delivery of tenant floors 12 through 18 has been severely delayed due to custom HVAC equipment failures and elevator pit structural reinforcement. This delay triggers landlord liability under the draft lease agreement with Apex Fintech Solutions LLC. Additionally, due to HVAC testing delays and contractor coordination issues, Turner Construction is projecting a <b>$8.00/RSF cost overrun</b> on Tenant Improvement works, increasing the final TI cost to <b>$158.00/RSF</b> against the $150.00/RSF budget.", body_style))
    
    story.append(Paragraph("2. Detailed Construction Progress & Delayed Milestones", heading_style))
    story.append(Paragraph("The critical path of the interior fit-out is constrained by two primary factors:", body_style))
    story.append(Paragraph("<b>(a) Custom HVAC Air Handling Units (AHUs):</b> The custom outdoor AHUs manufactured in Texas failed factory pressure testing in September 2026. Correcting these design defects and re-testing has pushed the shipping date to February 2027, with installation and mechanical connection scheduled for completion in June 2027. Core HVAC services cannot be energized for floors 12-18 until this occurs.", body_style))
    story.append(Paragraph("<b>(b) Elevator Shaft Pit Upgrades:</b> Reinforcements of the elevator pit structural slabs in the mid-rise elevator banks took 6 months longer than scheduled due to bedrock water infiltration. Full elevator service to floors 12-18 is now delayed until May 2027.", body_style))
    
    milestone_data = [
        [Paragraph("Milestone Phase", table_hdr), Paragraph("Original Schedule Date", table_hdr), Paragraph("Projected Actual Date", table_hdr), Paragraph("Variance & Primary Drivers", table_hdr)],
        [Paragraph("Structural Demolition & Demising Walls", table_cell), Paragraph("June 1, 2026", table_cell), Paragraph("June 15, 2026", table_cell), Paragraph("+14 days (Minor labor shortage)", table_cell)],
        [Paragraph("Rough-In Mechanical & Electrical (MEP)", table_cell), Paragraph("October 1, 2026", table_cell), Paragraph("April 1, 2027", table_cell), Paragraph("+182 days (HVAC equipment delay)", table_cell)],
        [Paragraph("Sheetrock & Drywall Close-In", table_cell), Paragraph("December 1, 2026", table_cell), Paragraph("May 30, 2027", table_cell), Paragraph("+180 days (MEP dependency)", table_cell)],
        [Paragraph("Substantial Completion & Delivery Date", table_cell), Paragraph("January 1, 2027", table_cell), Paragraph("July 15, 2027", table_cell), Paragraph("+195 days (HVAC/Elevator critical path)", table_cell)]
    ]
    t_m = Table(milestone_data, colWidths=[140, 100, 100, 164])
    t_m.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0F172A')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#F8FAFC')])
    ]))
    story.append(t_m)
    story.append(Spacer(1, 10))
    
    story.append(Paragraph("3. Lease Liability & Financial Impact Analysis (Apex Fintech)", heading_style))
    story.append(Paragraph("Under the current draft lease for Apex Fintech Solutions LLC (entire 14th & 15th floors, 130,000 RSF), the Landlord's Target Delivery Date is set at <b>June 1, 2027</b>. Because the projected actual Delivery Date is now <b>July 15, 2027</b>, the delay duration stands at forty-four (44) calendar days past the threshold.", body_style))
    story.append(Paragraph("Per Section 3.3 of the Apex lease, the delay triggers the following concession penalties:", body_style))
    story.append(Paragraph("<b>- Initial Delay Penalty (1-for-1):</b> The Rent Commencement Date is deferred by 1 additional day of free rent for each day of delay from June 1, 2027 through July 15, 2027. This results in exactly <b>44 days of additional Base Rent abatement</b>.", body_style))
    story.append(Paragraph("<b>- Total Concession Impact:</b> Original Base Rent abatement of 12 months (365 days) is extended by 44 days, totaling 409 days of rent-free period starting from the actual Commencement Date (July 15, 2027).", body_style))
    story.append(Paragraph("<b>- Cash Flow Inflection Timeline:</b> Rent Commencement shifts from the nominal projected date of January 1, 2028 (assuming on-time delivery on Jan 1, 2027) to <b>August 27, 2028</b> (July 15, 2027 + 409 days free rent, accounting for the 2028 leap year).", body_style))
    story.append(Paragraph("<b>- GAAP vs Cash NOI Impact:</b> While GAAP rental revenue will be recognized straight-line over the term, Cash NOI collection will be delayed by an estimated 239 days relative to the original underwriting model. This creates a Cash NOI deficit of <b>$1,723,835.62</b> for the calendar year 2027/2028 (calculated at 44 days * $39,178.08 per day base rent rate).", body_style))
    
    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"PDF generated: {pdf_path}")


# ---------------------------------------------------------
# Main Execution Block
# ---------------------------------------------------------
if __name__ == "__main__":
    create_csv_files()
    build_apex_lease_pdf()
    build_biomed_lease_pdf()
    build_construction_report_pdf()
    print("\n[SUCCESS] All structured and unstructured test data files generated successfully!")
