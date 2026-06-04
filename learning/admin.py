from django.contrib import admin 
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin 
from learning.models import ( 
    Role, User, UserProfile, 
    Language, Course, Module, Lesson, Exercise, 
    UserProgress, UserStats, Achievement, UserAchievement, 
    Subscription, UserSubscription, Payment, Order, 
) 

@admin.register(Role) 
class RoleAdmin(admin.ModelAdmin): 
    list_display = ['id', 'name'] 

@admin.register(User) 
class UserAdmin(BaseUserAdmin): 
    list_display = ['id', 'email', 'username', 'role', 'is_active', 'is_staff'] 
    fieldsets = BaseUserAdmin.fieldsets + ( 
        ('Info adicional', {'fields': ('role',)}), 
    ) 

@admin.register(UserProfile) 
class UserProfileAdmin(admin.ModelAdmin): 
    list_display = ['id', 'user', 'first_name', 'last_name', 'native_language'] 

@admin.register(Language) 
class LanguageAdmin(admin.ModelAdmin): 
    list_display = ['id', 'name', 'code'] 

@admin.register(Course) 
class CourseAdmin(admin.ModelAdmin): 
    list_display = ['id', 'title', 'language', 'difficulty_level'] 
    list_filter = ['difficulty_level', 'language'] 

@admin.register(Module) 
class ModuleAdmin(admin.ModelAdmin): 
    list_display = ['id', 'title', 'course', 'order'] 

@admin.register(Lesson) 
class LessonAdmin(admin.ModelAdmin): 
    list_display = ['id', 'title', 'module', 'content_type', 'order', 'xp_reward'] 

@admin.register(Exercise) 
class ExerciseAdmin(admin.ModelAdmin): 
    list_display = ['id', 'lesson', 'exercise_type', 'question_text'] 

@admin.register(UserProgress) 
class UserProgressAdmin(admin.ModelAdmin): 
    list_display = ['id', 'user', 'lesson', 'status', 'score'] 

@admin.register(UserStats) 
class UserStatsAdmin(admin.ModelAdmin): 
    list_display = ['id', 'user', 'total_xp', 'current_streak', 'longest_streak'] 

@admin.register(Achievement) 
class AchievementAdmin(admin.ModelAdmin): 
    list_display = ['id', 'name', 'required_xp'] 

@admin.register(UserAchievement) 
class UserAchievementAdmin(admin.ModelAdmin): 
    list_display = ['id', 'user', 'achievement', 'unlocked_at'] 

@admin.register(Subscription) 
class SubscriptionAdmin(admin.ModelAdmin): 
    list_display = ['id', 'name', 'price', 'duration_days'] 

@admin.register(UserSubscription) 
class UserSubscriptionAdmin(admin.ModelAdmin): 
    list_display = ['id', 'user', 'subscription', 'is_active'] 

@admin.register(Payment) 
class PaymentAdmin(admin.ModelAdmin): 
    list_display = ['id', 'user', 'amount', 'payment_method', 'status'] 


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'subscription', 'total_amount', 'payment_method', 'status', 'created_at']
