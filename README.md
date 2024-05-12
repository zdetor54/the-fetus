# the-fetus

This is the nth attempt to create the website. Is it working?

1. Create new env 'python -m venv fetusappenv'
2. Use '.\fetusappenv\Scripts\activate' to activate the VM
3. update the requirements 'pip install -r requirements.txt'


To migrate the database
1. flask db init #only the first time
2. flask db migrate -m "Initial migration."
3. flask db upgrade

Colour pallete
Calming Blue (#297FB9) - Provides a sense of trust and professionalism.
Vibrant Pink (#EF539E) - Offers a warm, engaging contrast.
Muted Coral (#F9A5A5) - A soft, soothing pink that pairs well with vibrant pink for a gentle touch.
Warm Beige (#F3E1D7) - A neutral, warm tone that adds an understated elegance and softens the overall look.
Rich Navy (#0B3C5D) - A deeper blue that enhances the seriousness and trustworthiness of the palette.

https://help.pythonanywhere.com/pages/Virtualenvs

pip freeze > requirements2.txt

Aftert deploying the app to pythonanywhere using the instructions detailed here: https://www.youtube.com/watch?v=Bx_jHawKn5A&list=PLWYY9UuOfmS2czQgos9-StzLE3eqKkZTi&index=5
1. go to the vm and migrate the database using the above instructions.
2. create an admin user as per the _assets/admin_user.txt
3. deploy the app

for updates...
1. cd to the-fetus folder
2. run the git pull origin main
3. redeploy the app