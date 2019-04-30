# edx pull server

This code is adapted from xqueue_pull_ref project https://github.com/Stanford-Online/xqueue_pull_ref

The few changes made are in ref_pull_grader.py, each_cycle and grade functions. The parameters in project_urls.py and settings.py are also changed.

## Deploy the code

1. `git push` to update the github project
2. Log into the SSH console of the EC2 instance
3. navigate to ~mobius_server/edx-server
4. `git pull` to update the project on the EC2 server
5. `pip install <missing packages>`
6. `screen -ls` to check if there are any active screen. if there is one, `screen -r` to resume working on that screen; if there is none, `screen` to create a new screen
7. `python ref_pull_grader.py` to run the server code
8. CTRL-A then D to detach from the screen, allow the server to run on the screen even after we exit the console.

## Authentication

Currently, a slightly modified version of my access key is stored in auth.py in the project folder on the EC2 instance (the file is added to .gitignore so that it won't be uploaded to github so my account wouldn't be flagged as compromised again).
This authentication method is not very safe. I would prefer to change it to role based using boto3 in the future.
If anyone would like to change the auth.py file, in the ssh console, `nano auth.py` and change it accordingly. Also, the code in line 20-21 in ref_pull_grader.py also need to be changed.