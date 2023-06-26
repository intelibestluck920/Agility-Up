from .models import Sprint, FeedBack, FeedbackElevationRecord
from datetime import datetime, timedelta, date
from .helpers import sprint_name_convention

from django.core.mail import send_mail


def create_sprint_periodic():
    if Sprint.objects.filter(end_date=datetime.today()):
        sprints = Sprint.objects.filter(end_date=datetime.today())
        for sprint in sprints:
            # create new sprint
            cadence = sprint.end_date - sprint.start_date
            name = sprint_name_convention(sprint.name)
            Team = sprint.Team
            start_date = sprint.end_date + timedelta(days=1)
            end_date = sprint.end_date + timedelta(days=(cadence.days + 1))
            new_sprint = Sprint.objects.create(name=name, Team=Team,
                                               start_date=start_date,
                                               end_date=end_date)
    else:
        pass


        # elevate unaddressed negative feedbacks
            # Feedback_list = sprint.feedback_elevate()
            # Feedbacks = FeedBack.objects.filter(id__in=Feedback_list)
            # Feedbacks.update(Sprint=new_sprint, created_at=datetime.today())

            # create record of elevation
            # for f in Feedbacks:
            #     FeedbackElevationRecord.objects.create(OriginalSprint=sprint, CurrentSprint=new_sprint,
            #                                            Feedback_id=f.id)


def alert_sprint_expire():
    dt = date.today() + timedelta(days=2)
    if Sprint.objects.filter(end_date=dt).exists():
        sprints = Sprint.objects.filter(end_date=dt).values('id')
        if FeedBack.objects.filter(addressed=False, sprint__in=sprints).exists():
            feedbacks = FeedBack.objects.filter(addressed=False, sprint__in=sprints)

            to_email = []
            for feedback in feedbacks:
                to_email.append(feedback.Team.team_lead.email)

            subject = 'Sprint expiring'
            message = f'Current sprint will expire in 2 days, ' \
                      f'address your teams feedbacks or they will be ' \
                      f'added to upcoming sprints.'

            from_email = 'agility.up.ai.test@gmail.com'

            send_mail(
                subject,
                message,
                from_email,
                to_email,
                fail_silently=False
            )


def alert_feedback():
    dt = date.today() + timedelta(days=2)
    if Sprint.objects.filter(end_date=dt).exists():
        sprints = Sprint.objects.filter(end_date=dt).values('id')

        to_email = []
        for sprint in sprints:
            email_list = sprint.Team.team_members.values_list('email', flat=True)
            for email in email_list:
                to_email.append(email.email)

        subject = 'Sprint expiring'
        message = f'Current sprint will expire in 2 days, ' \
                  f'give your feedbacks ' \
                  f'for current sprint.'

        from_email = 'agility.up.ai.test@gmail.com'

        send_mail(
            subject,
            message,
            from_email,
            to_email,
            fail_silently=False
        )
