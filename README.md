# the-fetus

This is the nth attempt to create the website. Is it working?

1. Create new env 'python -m venv fetusappenv'
2. Use '.\fetusappenv\Scripts\activate' to activate the VM
3. update the requirements 'pip install -r requirements.txt'


To migrate the database
1. flask db init #only the first time
2. flask db migrate -m "Initial migration."
3. flask db upgrade
4. follow the scripts in the migration_scripts folder:
    * for patients ensure records without a last name are deleted or updated

To include the keys to the APIs
1. Create the keys.env in the root folder (same as this README.md)
2. Update with the required Keys

Colour pallete
Calming Blue (#297FB9) - Provides a sense of trust and professionalism.
Vibrant Pink (#EF539E) - Offers a warm, engaging contrast.
Muted Coral (#F9A5A5) - A soft, soothing pink that pairs well with vibrant pink for a gentle touch.
Warm Beige (#F3E1D7) - A neutral, warm tone that adds an understated elegance and softens the overall look.
Rich Navy (#0B3C5D) - A deeper blue that enhances the seriousness and trustworthiness of the palette.

# Deploy in PythonAnywhere

https://help.pythonanywhere.com/pages/Virtualenvs

pip freeze > requirements2.txt

After deploying the app to pythonanywhere using the instructions detailed here: https://www.youtube.com/watch?v=Bx_jHawKn5A&list=PLWYY9UuOfmS2czQgos9-StzLE3eqKkZTi&index=5
1. go to the vm and migrate the database using the above instructions.
2. create an admin user as per the _assets/admin_user.txt
3. deploy the app

for updates...
1. cd to the-fetus folder
2. run the git stash / git pull origin main
3. redeploy the app or
4. pip install -r requirements.txt for the dependencies


IDEAS:
- Have a panel with the pregrancies that are about to BURST
- Have a visual indication of the age of the patient, how many pregnancies she has, etc
- API for greek addresses
- in no patients have infographics

rebase from origin
- git fetch origin
- git rebase origin/main (while on the branch)