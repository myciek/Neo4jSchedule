from data.db_session import db_auth
from .accounts_service import get_teachers_names
from .classes import FrequencyEnum

from .lessons_types_services import get_lesson_type_names
from .studies_types_services import get_studies_type_names

graph = db_auth()





def get_lesson_initial_info() -> dict:
    info = {
        "lesson_types": get_lesson_type_names(),
        "teachers": get_teachers_names(),
        "frequency": FrequencyEnum._member_names_,
        "studies_types": get_studies_type_names()
    }
    return info
