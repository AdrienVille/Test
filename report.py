from fpdf import FPDF

def generate_pdf_report(df):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Rapport d'Audit Energétique", ln=1, align="C")
    pdf.cell(200, 10, txt=f"Nombre de mesures : {len(df)}", ln=2)
    pdf.output("rapport_audit.pdf")
