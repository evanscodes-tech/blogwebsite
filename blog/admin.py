from django.contrib import admin
from django.utils import timezone
from .models import Post, Category, Tag, Comment


# ===== CATEGORY ADMIN =====
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'created_at')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name', 'description')


# ===== TAG ADMIN =====
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)


# ===== POST ADMIN =====
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'category', 'status', 'created_at', 'was_published_recently')
    list_filter = ('status', 'created_at', 'author', 'category')
    search_fields = ('title', 'content')
    prepopulated_fields = {'slug': ('title',)}
    list_per_page = 25
    readonly_fields = ('updated_at',)
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'slug', 'content', 'author')
        }),
        ('Categorization', {
            'fields': ('category', 'tags')
        }),
        ('Status & Media', {
            'fields': ('status', 'cover_image', 'views_count')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'published_at'),
            'classes': ('collapse',)
        })
    )
    
    def was_published_recently(self, obj):
        if not obj.published_at:
            return False
        now = timezone.now()
        return now - timezone.timedelta(days=1) <= obj.published_at <= now
    
    was_published_recently.boolean = True
    was_published_recently.short_description = 'Published recently?'


# ===== COMMENT ADMIN =====
class CommentAdmin(admin.ModelAdmin):
    list_display = ('author', 'post', 'content_preview', 'approved', 'created_at', 'has_replies')
    list_filter = ('approved', 'created_at', 'author')
    search_fields = ('content', 'author__username', 'post__title')
    actions = ['approve_comments', 'disapprove_comments']
    list_per_page = 25
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Comment Information', {
            'fields': ('post', 'author', 'content', 'parent')
        }),
        ('Moderation', {
            'fields': ('approved',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def content_preview(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Content'
    
    def has_replies(self, obj):
        return obj.replies.count() > 0
    has_replies.boolean = True
    has_replies.short_description = 'Has Replies'
    
    def approve_comments(self, request, queryset):
        queryset.update(approved=True)
        self.message_user(request, f"{queryset.count()} comments approved.")
    approve_comments.short_description = "Approve selected comments"
    
    def disapprove_comments(self, request, queryset):
        queryset.update(approved=False)
        self.message_user(request, f"{queryset.count()} comments disapproved.")
    disapprove_comments.short_description = "Disapprove selected comments"


# ===== REGISTER ALL MODELS =====
admin.site.register(Category, CategoryAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Post, PostAdmin)
admin.site.register(Comment, CommentAdmin)