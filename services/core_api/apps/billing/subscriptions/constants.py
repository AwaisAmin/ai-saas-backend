import os
from common.constants import PLAN_LIMITS

PLANS_DATA = [
    {
        "id": "free",
        "name": "Free",
        "price": {"monthly": 0, "yearly": 0},
        "price_ids": {"monthly": None, "yearly": None},
        "limits": PLAN_LIMITS["free"],
        "features": [
            "Up to 5 members",
            "3 projects",
            "10 AI actions/day",
            "Basic boards & tasks",
        ],
    },
    {
        "id": "pro",
        "name": "Pro",
        "price": {"monthly": 35, "yearly": 29},
        "price_ids": {
            "monthly": os.getenv("STRIPE_PRO_MONTHLY_PRICE_ID"),
            "yearly":  os.getenv("STRIPE_PRO_YEARLY_PRICE_ID"),
        },
        "limits": PLAN_LIMITS["pro"],
        "features": [
            "Up to 15 members",
            "Unlimited projects",
            "100 AI actions/day",
            "Roadmaps & analytics",
            "Priority support",
        ],
    },
    {
        "id": "business",
        "name": "Business",
        "price": {"monthly": 99, "yearly": 79},
        "price_ids": {
            "monthly": os.getenv("STRIPE_BUSINESS_MONTHLY_PRICE_ID"),
            "yearly":  os.getenv("STRIPE_BUSINESS_YEARLY_PRICE_ID"),
        },
        "limits": PLAN_LIMITS["business"],
        "features": [
            "Up to 50 members",
            "Unlimited projects",
            "500 AI actions/day",
            "Automations",
            "Advanced analytics",
            "Dedicated support",
        ],
    },
    {
        "id": "enterprise",
        "name": "Enterprise",
        "price": {"monthly": None, "yearly": None},
        "price_ids": {"monthly": None, "yearly": None},
        "limits": PLAN_LIMITS["enterprise"],
        "features": [
            "Unlimited members",
            "Unlimited projects",
            "2000 AI actions/day",
            "SSO & audit logs",
            "Custom integrations",
            "SLA & dedicated account manager",
        ],
    },
]
