import datetime
from io import BytesIO

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import HRFlowable, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


def generate_job_report(job, submissions):
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=2 * cm,
        leftMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
    )

    styles = getSampleStyleSheet()
    story = []

    title_style = ParagraphStyle(
        "Title",
        parent=styles["Title"],
        textColor=colors.HexColor("#7C3AED"),
        fontSize=20,
        spaceAfter=12,
    )
    story.append(Paragraph(f"Recruitment Report: {job.title}", title_style))
    story.append(
        Paragraph(
            f"Generated: {datetime.datetime.now().strftime('%B %d, %Y')} | "
            f"Company: {job.company_name or 'N/A'} | "
            f"Total Applicants: {len(submissions)}",
            styles["Normal"],
        )
    )
    story.append(Spacer(1, 0.5 * cm))
    story.append(HRFlowable(width="100%", color=colors.HexColor("#7C3AED"), thickness=1))
    story.append(Spacer(1, 0.5 * cm))

    data = [["Rank", "Candidate", "Email", "Score", "Status", "Applied"]]
    sorted_subs = sorted(submissions, key=lambda s: s.score or 0, reverse=True)
    for i, sub in enumerate(sorted_subs, 1):
        data.append(
            [
                str(i),
                sub.candidate_name or "—",
                sub.email or "—",
                f"{sub.score or 0}/100",
                (sub.status or "pending").replace("_", " ").title(),
                sub.created_at.strftime("%b %d, %Y") if sub.created_at else "—",
            ]
        )

    t = Table(
        data,
        colWidths=[1.2 * cm, 4 * cm, 5 * cm, 2.2 * cm, 2.8 * cm, 2.5 * cm],
    )
    t.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#7C3AED")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, 0), 9),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.HexColor("#F8F8FF"), colors.white]),
                ("FONTSIZE", (0, 1), (-1, -1), 8),
                ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#E2E8F0")),
                ("ALIGN", (3, 0), (3, -1), "CENTER"),
            ]
        )
    )
    story.append(t)

    doc.build(story)
    buffer.seek(0)
    return buffer
