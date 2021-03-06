from django.shortcuts import render,get_object_or_404
from django.core.paginator import Paginator
from django.conf import settings
from django.db.models import Count
from django.contrib.contenttypes.models import ContentType

from .models import Blog,BlogType
from read_statistics.utils import read_statistics_once_read

def get_blog_list_common_data(request,blogs_all_list):
    # 分页
    paginator = Paginator(blogs_all_list, settings.EACH_PAGE_BLOGS_NUMBER)  # 每4篇进行分页
    page_num = request.GET.get('page', 1)  # 获取页面参数
    page_of_blogs = paginator.get_page(page_num)
    current_page_num = page_of_blogs.number
    page_range = list(range(max(current_page_num - 2, 1), current_page_num)) + \
                 list(range(current_page_num, min(current_page_num + 2, paginator.num_pages) + 1))
    # 博客分类数量
    blog_types = BlogType.objects.all()
    blog_types_list = []
    for blog_type in blog_types:
        blog_type.blog_count = Blog.objects.filter(blog_type=blog_type).count()
        blog_types_list.append(blog_type)
    # 日期归档数量
    blog_dates = Blog.objects.dates('created_time', 'month', order='DESC')
    blog_dates_dict = {}
    for blog_date in blog_dates:
        blog_count = Blog.objects.filter(created_time__year=blog_date.year,created_time__month=blog_date.month).count()
        blog_dates_dict[blog_date] = blog_count

    context = {}
    context['blogs'] = page_of_blogs.object_list
    context['page_of_blogs'] = page_of_blogs
    context['page_range'] = page_range
    context['blog_types'] = blog_types_list
    context['blog_dates'] = blog_dates_dict
    return context

def blog_list(request):
    blogs_all_list = Blog.objects.all()
    context = get_blog_list_common_data(request,blogs_all_list)
    return render(request,'blog_list.html',context)

def blog_detail(request,blog_pk):
    blog = get_object_or_404(Blog, pk=blog_pk)
    read_cookie_key = read_statistics_once_read(request,blog)

    context = {}
    context['previous_blog'] = Blog.objects.filter(created_time__gt=blog.created_time).last()
    context['next_blog'] = Blog.objects.filter(created_time__lt=blog.created_time).first()
    context['blog'] = blog
    response = render(request,'blog_detail.html',context)   # 响应
    response.set_cookie(read_cookie_key,'true')   # 阅读cookie标记
    return response

def blogs_with_type(request,blog_type_pk):
    blog_type = get_object_or_404(BlogType,pk=blog_type_pk)
    blogs_all_list = Blog.objects.filter(blog_type=blog_type)
    context = get_blog_list_common_data(request,blogs_all_list)
    context['blog_type'] = blog_type
    return render(request,'blogs_with_type.html',context)

def blogs_with_date(request,year,month):
    blogs_all_list = Blog.objects.filter(created_time__year=year,created_time__month=month,)
    context = get_blog_list_common_data(request,blogs_all_list)
    context['blogs_with_date'] = '%s年%s月' % (year,month)
    return render(request, 'blogs_with_date.html', context)