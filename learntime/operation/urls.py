from django.urls import path

from learntime.operation import views

app_name = "operations"
urlpatterns = [
    path('logs/', view=views.LogList.as_view(), name='log_list'),
    path('join-list/', view=views.StudentActivityListView.as_view(), name='join_list'),
    path('sign-in-list/', view=views.SignInListView.as_view(), name='sign_in_list'),
    path('qrcode/<str:pk>/<int:frequency>/<int:signInOrSignOut>/<int:nonce>/', view=views.QRCodeAPIView.as_view(), name='qrcode'),
    path('person-list/<str:pk>/', view=views.PersonListAPIView.as_view(), name='person_list'),
]
