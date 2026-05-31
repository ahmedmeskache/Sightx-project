import os
import time
import config

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer,
    Table, TableStyle, Image, HRFlowable, PageBreak
)


ALERT_COLORS = {
    "SPEED": colors.HexColor("#e74c3c"),
    "ZONE": colors.HexColor("#c0392b"),
    "RUNNING": colors.HexColor("#e67e22"),
    "LOITER": colors.HexColor("#f39c12"),
    "AMBER": colors.HexColor("#ff3344"),
    "UNKNOWN": colors.HexColor("#7f8c8d"),
}

ALERT_LABELS = {
    "SPEED": "Speed Violation",
    "ZONE": "Zone Intrusion",
    "RUNNING": "Sudden Running",
    "LOITER": "Loitering",
    "AMBER": "Amber Alert",
    "UNKNOWN": "Unknown",
}


def generate_report(alert_log, outputs_dir=None):
    if outputs_dir is None:
        outputs_dir = config.OUTPUTS_DIR

    os.makedirs(outputs_dir, exist_ok=True)

    timestamp = time.strftime("%Y%m%d_%H%M%S")
    pdf_path = os.path.join(outputs_dir, f"SightX_Report_{timestamp}.pdf")

    document = SimpleDocTemplate(
        pdf_path,
        pagesize=A4,
        rightMargin=2 * cm, leftMargin=2 * cm,
        topMargin=2 * cm, bottomMargin=2 * cm,
    )

    styles = getSampleStyleSheet()
    story = []

    title_style = ParagraphStyle(
        "SightXTitle", parent=styles["Title"],
        fontSize=26, textColor=colors.HexColor("#2c3e50"), spaceAfter=6)

    subtitle_style = ParagraphStyle(
        "SightXSubtitle", parent=styles["Normal"],
        fontSize=11, textColor=colors.HexColor("#7f8c8d"), spaceAfter=4)

    section_style = ParagraphStyle(
        "SightXSection", parent=styles["Heading2"],
        fontSize=13, textColor=colors.HexColor("#2c3e50"),
        spaceBefore=14, spaceAfter=6, borderPad=4)

    body_style = ParagraphStyle(
        "SightXBody", parent=styles["Normal"],
        fontSize=10, textColor=colors.HexColor("#2c3e50"),
        spaceAfter=4, leading=16)

    header_data = [[
        Paragraph("<b>SIGHTX</b>", ParagraphStyle(
            "Header", fontSize=18,
            textColor=colors.white, fontName="Helvetica-Bold")),
        Paragraph("Security Camera System", ParagraphStyle(
            "HeaderSub", fontSize=10, textColor=colors.HexColor("#bdc3c7")))
    ]]
    header_table = Table(header_data, colWidths=[8 * cm, 9 * cm])
    header_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#2c3e50")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 16),
        ("TOPPADDING", (0, 0), (-1, -1), 14),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 14),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 0.5 * cm))

    story.append(Paragraph("Incident Report", title_style))
    story.append(Paragraph(
        f"Generated: {time.strftime('%A, %B %d, %Y at %H:%M:%S')}",
        subtitle_style))
    story.append(HRFlowable(
        width="100%", thickness=1,
        color=colors.HexColor("#bdc3c7"), spaceAfter=12))

    story.append(Paragraph("Session Summary", section_style))

    total = len(alert_log)
    speed_count = sum(1 for a in alert_log if a["type"] == "SPEED")
    zone_count = sum(1 for a in alert_log if a["type"] == "ZONE")
    running_count = sum(1 for a in alert_log if a["type"] == "RUNNING")
    loiter_count = sum(1 for a in alert_log if a["type"] == "LOITER")
    amber_count = sum(1 for a in alert_log if a["type"] == "AMBER")

    summary_data = [
        ["Metric", "Value"],
        ["Total Alerts", str(total)],
        ["Speed Violations", str(speed_count)],
        ["Zone Intrusions", str(zone_count)],
        ["Running Detections", str(running_count)],
        ["Loitering Alerts", str(loiter_count)],
        ["Amber Alerts", str(amber_count)],
        ["Report Generated", time.strftime("%Y-%m-%d %H:%M:%S")],
    ]
    summary_table = Table(summary_data, colWidths=[9 * cm, 8 * cm])
    summary_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2c3e50")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#ecf0f1")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#ecf0f1")]),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#bdc3c7")),
        ("LEFTPADDING", (0, 0), (-1, -1), 12),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    story.append(summary_table)
    story.append(Spacer(1, 0.5 * cm))

    story.append(Paragraph("Alert Breakdown", section_style))
    story.append(Paragraph("The following alert types were recorded during this session:", body_style))

    breakdown_data = [["Type", "Count", "Severity"]]
    for atype, count, severity in [
        ("SPEED", speed_count, "High"),
        ("ZONE", zone_count, "High"),
        ("RUNNING", running_count, "Medium"),
        ("LOITER", loiter_count, "Low"),
        ("AMBER", amber_count, "Critical"),
    ]:
        breakdown_data.append([ALERT_LABELS.get(atype, atype), str(count), severity])

    breakdown_table = Table(breakdown_data, colWidths=[7 * cm, 4 * cm, 6 * cm])
    breakdown_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#34495e")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#ecf0f1")]),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#bdc3c7")),
        ("LEFTPADDING", (0, 0), (-1, -1), 12),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    story.append(breakdown_table)

    if alert_log:
        story.append(PageBreak())
        story.append(Paragraph("Incident Details", section_style))
        story.append(Paragraph(
            "Each alert below includes a timestamp, description, offender snapshot, and evidence where available.",
            body_style))
        story.append(Spacer(1, 0.3 * cm))

        for index, entry in enumerate(alert_log):
            atype = entry.get("type", "UNKNOWN")
            track_id = entry.get("track_id", "?")
            details = entry.get("details", "")
            event_time = entry.get("time", "")
            color = ALERT_COLORS.get(atype, colors.grey)
            label = ALERT_LABELS.get(atype, atype)

            alert_header = Table([[
                Paragraph(f"<b>#{index+1} — {label}</b>", ParagraphStyle(
                    "AH", fontSize=11, textColor=colors.white,
                    fontName="Helvetica-Bold")),
                Paragraph(f"ID {track_id}  |  {event_time}", ParagraphStyle(
                    "AHS", fontSize=9, textColor=colors.HexColor("#ecf0f1")))
            ]], colWidths=[10 * cm, 7 * cm])
            alert_header.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, -1), color),
                ("LEFTPADDING", (0, 0), (-1, -1), 10),
                ("TOPPADDING", (0, 0), (-1, -1), 8),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ]))
            story.append(alert_header)

            detail_table = Table([
                ["Object ID", f"Tracked Object #{track_id}"],
                ["Alert Type", label],
                ["Details", details],
                ["Time", event_time],
            ], colWidths=[4 * cm, 13 * cm])
            detail_table.setStyle(TableStyle([
                ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("TEXTCOLOR", (0, 0), (0, -1), colors.HexColor("#7f8c8d")),
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f8f9fa")),
                ("GRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#dee2e6")),
                ("LEFTPADDING", (0, 0), (-1, -1), 10),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ]))
            story.append(detail_table)

            crop_path = find_crop_snapshot(outputs_dir, atype, track_id)
            if crop_path and os.path.exists(crop_path):
                story.append(Spacer(1, 0.2 * cm))
                try:
                    img = Image(crop_path, width=8 * cm, height=8 * cm)
                    img.hAlign = "CENTER"
                    story.append(img)
                    story.append(Paragraph(
                        f"<b>OFFENDER IDENTIFIED</b> — Track ID {track_id}",
                        ParagraphStyle("Cap", fontSize=9,
                                       textColor=colors.HexColor("#c0392b"),
                                       alignment=1, spaceAfter=4)))
                except Exception as e:
                    story.append(Paragraph(f"[Snapshot unavailable: {e}]", body_style))
            else:
                story.append(Paragraph("No offender snapshot available.", body_style))

            snapshot_path = find_snapshot(outputs_dir, atype, track_id)
            if snapshot_path and os.path.exists(snapshot_path):
                story.append(Spacer(1, 0.2 * cm))
                try:
                    img = Image(snapshot_path, width=15 * cm, height=9 * cm)
                    img.hAlign = "CENTER"
                    story.append(img)
                    story.append(Paragraph(
                        f"Full scene evidence: {os.path.basename(snapshot_path)}",
                        ParagraphStyle("Cap", fontSize=8,
                                       textColor=colors.HexColor("#7f8c8d"),
                                       alignment=1)))
                except Exception as e:
                    story.append(Paragraph(f"[Snapshot unavailable: {e}]", body_style))

            story.append(Spacer(1, 0.5 * cm))
            story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#dee2e6"), spaceAfter=8))

    story.append(PageBreak())
    story.append(Spacer(1, 3 * cm))
    story.append(Paragraph("End of Report", title_style))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#bdc3c7"), spaceAfter=12))
    story.append(Paragraph(
        f"This report was automatically generated by SightX v1.0 on {time.strftime('%Y-%m-%d at %H:%M:%S')}. Total incidents recorded: {len(alert_log)}.",
        body_style))
    story.append(Spacer(1, 0.5 * cm))
    story.append(Paragraph(
        "SightX — Security Camera System | Built with Python, YOLOv8, OpenCV",
        ParagraphStyle("Footer", fontSize=8, textColor=colors.HexColor("#7f8c8d"))))

    try:
        document.build(story)
        print(f"[REPORT] PDF saved: {pdf_path}")
        return pdf_path
    except Exception as e:
        print(f"[ERROR] Failed to generate PDF report: {e}")
        return None


def find_snapshot(outputs_dir, alert_type, track_id):
    try:
        matches = [
            f for f in os.listdir(outputs_dir)
            if f.startswith(f"{alert_type}_ID{track_id}_")
            and f.endswith(".jpg")
            and not f.endswith("_CROP.jpg")
        ]
        if not matches:
            return None
        matches.sort(reverse=True)
        return os.path.join(outputs_dir, matches[0])
    except Exception:
        return None


def find_crop_snapshot(outputs_dir, alert_type, track_id):
    try:
        matches = [
            f for f in os.listdir(outputs_dir)
            if f.startswith(f"{alert_type}_ID{track_id}_")
            and f.endswith("_CROP.jpg")
        ]
        if not matches:
            return None
        matches.sort(reverse=True)
        return os.path.join(outputs_dir, matches[0])
    except Exception:
        return None