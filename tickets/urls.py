from rest_framework.routers import DefaultRouter

from .views import (
    TicketViewSet,
    CommentViewSet,
    AgentViewSet,
)

router = DefaultRouter()

router.register(r"tickets", TicketViewSet, basename="tickets")
router.register(r"comments", CommentViewSet, basename="comments")
router.register(r"agents", AgentViewSet, basename="agents")

urlpatterns = router.urls