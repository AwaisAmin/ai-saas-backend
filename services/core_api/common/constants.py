OWNER  = 'owner'
ADMIN  = 'admin'
MEMBER = 'member'
VIEWER = 'viewer'

ADMIN_ROLES = [OWNER, ADMIN]
WRITE_ROLES = [OWNER, ADMIN, MEMBER]

PLAN_LIMITS = {
    'free':       {'max_members': 5,    'max_projects': 3,    'max_ai_calls_per_day': 10},
    'pro':        {'max_members': 15,   'max_projects': None, 'max_ai_calls_per_day': 100},
    'business':   {'max_members': 50,   'max_projects': None, 'max_ai_calls_per_day': 500},
    'enterprise': {'max_members': None, 'max_projects': None, 'max_ai_calls_per_day': 2000},
}

TEMPLATE_COLUMNS = {
    'product_sprint':     ['Backlog', 'Todo', 'In Progress', 'In Review', 'Done'],
    'marketing_campaign': ['Ideas', 'Brief', 'In Progress', 'Review', 'Published'],
    'design_agency':      ['Research', 'Design', 'Review', 'Client Review', 'Delivered'],
    'blank':              ['To Do', 'In Progress', 'Done'],
}
