from django.db import connection


def get_schema_name():
    # Database shchema connection
    tenant = connection.get_tenant()
    return tenant.schema_name
