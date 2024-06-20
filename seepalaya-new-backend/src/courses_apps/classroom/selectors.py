from courses_apps.classroom.models import ClassRoom
from django.core.exceptions import ValidationError as DjangoValidationError
from django.utils.translation import gettext as _
from django.db.models import F, Count
from courses_apps.teacher.selectors import teacher_get_from_user
from django.contrib.auth import get_user_model

User = get_user_model()

def get_classroom_from_code(*, class_code: str) -> ClassRoom:
    """
    Returns a classroom object from the given class_code.
    """
    try:
        classroom = ClassRoom.objects.get(class_code=class_code)
    except ClassRoom.DoesNotExist:
        classroom = None
    return classroom

def get_class_room_name_from_class_code(class_code: str) -> str:
    """
    Returns the name of a class room from the given class code.
    """
    classroom = get_classroom_from_code(class_code=class_code)
    if classroom is None:
        raise DjangoValidationError(_("Classroom does not exist."))
    return classroom.title

# def get_classroom_students(*, class_code: str) -> list:
#     """
#     Returns a list of students associated with a given class_code.
#     """
#     classroom = get_classroom_from_code(class_code=class_code)
#     if classroom is None:
#         raise DjangoValidationError(_("Classroom does not exist."))
#     return classroom.students.all()


def get_classroom_students(*, class_code: str, search_query: str = '', sort_order: str = 'asc', teacher_user: User) -> list:
    """
    Returns a list of students associated with a given class_code,
    optionally filtered by search_query and sorted by full_name.
    """
    classroom = get_classroom_from_code(class_code=class_code)
    if classroom is None:
        raise DjangoValidationError(_("Classroom does not exist."))
    
    teacher = teacher_get_from_user(user=teacher_user)
    if classroom.teacher != teacher:
        raise DjangoValidationError(_("Teacher is not the owner of the classroom."))

    students = classroom.students.all()

    if search_query:
        students = students.filter(full_name__icontains=search_query)

    # Apply sorting
    if sort_order == 'asc':
        students = students.order_by('full_name')
    else:
        students = students.order_by('-full_name')

    return students

def get_classroom_details(*, class_code: str, teacher_user: User) -> dict:
    """
    Returns a dictionary containing the details of a classroom.
    """
    teacher = teacher_get_from_user(user=teacher_user)
    if not teacher:
        raise DjangoValidationError(_("Teacher does not exist."))

    classroom = get_classroom_from_code(class_code=class_code)
    if classroom is None:
        raise DjangoValidationError(_("Classroom does not exist."))
    
    if classroom.teacher != teacher:
        raise DjangoValidationError(_("Teacher is not the owner of the classroom."))

    student_count = classroom.students.count()

    return {
        "title": classroom.title,
        "class_code": classroom.class_code,
        "student_count": student_count,
    }
