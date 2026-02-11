from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from .models import Post, Comment
from .forms import CommentForm, CommentEditForm

def home(request):
    """Homepage view showing recent published posts"""
    posts = Post.objects.filter(status='published').order_by('-published_at')[:5]
    return render(request, 'blog/home.html', {'posts': posts})

def post_detail(request, pk):
    """View a single blog post with comments"""
    post = get_object_or_404(Post, pk=pk)
    return render(request, 'blog/post_detail.html', {'post': post})

# Add comment to post
@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user
            
            # Auto-approve staff users and post authors
            if request.user.is_staff or request.user == post.author:
                comment.approved = True
                messages.success(request, 'Comment published successfully!')
            else:
                comment.approved = False
                messages.info(request, 'Your comment is awaiting moderation.')
            
            comment.save()
    
    return redirect('blog:post_detail', pk=post.id)

# Edit comment
@login_required
def edit_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    
    # Permission check
    if comment.author != request.user and not request.user.is_staff:
        messages.error(request, 'You cannot edit this comment.')
        return redirect('blog:post_detail', pk=comment.post.id)
    
    if request.method == 'POST':
        form = CommentEditForm(request.POST, instance=comment)
        if form.is_valid():
            form.save()
            messages.success(request, 'Comment updated!')
            return redirect('blog:post_detail', pk=comment.post.id)
    else:
        form = CommentEditForm(instance=comment)
    
    return render(request, 'blog/edit_comment.html', {
        'form': form,
        'comment': comment,
        'post': comment.post
    })

# Delete comment - UPDATED to handle GET requests
@login_required
def delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    
    # Permission check
    if comment.author != request.user and not request.user.is_staff:
        messages.error(request, 'You cannot delete this comment.')
        return redirect('blog:post_detail', pk=comment.post.id)
    
    # Handle both GET (link click) and POST (form submission)
    if request.method in ['GET', 'POST']:
        comment.delete()
        messages.success(request, 'Comment deleted.')
        return redirect('blog:post_detail', pk=comment.post.id)
    
    # Show confirmation page for other methods (though unlikely)
    return render(request, 'blog/confirm_delete.html', {'comment': comment})

# Approve comment (admin only) - UPDATED to handle GET requests
@staff_member_required
def approve_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    
    # Handle both GET and POST
    if request.method in ['GET', 'POST']:
        comment.approved = True
        comment.save()
        messages.success(request, 'Comment approved.')
        return redirect('blog:post_detail', pk=comment.post.id)
    
    # Fallback (shouldn't normally be reached)
    return redirect('blog:post_detail', pk=comment.post.id)

# Comment moderation dashboard
@staff_member_required
def comment_moderation(request):
    pending_comments = Comment.objects.filter(approved=False)
    return render(request, 'blog/comment_moderation.html', {
        'pending_comments': pending_comments
    })