from django.urls import path
from .views import CreateSessionView, SendMessageView, SessionDetailView

urlpatterns = [
    path('sessions/', CreateSessionView.as_view()),
    path('sessions/<int:session_id>/', SessionDetailView.as_view()),
    path('sessions/<int:session_id>/message/', SendMessageView.as_view()),
]
