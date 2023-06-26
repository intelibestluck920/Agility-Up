from django.contrib import admin
from .models import *


# Register your models here.

class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('id', 'score', 'Sprint', 'Team')
    search_fields = ('Team__name', 'User__email')


class SentimentAnalysisAdmin(admin.ModelAdmin):
    list_display = ('id', 'feedback_sentence', 'score', 'addressed')


class SprintAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'Team', 'start_date', 'end_date')
    search_fields = ('Team__name',)


# class TeamMembersAdmin(admin.ModelAdmin):
#     list_display = ('id', 'member', 'team', 'created_at', 'updated_at')
#     search_fields = ('team__name', 'member__email')

class TeamMembersAdmin(admin.ModelAdmin): # TODO fix create_at
    list_display = ('id', 'member', 'team', 'create_at', 'updated_at')
    search_fields = ('team__name', 'member__email')

class TeamAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'team_lead', 'team_members', 'pause')
    search_fields = ('team_lead__email',)

    def team_members(self, obj):
        return "\n".join([p.email for p in obj.team_members.all()])


class FeedbackElevationAdmin(admin.ModelAdmin):
    list_display = ('id', 'OriginalSprint', 'CurrentSprint', 'Feedback')


class BucketAdmin(admin.ModelAdmin):
    list_display = ('id', 'keyword', 'created_at', 'updated_at')
    search_fields = ('keyword',)


admin.site.register(Team, TeamAdmin)
admin.site.register(TeamMembers, TeamMembersAdmin)
admin.site.register(Sprint, SprintAdmin)
admin.site.register(FeedBack, FeedbackAdmin)
admin.site.register(SentimentAnalysis, SentimentAnalysisAdmin)
admin.site.register(FeedbackElevationRecord, FeedbackElevationAdmin)
admin.site.register(Bucket, BucketAdmin)
