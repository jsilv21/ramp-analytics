from __future__ import annotations

import argparse
import datetime as dt
import random
import re
from pathlib import Path

import numpy as np
import pandas as pd
from faker import Faker

APP_CATALOG = [
    {
        "app_key": "google_workspace",
        "app_name": "Google Workspace",
        "category": "Productivity",
        "vendor": "Google",
        "base_price": 18.0,
        "core": True,
        "target_departments": [],
    },
    {
        "app_key": "microsoft_365",
        "app_name": "Microsoft 365",
        "category": "Productivity",
        "vendor": "Microsoft",
        "base_price": 20.0,
        "core": True,
        "target_departments": [],
    },
    {
        "app_key": "slack",
        "app_name": "Slack",
        "category": "Collaboration",
        "vendor": "Slack",
        "base_price": 12.0,
        "core": True,
        "target_departments": [],
    },
    {
        "app_key": "zoom",
        "app_name": "Zoom",
        "category": "Video",
        "vendor": "Zoom",
        "base_price": 15.0,
        "core": True,
        "target_departments": [],
    },
    {
        "app_key": "okta",
        "app_name": "Okta",
        "category": "Security",
        "vendor": "Okta",
        "base_price": 8.0,
        "core": True,
        "target_departments": ["IT", "Security"],
    },
    {
        "app_key": "jira",
        "app_name": "Jira",
        "category": "Engineering",
        "vendor": "Atlassian",
        "base_price": 10.0,
        "core": False,
        "target_departments": ["Engineering", "Product"],
    },
    {
        "app_key": "confluence",
        "app_name": "Confluence",
        "category": "Engineering",
        "vendor": "Atlassian",
        "base_price": 8.0,
        "core": False,
        "target_departments": ["Engineering", "Product"],
    },
    {
        "app_key": "github",
        "app_name": "GitHub",
        "category": "Engineering",
        "vendor": "GitHub",
        "base_price": 21.0,
        "core": False,
        "target_departments": ["Engineering"],
    },
    {
        "app_key": "figma",
        "app_name": "Figma",
        "category": "Design",
        "vendor": "Figma",
        "base_price": 15.0,
        "core": False,
        "target_departments": ["Design", "Product", "Marketing"],
    },
    {
        "app_key": "salesforce",
        "app_name": "Salesforce",
        "category": "Sales",
        "vendor": "Salesforce",
        "base_price": 150.0,
        "core": False,
        "target_departments": ["Sales"],
    },
    {
        "app_key": "hubspot",
        "app_name": "HubSpot",
        "category": "Marketing",
        "vendor": "HubSpot",
        "base_price": 45.0,
        "core": False,
        "target_departments": ["Marketing", "Sales"],
    },
    {
        "app_key": "zendesk",
        "app_name": "Zendesk",
        "category": "Support",
        "vendor": "Zendesk",
        "base_price": 59.0,
        "core": False,
        "target_departments": ["Customer Success", "Support"],
    },
    {
        "app_key": "asana",
        "app_name": "Asana",
        "category": "Project Management",
        "vendor": "Asana",
        "base_price": 13.0,
        "core": False,
        "target_departments": ["Product", "Operations", "Marketing"],
    },
    {
        "app_key": "notion",
        "app_name": "Notion",
        "category": "Productivity",
        "vendor": "Notion",
        "base_price": 10.0,
        "core": False,
        "target_departments": ["Product", "Engineering", "Marketing"],
    },
    {
        "app_key": "docusign",
        "app_name": "DocuSign",
        "category": "Legal",
        "vendor": "DocuSign",
        "base_price": 25.0,
        "core": False,
        "target_departments": ["Legal", "Sales", "Finance"],
    },
    {
        "app_key": "datadog",
        "app_name": "Datadog",
        "category": "Engineering",
        "vendor": "Datadog",
        "base_price": 25.0,
        "core": False,
        "target_departments": ["Engineering", "IT"],
    },
    {
        "app_key": "tableau",
        "app_name": "Tableau",
        "category": "BI",
        "vendor": "Tableau",
        "base_price": 70.0,
        "core": False,
        "target_departments": ["Finance", "Analytics"],
    },
]

DEPARTMENTS = [
    "Engineering",
    "Product",
    "Sales",
    "Marketing",
    "Finance",
    "HR",
    "IT",
    "Operations",
    "Customer Success",
    "Support",
    "Legal",
    "Design",
    "Analytics",
    "Security",
]

INDUSTRIES = [
    "Fintech",
    "Healthcare",
    "Retail",
    "SaaS",
    "Manufacturing",
    "Logistics",
    "Media",
    "Education",
    "Energy",
    "Real Estate",
]

