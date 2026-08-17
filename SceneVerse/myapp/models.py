from django.db import models

class Register(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20)
    creator_role = models.CharField(max_length=20, blank=True, null=True)
    artist_role = models.CharField(max_length=20, blank=True, null=True)
    password = models.CharField(max_length=100)
    rights = models.CharField(max_length=100, default='user')

    created_at = models.DateTimeField(auto_now_add=True)
    last_activity = models.DateTimeField(null=True, blank=True)


    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Project(models.Model):
    added_by = models.ForeignKey(Register,on_delete=models.CASCADE)
    project_title = models.CharField(max_length=255)
    project_type = models.CharField(max_length=50)
    project_description = models.TextField(blank=True, null=True)
    genre = models.CharField(max_length=100)
    project_status = models.CharField(max_length=50)
    rights = models.CharField(max_length=100, default='project')

    # Media Fields
    image = models.ImageField(upload_to='projects/images/', null=True, blank=True)
    video = models.FileField(upload_to='projects/videos/', null=True, blank=True)
    video_start = models.FloatField(default=0.0)
    video_end = models.FloatField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.project_title



class CastingCall(models.Model):
    project_title = models.ForeignKey(Project,on_delete=models.CASCADE)
    added_by = models.ForeignKey(Register,on_delete=models.CASCADE)
    role_title = models.CharField(max_length=255)
    role_category = models.CharField(max_length=50)
    role_requirements = models.CharField(max_length=500, null=True)
    role_description = models.TextField(blank=True, null=True)
    required_gender = models.CharField(max_length=20, default='Any')
    age_range = models.CharField(max_length=50, blank=True, null=True)
    compensation = models.CharField(max_length=100)
    deadline = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.role_title} for {self.project_title}"

class ArtistDetails(models.Model):
    added_by = models.ForeignKey(Register,on_delete=models.CASCADE)
    coverphoto = models.ImageField(upload_to='images/',null=True)
    avatarphoto = models.ImageField(upload_to='images/',null=True)
    title = models.TextField(blank=True)
    about = models.TextField(blank=True)
    gender=models.CharField(max_length=100,default="Not interested to say")
    location = models.CharField(max_length=150)
    skillsinput = models.CharField(max_length=100)
    phone = models.TextField(max_length=100,blank=True)
    personalwebsite = models.TextField(max_length=100,blank=True)
    instagram = models.TextField(max_length=100,blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.added_by}"


class Applications(models.Model):
    casting_id = models.ForeignKey(CastingCall,on_delete=models.CASCADE)
    added_by = models.ForeignKey(Register,on_delete=models.CASCADE)
    details_of = models.ForeignKey(ArtistDetails,on_delete=models.CASCADE,null=True)
    message = models.CharField(max_length=255)
    application_status = models.CharField(max_length=100, default='Pending',null=True)



    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.added_by} for {self.casting_id.role_title} of {self.casting_id.project_title}"


class ApplicationAttachment(models.Model):
    application = models.ForeignKey(Applications, on_delete=models.CASCADE, related_name='attachments')
    file = models.FileField(upload_to='applications/attachments/')
    file_type = models.CharField(max_length=20, default='unknown') # 'image' or 'video'
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Attachment for Application {self.application.id}"


class ProjectComment(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    added_by = models.ForeignKey(Register, on_delete=models.CASCADE)
    comment = models.TextField()
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.added_by} on {self.project}"


class ProjectLike(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    liked_by = models.ForeignKey(Register, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

class Post(models.Model):
    added_by = models.ForeignKey(Register, on_delete=models.CASCADE)
    caption = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return f"Post by {self.added_by.first_name} {self.added_by.last_name} at {self.created_at}"


class PhotoPost(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, null=True)
    image = models.ImageField(upload_to='posts/images/', blank=False, null=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"PhotoPost by {self.created_at}"

class VideoPost(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, null=True)
    video = models.FileField(upload_to='posts/videos/', blank=False, null=False)
    start_time = models.FloatField(default=0.0)
    end_time = models.FloatField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"VideoPost by {self.created_at}"

class ArtistLike(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    liked_by = models.ForeignKey(Register, on_delete=models.CASCADE)  # artist user
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.liked_by.first_name} liked Post {self.post.id}"

class ArtistComment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    commented_by = models.ForeignKey(Register, on_delete=models.CASCADE)
    comment = models.TextField()
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.commented_by.first_name} on Post {self.post.id}"


class ChatThread(models.Model):
    participants = models.ManyToManyField(Register, related_name='chat_threads')
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Thread {self.id}"

class ChatMessage(models.Model):
    thread = models.ForeignKey(ChatThread, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(Register, on_delete=models.CASCADE)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    is_edited = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)           # Delete for everyone
    deleted_by_sender = models.BooleanField(default=False)   # Delete for me (sender only)
    deleted_by_recipient = models.BooleanField(default=False) # Delete for me (recipient only)

    def __str__(self):
        return f"Message by {self.sender} in Thread {self.thread.id}"

class ChatTyping(models.Model):
    thread = models.ForeignKey(ChatThread, on_delete=models.CASCADE)
    user = models.ForeignKey(Register, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user} is typing in {self.thread}"
