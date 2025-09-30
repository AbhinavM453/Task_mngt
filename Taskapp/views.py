from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework.response import Response
from .models import User, Task, TaskLog
from .serializers import UserSerializer, TaskSerializer, TaskCompletionSerializer



@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_tasks(request):
    tasks = Task.objects.filter(assigned_to=request.user)
    serializer = TaskSerializer(tasks, many=True)
    return Response(serializer.data)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_task_status(request, pk):
    try:
        task = Task.objects.get(pk=pk, assigned_to=request.user)
    except Task.DoesNotExist:
        return Response({"detail": "Task not found."}, status=status.HTTP_404_NOT_FOUND)

    serializer = TaskCompletionSerializer(task, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        # Log action
        TaskLog.objects.create(
            task=task,
            user=request.user,
            action="status_update",
            details=f"Status updated to {serializer.validated_data.get('status')}"
        )
        return Response(TaskSerializer(task).data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def task_report(request, pk):
    try:
        task = Task.objects.get(pk=pk)
    except Task.DoesNotExist:
        return Response({"detail": "Task not found."}, status=status.HTTP_404_NOT_FOUND)

    # Only allow Admin/SuperAdmin to view completed reports
    if task.status != 'completed':
        return Response({"detail": "Task not completed yet."}, status=status.HTTP_400_BAD_REQUEST)

    if request.user.role not in ['admin', 'superadmin']:
        return Response({"detail": "Not authorized."}, status=status.HTTP_403_FORBIDDEN)

    return Response({
        "completion_report": task.completion_report,
        "worked_hours": task.worked_hours
    })




@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def admin_users(request):
    # if request.user.role != 'superadmin':
    #     return Response({"detail": "Not authorized."}, status=status.HTTP_403_FORBIDDEN)

    if request.method == 'GET':
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)

    if request.method == 'POST':
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def admin_user_detail(request, pk):
    if request.user.role != 'superadmin':
        return Response({"detail": "Not authorized."}, status=status.HTTP_403_FORBIDDEN)

    try:
        user = User.objects.get(pk=pk)
    except User.DoesNotExist:
        return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = UserSerializer(user)
        return Response(serializer.data)
    elif request.method == 'PUT':
        serializer = UserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'DELETE':
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def assign_user_to_admin(request):
    if request.user.role != 'superadmin':
        return Response({"detail": "Not authorized."}, status=status.HTTP_403_FORBIDDEN)

    user_id = request.data.get('user_id')
    admin_id = request.data.get('admin_id')

    try:
        user = User.objects.get(id=user_id)
        admin = User.objects.get(id=admin_id, role='admin')
    except User.DoesNotExist:
        return Response({"detail": "User/Admin not found."}, status=status.HTTP_404_NOT_FOUND)

    user.assigned_admin = admin
    user.save()
    return Response({"detail": f"User {user.username} assigned to Admin {admin.username}"})


@api_view(['GET', 'POST'])
def admin_tasks(request):
    if request.method == 'GET':
        tasks = Task.objects.all()
        serializer = TaskSerializer(tasks, many=True)
        return Response(serializer.data)

    if request.method == 'POST':
        serializer = TaskSerializer(data=request.data)
        if serializer.is_valid():
            # created_by will be null since no user is logged in
            serializer.save(created_by=None)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def admin_task_update(request, pk):
    try:
        task = Task.objects.get(pk=pk)
        if request.user.role == 'admin' and task.assigned_to.assigned_admin != request.user:
            return Response({"detail": "Not authorized."}, status=status.HTTP_403_FORBIDDEN)
    except Task.DoesNotExist:
        return Response({"detail": "Task not found."}, status=status.HTTP_404_NOT_FOUND)

    serializer = TaskSerializer(task, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
