"""main URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin
from graphene_django.views import GraphQLView
from tastypie.api import Api
from api.resources import (
    DisasterTypeResource,
    EventResource,
    ContactResource,
    CountryResource,
    ActionResource,
    ActionsTakenResource,
    FieldReportResource,
    UserResource,
    ProfileResource,
)
from api.views import get_auth_token, es_keyword_search

v1_api = Api(api_name='v1')
v1_api.register(DisasterTypeResource())
v1_api.register(ContactResource())
v1_api.register(EventResource())
v1_api.register(CountryResource())
v1_api.register(ActionResource())
v1_api.register(ActionsTakenResource())
v1_api.register(FieldReportResource())
v1_api.register(UserResource())
v1_api.register(ProfileResource())

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^api/', include(v1_api.urls)),
    url(r'^api/v1/es_search/', es_keyword_search.as_view()),
    url(r'^api/v1/graphql/', GraphQLView.as_view(graphiql=True)),
    url(r'^get_auth_token', get_auth_token),
]
