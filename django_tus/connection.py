from django.db import connection


def get_schema_name():
    # Database shchema connection
    try:
        tenant = connection.get_tenant()
        return tenant.schema_name
    except AttributeError:
        return 'public'
