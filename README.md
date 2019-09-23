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
