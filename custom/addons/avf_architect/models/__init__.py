
# -*- coding: utf-8 -*-

# Base models first
from . import res_company

# Core business models
from . import architect_project
from . import dpr_management
from . import compliance_tracking
from . import rate_schedule
from . import drawing_management
from . import survey_management
from . import ai_assistant
from . import project_stages
from . import team_collaboration
from . import client_portal
from . import document_management
from . import document_attachment
from . import financial_tracking

# Partners should be imported last to avoid circular dependencies
from . import res_partner
