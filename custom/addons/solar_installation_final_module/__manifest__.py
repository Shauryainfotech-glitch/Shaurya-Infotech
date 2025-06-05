{
    'name': "Solar Installation Management",
    'version': "1.0.0",
    'summary': "Manage solar projects end-to-end: surveys, quoting, scheduling, BOM, teams, products.",
    'description': """
    Solar Installation Management Module
    ====================================
    This module provides:
      - Project tracking from inquiry through completion.
      - Site surveys with recommendations.
      - Product catalog (panels, inverters, batteries, etc.).
      - Quote/proposal generation with line items and totals.
      - BOM (product lines) per project, including cost computations.
      - Installation teams with skills and workload tracking.
      - Scheduling shifts for installation phases.
      - Sequences and security rules.
    """,
    'author': "YourCompany",
    'website': "https://www.yourcompany.example",
    'category': "Services/Solar",
    'license': "LGPL-3",
    'application': True,
    'installable': True,
    'auto_install': False,
    'depends': [
        'base',
        'mail',
        'uom',
        'hr',
        'stock',
        'product'
    ],
    'data': [
        'data/ir_sequence_data.xml',  # Ensure this path is correct
        'security/solar_security.xml',
        'security/ir.model.access.csv',
        'views/solar_install_skill_views.xml',
        'views/solar_product_views.xml',
        'views/solar_project_views.xml',
        'views/solar_quote_views.xml',
        'views/solar_install_schedule_views.xml',
        'views/solar_site_survey_views.xml',
        'views/solar_install_menu.xml',
    ],
}
