from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from .models import Blog
from .forms import BlogForm
from PIL import Image
from django.contrib import messages

def register(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("home")
    else:
        form = UserCreationForm()
    return render(request, "registration/register.html", {"form": form})

def user_login(request):
    if request.user.is_authenticated:
        return redirect("home")
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect("home")
    else:
        form = AuthenticationForm()
    return render(request, "registration/login.html", {"form": form})

@login_required
def user_logout(request):
    logout(request)
    return redirect("login")



def home(request):
    """Show all public blogs + private blogs of the logged-in user"""
    messages.info(
        request,
        "Welcome to our blogging platform! 🎉 This app is completely free to use. You can write your personal diary, share your thoughts as blogs, and even add images to make them more engaging. Your posts are private unless you choose to share them. Enjoy a secure and hassle-free blogging experience!"
    )
    if request.user.is_authenticated:
        blogs = Blog.objects.filter(is_public=True) | Blog.objects.filter(author=request.user)
    else:
        blogs = Blog.objects.filter(is_public=True)  # Only public blogs for anonymous users

    return render(request, 'home.html', {'blogs': blogs})


@login_required
def create_blog(request):
    if request.method == "POST":
        
        form = BlogForm(request.POST, request.FILES)

        if form.is_valid():
            blog = form.save(commit=False)
            blog.author = request.user
            blog.save()

            return redirect('home')
            
    else:
        form = BlogForm()
        
    return render(request, "create_blog.html", {"form": form})

def blog_detail(request, slug):
    blog = get_object_or_404(Blog, slug=slug)

    # Ensure that only one image is used
    image = blog.image if blog.image else None  

    if image:
        img = Image.open(blog.image.path)
        max_size = (500, 500)  # Adjust max width & height
        img.thumbnail(max_size)
        img.save(blog.image.path)

    # Restrict access to private blogs
    if not blog.is_public and request.user != blog.author:
        return render(request, 'not_allowed.html')  # Show access denied page

    # Track views for authenticated users
    if request.user.is_authenticated:
        if not hasattr(blog, "viewed_users") or request.user not in blog.viewed_users.all():
            blog.views += 1
            blog.viewed_users.add(request.user)
            blog.save()
    else:
        # Track views for anonymous users using session
        session_key = f'viewed_blog_{blog.slug}'
        if not request.session.get(session_key, False):
            blog.views += 1
            blog.save()
            request.session[session_key] = True  # Mark this blog as viewed

    return render(request, 'blog_detail.html', {'blog': blog, 'image': image})



@login_required
def edit_blog(request, blog_id):
    blog = get_object_or_404(Blog, id=blog_id, author=request.user)

    if request.method == "POST":
        form = BlogForm(request.POST, request.FILES, instance=blog)
        if form.is_valid():
            form.save()
            messages.success(request, "Blog updated successfully!")
            return redirect('blog_detail', blog_id=blog.id)
    else:
        form = BlogForm(instance=blog)

    return render(request, 'edit_blog.html', {'form': form, 'blog': blog})



@login_required
def delete_blog(request, blog_id):
    blog = get_object_or_404(Blog, id=blog_id, author=request.user)

    if request.method == "POST":
        blog.delete()
        messages.success(request, "Blog deleted successfully!")
        return redirect('home')  # Redirect to home page after deletion

    return render(request, 'confirm_delete.html', {'blog': blog})
