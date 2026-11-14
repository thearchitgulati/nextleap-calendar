#!/usr/bin/env python3
"""Generate events.ics from the EVENTS list below.

Edit EVENTS, then run:  python3 build.py
UIDs are derived from date + time slot, so they stay stable across rebuilds
(changing a title updates the event instead of duplicating it).
"""
from datetime import date, datetime, timedelta, timezone

CAL_NAME = "NextLeap"
IST = timezone(timedelta(hours=5, minutes=30))
SLOTS = {"AM": ((10, 30), (12, 30)), "PM": ((14, 0), (16, 0))}
DASHBOARD = "https://nextleap.app/course-dashboard/nlcfsnyburhb9w7udwabt/overview"


def is_recorded(title):
    # Mentor Labs and Mock Interviews are live-only; everything else is recorded.
    return not title.lower().startswith(("mentor", "mock interview"))


def description(title):
    rec = ("🎥 Recorded: Yes" if is_recorded(title)
           else "🔴 Not recorded (live only)")
    return (f"{rec}\n\n"
            "Joining link: posted on the dashboard 30 mins before the session "
            "(log in to view):\n"
            f"{DASHBOARD}")

# (date, slot, title)
EVENTS = [
    ("2026-11-14", "AM", "Systems Thinking"),
    ("2026-11-14", "PM", "Mapping Business Outcomes to Product Outcomes"),
    ("2026-11-15", "AM", "Mentor Labs - Milestone 1 Guidance"),
    ("2026-11-15", "PM", "Case Hours: KPI Trees"),
    ("2026-11-21", "AM", "Mapping Outcomes to Opportunities"),
    ("2026-11-21", "PM", "Deriving Insights from User Research"),
    ("2026-11-22", "AM", "Mentor Lab - Milestone 1 Feedback"),
    ("2026-11-22", "PM", "Case hours - Segmenting for Scale"),
    ("2026-11-28", "AM", "Problem Framing & Ideation"),
    ("2026-11-28", "PM", "Metrics & Data Analytics"),
    ("2026-11-29", "AM", "Mentor Lab - Milestone 2 Guidance"),
    ("2026-11-29", "PM", "Case Hours: Metrics"),
    ("2026-12-05", "AM", "User Flows & Wireframing"),
    ("2026-12-05", "PM", "UX Design Foundations"),
    ("2026-12-06", "AM", "Mentor Labs - Milestone 2 Feedback"),
    ("2026-12-06", "PM", "Case Hours: Product Sense"),
    ("2026-12-12", "AM", "Product Growth"),
    ("2026-12-12", "PM", "MVP Prototyping with AI"),
    ("2026-12-13", "AM", "Mentor Labs - Milestone 3 Guidance"),
    ("2026-12-19", "AM", "APIs, Webhooks & SDKs"),
    ("2026-12-19", "PM", "AI System Design"),
    ("2026-12-20", "AM", "Mentor Labs - Milestone 3 Feedback"),
    ("2026-12-20", "PM", "Build Hours: Building with APIs"),
    ("2026-12-26", "AM", "LLMs: How they Work"),
    ("2026-12-26", "PM", "Prompt Engineering"),
    ("2026-12-27", "AM", "Build Hours: Building AI prototypes (backend)"),
    ("2026-12-27", "PM", "Build Hours: Building AI prototypes (Frontend)"),
    ("2027-01-02", "AM", "RAG fundamentals & types"),
    ("2027-01-02", "PM", "Advanced RAGs: Graph & Vector RAGs"),
    ("2027-01-03", "AM", "Build Hours: Building a RAG Chatbot"),
    ("2027-01-03", "PM", "Build Hours: Building a RAG Chatbot"),
    ("2027-01-09", "AM", "Context Engineering: Sessions, Memory, Tools"),
    ("2027-01-09", "PM", "AI workflows, Agents & MCP"),
    ("2027-01-10", "AM", "Build Hours: Building linear AI workflows (with n8n)"),
    ("2027-01-10", "PM", "Build Hours: Building Agents (with Zapier)"),
    ("2027-01-16", "AM", "AI Evals"),
    ("2027-01-16", "PM", "How to Test AI Products"),
    ("2027-01-23", "AM", "Interview Preparation - Guesstimates"),
    ("2027-01-23", "PM", "Interview Preparation - RCAs"),
    ("2027-01-24", "AM", "Mock Interviews - RCAs"),
    ("2027-01-24", "PM", "Mock Interviews - Guesstimates"),
    ("2027-01-30", "AM", "Interview Preparation - Product Design"),
    ("2027-01-30", "PM", "Interview Preparation - Metrics"),
    ("2027-01-31", "AM", "Mock Interviews - Product Design"),
    ("2027-01-31", "PM", "Mock Interviews - Metrics"),
]


def esc(text):
    return (text.replace("\\", "\\\\").replace(";", "\\;")
                .replace(",", "\\,").replace("\n", "\\n"))


def fold(line):
    """RFC 5545: lines max 75 octets, continuation lines start with a space."""
    out, raw = [], line.encode("utf-8")
    while len(raw) > 75:
        cut = 75 if not out else 74
        while (raw[cut] & 0xC0) == 0x80:  # don't split a UTF-8 char
            cut -= 1
        out.append(raw[:cut].decode())
        raw = raw[cut:]
    out.append(raw.decode())
    return "\r\n ".join(out)


def utc(d, hm):
    dt = datetime(d.year, d.month, d.day, *hm, tzinfo=IST)
    return dt.astimezone(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def build():
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//nextleap-calendar//EN",
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH",
        f"X-WR-CALNAME:{CAL_NAME}",
        "X-WR-TIMEZONE:Asia/Kolkata",
        "REFRESH-INTERVAL;VALUE=DURATION:PT12H",
        "X-PUBLISHED-TTL:PT12H",
    ]
    for ds, slot, title in EVENTS:
        d = date.fromisoformat(ds)
        start, end = SLOTS[slot]
        lines += [
            "BEGIN:VEVENT",
            f"UID:{ds}-{slot.lower()}@nextleap-calendar",
            f"DTSTAMP:{stamp}",
            f"DTSTART:{utc(d, start)}",
            f"DTEND:{utc(d, end)}",
            f"SUMMARY:{esc(title)}",
            f"DESCRIPTION:{esc(description(title))}",
            f"LOCATION:{esc(DASHBOARD)}",
            f"URL:{DASHBOARD}",
            "STATUS:CONFIRMED",
            "END:VEVENT",
        ]
    lines.append("END:VCALENDAR")
    return "\r\n".join(fold(l) for l in lines) + "\r\n"


if __name__ == "__main__":
    with open("events.ics", "w", newline="") as f:
        f.write(build())
    print(f"Wrote events.ics with {len(EVENTS)} events")
