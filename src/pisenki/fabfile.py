from fabric import api

def prepare_deployment():
    api.local('python manage.py test pisenki')