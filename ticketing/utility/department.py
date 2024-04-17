from ticketing.models.departments import Department


def get_department(id):
    try:
        department = Department.objects.get(id=id)
    except Department.DoesNotExist:
        return None
    return department
