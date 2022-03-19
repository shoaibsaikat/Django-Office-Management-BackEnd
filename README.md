# Django-Office-Management-BackEnd
Office Management System using Django Backend with REST api support using Django REST Framework.
It can be consumed by different front-ends like Angular, React or Vue.js.

Some requirements:
1. pip install django mysqlclient
2. pip install django-cors-headers

For Django REST Framework:
1. pip install djangorestframework

For JWT:
1. pip install djangorestframework-simplejwt

To use Conda-Forge:
1. conda --version
2. conda update conda
3. conda config --add channels conda-forge
4. conda config --set channel_priority strict

Note:
1. To generate spec list file -> conda list --explicit > <file_name>.txt
2. To generate environment.yml file -> conda env export --name <environment_name> > <file_name>.yml
3. to update all packages -> conda update -all

Frontend Project:
1. https://github.com/shoaibsaikat/Angular-Office-Management
Note: django_jwt branch need to be used.