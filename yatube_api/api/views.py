from rest_framework.response import Response

from posts.models import (Post,
                          Group,
                          Comment)
from rest_framework import viewsets, status
from .serializers import (PostSerializer,
                          GroupSerializer, CommentSerializer)
from django.contrib.auth import get_user_model

User = get_user_model()


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer

    def create(self, request, *args, **kwargs):
        if request.method == "POST":
            user = request.user
            serializer = PostSerializer(data=request.data)
            if serializer.is_valid():
                serializer.validated_data['author'] = user
                serializer.save()
                return Response(serializer.data,
                                status=status.HTTP_201_CREATED)
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        if request.user != self.get_object().author:
            return Response(status=status.HTTP_403_FORBIDDEN)
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        if request.user != self.get_object().author:
            return Response(status=status.HTTP_403_FORBIDDEN)
        return super().destroy(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        if request.user != self.get_object().author:
            return Response(status=status.HTTP_403_FORBIDDEN)
        return super().partial_update(request, *args, **kwargs)


class GroupViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer


class CommentViewSet(viewsets.ViewSet):
    queryset = Comment.objects.all()

    def list(self, request, post_id=None):
        post = self.get_post(post_id)
        if post is not None:
            comments = Comment.objects.filter(post=post)
            serializer = CommentSerializer(comments,
                                           many=True)
            return Response(serializer.data)
        return Response(
            {'error': 'Возможно пост не существует.'
             }, status=status.HTTP_400_BAD_REQUEST)

    def create(self, request, post_id=None):
        post = self.get_post(post_id)
        if post is None:
            return Response(status=status.HTTP_404_NOT_FOUND)

        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.validated_data['author'] = request.user
            serializer.validated_data['post'] = post
            serializer.save(post=post)
            return Response(serializer.data,
                            status=status.HTTP_201_CREATED)
        return Response(serializer.errors,
                        status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, post_id=None, pk=None):
        post = self.get_post(post_id)
        if post is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        try:
            comment = self.queryset.get(id=pk,
                                        post_id=post_id)
        except Comment.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = CommentSerializer(comment)
        return Response(serializer.data,
                        status=status.HTTP_200_OK)

    def update(self,
               request,
               post_id=None,
               pk=None):
        post = self.get_post(post_id)
        if post is None:
            return Response(status=status.HTTP_404_NOT_FOUND)

        try:
            comment = self.queryset.get(id=pk, post_id=post_id)
            if comment.author != request.user:
                return Response(status=status.HTTP_403_FORBIDDEN)
            serializer = CommentSerializer(comment,
                                           data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)
        except Comment.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def destroy(self, request, post_id=None, pk=None):
        """Удаление комментария."""
        post = self.get_post(post_id)

        if post is None:
            return Response(status=status.HTTP_404_NOT_FOUND)

        try:
            comment = post.comments.get(pk=pk)
            if comment.author != request.user:
                return Response(status=status.HTTP_403_FORBIDDEN)
            comment.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Comment.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def partial_update(self, request, post_id=None, pk=None):
        post = self.get_post(post_id)
        if post is None:
            return Response(status=status.HTTP_404_NOT_FOUND)

        try:
            comment = self.queryset.get(id=pk, post_id=post_id)
            serializer = CommentSerializer(comment,
                                           data=request.data,
                                           partial=True)
            if comment.author != request.user:
                return Response(status=status.HTTP_403_FORBIDDEN)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)
        except Comment.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def get_post(self, post_id=None):
        try:
            return Post.objects.get(pk=post_id)
        except Post.DoesNotExist:
            return None
