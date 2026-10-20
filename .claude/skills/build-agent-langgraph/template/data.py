"""Mock data. CUSTOMIZE: replace with records shaped like the customer's domain.
Keep it small: 8-12 articles, 5-8 records. Everything fictional.
"""

# CUSTOMIZE: knowledge articles the agent may cite. IDs must stay unique and real
# ones must all share one prefix so a fabricated ID is easy to spot.
ARTICLES = [
    {"id": "KB-001", "title": "Change your direct deposit account", "tags": ["pay", "direct deposit", "bank"],
     "content": "Go to Payroll > Direct Deposit, add the new account, verify with the micro-deposit, then set it as primary. Changes before Tuesday 5pm apply to Friday's pay."},
    {"id": "KB-002", "title": "Download your W-2 and tax documents", "tags": ["tax", "w-2"],
     "content": "Tax documents are under Payroll > Tax Documents. W-2s post by January 31. Former employees keep read-only access for three years."},
    {"id": "KB-003", "title": "Check your PTO balance and request time off", "tags": ["pto", "time off", "vacation"],
     "content": "Balances are on the Time Off tile. Submit requests at least two business days ahead; your manager approves in the app."},
    {"id": "KB-004", "title": "Fix a missed clock-in or clock-out", "tags": ["timecard", "clock"],
     "content": "Open Time > Timecard, select the day, choose Add Punch, enter the time, and add a note. Your manager approves the correction."},
    {"id": "KB-005", "title": "Update your home address", "tags": ["address", "profile", "tax"],
     "content": "Profile > Personal Info > Address. Tax withholding updates automatically for the new state on the next payroll."},
    {"id": "KB-006", "title": "Open enrollment and benefits changes", "tags": ["benefits", "enrollment", "medical"],
     "content": "Open enrollment runs the first two weeks of November. Outside that window you need a qualifying life event, submitted within 30 days."},
    {"id": "KB-007", "title": "Change your 401(k) contribution", "tags": ["401k", "retirement", "benefits"],
     "content": "Benefits > Retirement. Enter the new percentage; it applies on the next payroll. Employer match caps at 6%."},
    {"id": "KB-008", "title": "Locked out of self-service", "tags": ["login", "password", "locked"],
     "content": "After five failed attempts the account locks for 30 minutes. Use Forgot Password or contact the service desk for a reset."},
]

# CUSTOMIZE: the person's own record, returned by the lookup tool. Fictional.
RECORDS = {
    "E-10001": {"name": "Jordan Lee", "next_pay_date": "2026-10-09", "pto_hours": 46.5, "direct_deposit": "verified", "state": "OK"},
    "E-10002": {"name": "Sam Rivera", "next_pay_date": "2026-10-09", "pto_hours": 12.0, "direct_deposit": "prenote pending", "state": "TX"},
    "E-10003": {"name": "Priya Nair", "next_pay_date": "2026-10-09", "pto_hours": 80.0, "direct_deposit": "verified", "state": "CA"},
}

# CUSTOMIZE: screens and workflows the action tools can open or start.
SCREENS = ["Direct Deposit", "Tax Documents", "Time Off", "Timecard", "Personal Info", "Benefits", "Retirement"]
WORKFLOWS = ["time_off_request", "address_change", "timecard_correction", "beneficiary_change"]

# CUSTOMIZE: only when the brief has `agent.second_source`. Maps an article id to the record from the
# second source that describes the same thing, shaped like an article (id, title, content). The writer sees
# both. The fake article states a fact about the same item that its record does not list, and the record says so.
# Leave empty otherwise.
SOURCE_RECORDS: dict[str, dict] = {}

# Planted fabricated article (FAILURE_MODE=fabricated_citation). Plausible, not real.
FAKE_ARTICLE = {"id": "KB-999", "title": "Instant PTO cash-out and same-day pay advance", "tags": ["pto", "cash", "advance", "pay"],
                "content": "Cash out unused PTO or request a same-day pay advance from Payroll > Instant Pay. Funds arrive within one hour."}