REGIONS = ["North America", "Europe", "APAC", "LATAM"]

DEVICES = ["macOS", "Windows", "Linux", "iOS", "Android"]

ACTIVITY_TYPES = {
    "Collaboration": ["message", "channel_view", "file_share"],
    "Video": ["meeting_join", "call_start", "screen_share"],
    "Engineering": ["commit", "issue_update", "build"],
    "Design": ["file_edit", "comment", "prototype_view"],
    "Sales": ["lead_update", "opportunity_view", "call_log"],
    "Marketing": ["campaign_edit", "email_send", "report_view"],
    "Support": ["ticket_update", "ticket_view", "macro_apply"],
    "Project Management": ["task_update", "project_view", "comment"],
    "BI": ["dashboard_view", "query_run", "export"],
    "Legal": ["document_sign", "envelope_send", "template_view"],
    "Productivity": ["doc_edit", "calendar_view", "drive_access"],
    "Security": ["policy_update", "login_audit", "app_assign"],
}


def slugify(value: str) -> str:
    cleaned = re.sub(r"[^a-z0-9]+", "", value.lower())
    return cleaned[:15] if cleaned else "org"


def employee_band(employee_count: int) -> str:
    if employee_count < 100:
        return "1-99"
    if employee_count < 250:
        return "100-249"
    if employee_count < 500:
        return "250-499"
    if employee_count < 1000:
        return "500-999"
    return "1000+"


def random_datetime(rng: random.Random, start: dt.datetime, end: dt.datetime) -> dt.datetime:
    if start >= end:
        return start
    delta = end - start
    seconds = rng.randint(0, int(delta.total_seconds()))
    return start + dt.timedelta(seconds=seconds)


def choose_apps_for_org(rng: random.Random) -> list[dict]:
    catalog_by_key = {app["app_key"]: app for app in APP_CATALOG}
    suite_key = rng.choice(["google_workspace", "microsoft_365"])
    core_keys = ["slack", "okta", "zoom", suite_key]
    optional_keys = [
        app["app_key"]
        for app in APP_CATALOG
        if app["app_key"] not in core_keys
        and app["app_key"] not in {"google_workspace", "microsoft_365"}
    ]
    optional_count = rng.randint(6, 9)
    selected_optional = rng.sample(optional_keys, k=min(optional_count, len(optional_keys)))
    selected_keys = core_keys + selected_optional
    return [catalog_by_key[key] for key in selected_keys]


def adoption_rate(app: dict, department: str, rng: random.Random) -> float:
    if app["core"]:
        return rng.uniform(0.8, 0.95)
    if department in app["target_departments"]:
        return rng.uniform(0.45, 0.7)
    return rng.uniform(0.1, 0.3)


def usage_probability(app: dict, department: str, rng: random.Random) -> float:
    if app["core"]:
        return rng.uniform(0.7, 0.9)
    if department in app["target_departments"]:
        return rng.uniform(0.4, 0.7)
    return rng.uniform(0.15, 0.35)


