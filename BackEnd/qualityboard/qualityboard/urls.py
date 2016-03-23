from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns
from testboard import views


urlpatterns = [
    url(r'^test/$', views.test_all),
    url(r'^test/(?P<target>.*)$', views.test_list),
    url(r'^test_detail/(?P<key>.*)$', views.test_detail),
    url(r'^person/$', views.person_all),
    url(r'^fixversion/$', views.fix_version_all),
    url(r'^fixversion/(?P<tribe>.*)$', views.fix_version_tribe),
    url(r'^issuelink/$', views.issuelinks_all),
    url(r'^cr/$', views.cr_all),
    url(r'^cr/(?P<target>.*)/(?P<project>.*)$', views.cr_list),
    url(r'^cr_detail/(?P<key>.*)$', views.cr_detail),
    url(r'^execution/$', views.execution_all),
    url(r'^execution/(?P<version>.*)/(?P<project>.*)$', views.execution_list),
    url(r'^project/$', views.project_all),
    url(r'^email_bypass/(?P<env>.*)/(?P<email>.*)$', views.request_verification_bypass),
]

urlpatterns = format_suffix_patterns(urlpatterns)
