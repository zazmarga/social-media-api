from content.models import Post

from celery import shared_task


@shared_task
def schedule_post_publication(post_id, time_posting):
    post = Post.objects.get(id=post_id)
    post.is_draft = False
    post.created_at = time_posting
    post.save()
