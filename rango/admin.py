from django.contrib import admin

from rango.models import Category, Page, UserProfile


class PageAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "url")


class PageInLine(admin.StackedInline):
    model = Page
    extra = 1


class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}
    inlines = [PageInLine]


admin.site.register(Category, CategoryAdmin)
admin.site.register(Page, PageAdmin)
admin.site.register(UserProfile)
