AgilityUp backend APIs:

install and run:

1. create virtual env.
2. install requirements from requirements.txt.
3. run production server "python manage.py runserver".

Endpoint list and detail:

1. team-list
   response: team-id, team-name
2. team-detail:
   parameters: team-id
   response: team-id, team-name
3. team-create:
   post: name
4. team-update: 
   parameters: id
   post: id, name
5. invite-member: 
   post: email, team_id
6. create-sprint:
   post: cadence, start_date, team
7. submit-feedback:
   post: Sprint, feedback
8. 
    
