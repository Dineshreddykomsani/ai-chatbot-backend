from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from drf_yasg.utils import swagger_auto_schema

from .models import ChatSession, Message
from .serializers import ChatSessionSerializer, SendMessageSerializer
from .services import build_prompt, call_llm


class CreateSessionView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        responses={201: "Session created successfully"}
    )
    def post(self, request):
        session = ChatSession.objects.create(user=request.user)
        return Response({"session_id": session.id}, status=201)


class SendMessageView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        request_body=SendMessageSerializer,
        responses={200: "Message sent successfully"}
    )
    def post(self, request, session_id):
        serializer = SendMessageSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=400)

        try:
            session = ChatSession.objects.get(id=session_id, user=request.user)
        except ChatSession.DoesNotExist:
            return Response({"error": "Invalid session"}, status=404)

        # Save user message
        Message.objects.create(
            session=session,
            role="user",
            content=serializer.validated_data["message"]
        )

        # Build prompt from history
        history = session.messages.all().order_by("created_at")
        prompt = build_prompt(history)

        # Call AI
        ai_response = call_llm(prompt)

        # Save assistant response
        Message.objects.create(
            session=session,
            role="assistant",
            content=ai_response
        )

        return Response({"reply": ai_response}, status=200)


class SessionDetailView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        responses={200: ChatSessionSerializer}
    )
    def get(self, request, session_id):
        try:
            session = ChatSession.objects.get(id=session_id, user=request.user)
        except ChatSession.DoesNotExist:
            return Response({"error": "Invalid session"}, status=404)

        serializer = ChatSessionSerializer(session)
        return Response(serializer.data)