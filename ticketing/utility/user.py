from ticketing.models import User, SpecialistDepartment
from ticketing.utility.department import *
from ticketing.utility.model import *
from django import forms


def get_user(id):
    try:
        user = User.objects.get(id=id)
    except User.DoesNotExist:
        return None
    return user


def get_user_by_email(email):
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return None
    return user


def user_exists_by_email(email):
    if get_user_by_email(email):
        return True
    else:
        return False


def get_user_department(user):
    try:
        specialist_department = SpecialistDepartment.objects.get(
            specialist=user
        )

    except SpecialistDepartment.DoesNotExist:
        return None

    return get_department(specialist_department.department.id)


def update_specialist_department(user, old_role, new_role, department):

    if old_role == User.Role.SPECIALIST:
        if new_role != User.Role.SPECIALIST:
            delete_model_object(SpecialistDepartment, specialist=user.id)

        else:
            # We need to update the existing database entry
            specialist_department = get_model_object(
                SpecialistDepartment, specialist=user.id
            )

            if specialist_department != None:
                specialist_department.department = department
                
                specialist_department.save()
            else:
                SpecialistDepartment(specialist=user, department=department).save()


    elif new_role == User.Role.SPECIALIST:
        # We will only get here is old_role is != SPECIALIST and new_role is == SPECIALIST
        SpecialistDepartment(specialist=user, department=department).save()