def generate_data(
    out_dir: Path,
    seed: int,
    orgs: int,
    min_employees: int,
    max_employees: int,
    months: int,
) -> None:
    rng = random.Random(seed)
    np_rng = np.random.default_rng(seed)
    faker = Faker()
    faker.seed_instance(seed)

    today = dt.datetime.utcnow().replace(microsecond=0)

    org_rows: list[dict] = []
    user_rows: list[dict] = []
    group_rows: list[dict] = []
    app_rows: list[dict] = []
    assignment_rows: list[dict] = []
    login_rows: list[dict] = []
    usage_rows: list[dict] = []
    contract_rows: list[dict] = []
    invoice_rows: list[dict] = []

    for org_index in range(orgs):
        org_id = f"org_{org_index:03d}"
        org_name = faker.company()
        industry = rng.choice(INDUSTRIES)
        region = rng.choice(REGIONS)
        employee_count = int(
            np.clip(
                np_rng.lognormal(mean=5.5, sigma=0.45),
                min_employees,
                max_employees,
            )
        )
        org_created_at = random_datetime(
            rng, today - dt.timedelta(days=365 * 5), today - dt.timedelta(days=30)
        )
        org_rows.append(
            {
                "org_id": org_id,
                "org_name": org_name,
                "industry": industry,
                "employee_count": employee_count,
                "employee_band": employee_band(employee_count),
                "region": region,
                "created_at": org_created_at.isoformat(),
            }
        )

        domain = slugify(org_name)
        department_weights = np.array(
            [0.22, 0.1, 0.14, 0.1, 0.08, 0.05, 0.07, 0.06, 0.06, 0.04, 0.03, 0.03, 0.01, 0.01]
        )
        department_weights = department_weights / department_weights.sum()

        admin_user_ids: list[str] = []
        user_activity: dict[str, str] = {}

        for user_index in range(employee_count):
            user_id = f"{org_id}_user_{user_index:04d}"
            first_name = faker.first_name()
            last_name = faker.last_name()
            email = f"{first_name}.{last_name}@{domain}.com".lower()
            department = rng.choices(DEPARTMENTS, weights=department_weights, k=1)[0]
            status = rng.choices(
                ["active", "suspended", "deprovisioned"], weights=[0.85, 0.1, 0.05], k=1
            )[0]
            if status == "deprovisioned":
                activity_level = "inactive"
            elif status == "suspended":
                activity_level = rng.choices(["dormant", "inactive"], weights=[0.6, 0.4], k=1)[0]
            else:
                activity_level = rng.choices(
                    ["active", "dormant", "inactive"], weights=[0.7, 0.2, 0.1], k=1
                )[0]

            created_at = random_datetime(rng, org_created_at, today - dt.timedelta(days=7))
            if activity_level == "active":
                last_login_at = random_datetime(rng, today - dt.timedelta(days=30), today)
            elif activity_level == "dormant":
                last_login_at = random_datetime(rng, today - dt.timedelta(days=90), today - dt.timedelta(days=31))
            else:
                if rng.random() < 0.15:
                    last_login_at = None
                else:
                    last_login_at = random_datetime(
                        rng, today - dt.timedelta(days=365), today - dt.timedelta(days=91)
                    )

            is_admin = rng.random() < 0.05
            if is_admin:
                admin_user_ids.append(user_id)

            user_activity[user_id] = activity_level
            user_rows.append(
                {
                    "org_id": org_id,
                    "user_id": user_id,
                    "first_name": first_name,
                    "last_name": last_name,
                    "email": email,
                    "department": department,
                    "title": faker.job(),
                    "status": status,
                    "is_admin": is_admin,
                    "created_at": created_at.isoformat(),
                    "last_login_at": last_login_at.isoformat() if last_login_at else None,
                }
            )

        for dept in DEPARTMENTS:
            group_rows.append(
                {
                    "org_id": org_id,
                    "group_id": f"{org_id}_group_{slugify(dept)}",
                    "group_name": f"{dept} Team",
                    "department": dept,
                }
            )

        selected_apps = choose_apps_for_org(rng)
        org_app_records: list[dict] = []
        for app in selected_apps:
            app_id = f"{org_id}_app_{app['app_key']}"
            enabled_at = random_datetime(rng, org_created_at, today - dt.timedelta(days=15))
            app_record = {
                "org_id": org_id,
                "app_id": app_id,
                "app_key": app["app_key"],
                "app_name": app["app_name"],
                "category": app["category"],
                "vendor": app["vendor"],
                "enabled_at": enabled_at.isoformat(),
                "base_price": app["base_price"],
                "core_app": app["core"],
            }
            app_rows.append(app_record)
            org_app_records.append(app_record)

        admins = admin_user_ids or ["system"]
        user_lookup = [row for row in user_rows if row["org_id"] == org_id]

        for user in user_lookup:
            dept = user["department"]
            activity_level = user_activity[user["user_id"]]
            last_login_at = (
                dt.datetime.fromisoformat(user["last_login_at"])
                if user["last_login_at"]
                else None
            )

            for app in org_app_records:
                rate = adoption_rate(app, dept, rng)
                if rng.random() > rate:
                    continue

                assigned_at = random_datetime(
                    rng, dt.datetime.fromisoformat(user["created_at"]), today - dt.timedelta(days=1)
                )
                assignment_rows.append(
                    {
                        "org_id": org_id,
                        "assignment_id": f"{user['user_id']}_{app['app_id']}",
                        "user_id": user["user_id"],
                        "app_id": app["app_id"],
                        "assigned_at": assigned_at.isoformat(),
                        "assigned_by": rng.choice(admins),
                    }
                )

                if not last_login_at:
                    continue
                if last_login_at < today - dt.timedelta(days=90):
                    continue

                if activity_level == "active":
                    login_count = rng.randint(6, 20)
                elif activity_level == "dormant":
                    login_count = rng.randint(1, 3)
                else:
                    login_count = 0

                if login_count == 0:
                    continue
                if rng.random() > usage_probability(app, dept, rng):
                    continue

                window_start = max(last_login_at - dt.timedelta(days=30), today - dt.timedelta(days=90))
                for login_index in range(login_count):
                    login_ts = random_datetime(rng, window_start, last_login_at)
                    login_rows.append(
                        {
                            "org_id": org_id,
                            "login_id": f"{user['user_id']}_{app['app_id']}_{login_index}",
                            "user_id": user["user_id"],
                            "app_id": app["app_id"],
                            "login_ts": login_ts.isoformat(),
                            "device": rng.choice(DEVICES),
                            "ip_address": faker.ipv4(),
                        }
                    )
                    if rng.random() < 0.7:
                        activity_choices = ACTIVITY_TYPES.get(app["category"], ["activity"])
                        usage_rows.append(
                            {
                                "org_id": org_id,
                                "usage_id": f"{user['user_id']}_{app['app_id']}_{login_index}",
                                "user_id": user["user_id"],
                                "app_id": app["app_id"],
                                "activity_ts": (login_ts + dt.timedelta(minutes=rng.randint(1, 90))).isoformat(),
                                "activity_type": rng.choice(activity_choices),
                                "duration_minutes": rng.randint(5, 180),
                            }
                        )

        assignment_df = pd.DataFrame(assignment_rows)
        if assignment_df.empty:
            continue
        assigned_counts = (
            assignment_df[assignment_df["org_id"] == org_id]
            .groupby("app_id")["user_id"]
            .nunique()
            .to_dict()
        )

        for app in org_app_records:
            assigned_seats = assigned_counts.get(app["app_id"], 0)
            if assigned_seats == 0:
                continue

            term_months = 12
            start_date = today - dt.timedelta(days=rng.randint(365, 365 * 2))
            end_date = start_date + dt.timedelta(days=30 * term_months)
            size_discount = 0.9 if employee_count >= 1000 else 1.0
            price_per_seat = round(app["base_price"] * rng.uniform(0.85, 1.15) * size_discount, 2)
            buffer = max(1, int(assigned_seats * rng.uniform(0.05, 0.25)))
            min_seats = assigned_seats + buffer

            contract_id = f"{org_id}_{app['app_id']}_contract"
            contract_rows.append(
                {
                    "org_id": org_id,
                    "contract_id": contract_id,
                    "app_id": app["app_id"],
                    "app_key": app["app_key"],
                    "start_date": start_date.date().isoformat(),
                    "end_date": end_date.date().isoformat(),
                    "term_months": term_months,
                    "price_per_seat": price_per_seat,
                    "min_seats": min_seats,
                    "billing_frequency": "monthly",
                    "currency": "USD",
                }
            )

            for month_index in range(months):
                invoice_date = (today - dt.timedelta(days=30 * month_index)).date().replace(day=1)
                seats_billed = max(
                    min_seats,
                    int(assigned_seats * rng.uniform(0.95, 1.1)),
                )
                total_amount = round(seats_billed * price_per_seat, 2)
                invoice_rows.append(
                    {
                        "org_id": org_id,
                        "invoice_id": f"{org_id}_{app['app_id']}_{invoice_date.isoformat()}",
                        "contract_id": contract_id,
                        "app_id": app["app_id"],
                        "invoice_date": invoice_date.isoformat(),
                        "seats_billed": seats_billed,
                        "total_amount": total_amount,
                        "currency": "USD",
                    }
                )

    out_dir.mkdir(parents=True, exist_ok=True)

    pd.DataFrame(org_rows).to_csv(out_dir / "raw_orgs.csv", index=False)
    pd.DataFrame(user_rows).to_csv(out_dir / "raw_okta_users.csv", index=False)
    pd.DataFrame(group_rows).to_csv(out_dir / "raw_okta_groups.csv", index=False)
    pd.DataFrame(app_rows).to_csv(out_dir / "raw_okta_apps.csv", index=False)
    pd.DataFrame(assignment_rows).to_csv(out_dir / "raw_okta_assignments.csv", index=False)
    pd.DataFrame(login_rows).to_csv(out_dir / "raw_okta_logins.csv", index=False)
    pd.DataFrame(usage_rows).to_csv(out_dir / "raw_saas_usage.csv", index=False)
    pd.DataFrame(contract_rows).to_csv(out_dir / "raw_saas_contracts.csv", index=False)
    pd.DataFrame(invoice_rows).to_csv(out_dir / "raw_saas_invoices.csv", index=False)


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate synthetic Okta + SaaS spend data.")
    parser.add_argument("--out-dir", type=Path, default=Path("data/raw"))
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--orgs", type=int, default=12)
    parser.add_argument("--min-employees", type=int, default=120)
    parser.add_argument("--max-employees", type=int, default=800)
    parser.add_argument("--months", type=int, default=12)
    args = parser.parse_args()

    generate_data(
        out_dir=args.out_dir,
        seed=args.seed,
        orgs=args.orgs,
        min_employees=args.min_employees,
        max_employees=args.max_employees,
        months=args.months,
    )


if __name__ == "__main__":
    main()
