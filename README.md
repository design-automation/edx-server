# edx pull server

This code is adapted from xqueue_pull_ref project https://github.com/Stanford-Online/xqueue_pull_ref

The few changes made are in ref_pull_grader.py ("each_cycle" and "grade" functions specifically). The parameters in project_urls.py and settings.py are also changed.

## Deploy the code

### Update the code on EC2 server

1. `git push` to update the github project.
2. Log into the SSH console of the EC2 instance.
3. navigate to ~mobius_server/edx-server.
4. `git pull` to update the project on the EC2 server.
5. `pip install <missing packages>` if there are new packages installed.
6. If there is a new queue for edx, update the `auth.py` file with the edx queue credentials using `vim auth.py`

### Run the server

There are 2 ways to run the server. Make sure that all the running instances (regardless of how these instances are run) are updated. Currently, the server only have one running instance using systemd service. 

#### systemd service

systemd service allow a server instance to be started the moment an amazon ec2 is initiated as well as restarting the instance when the instance is forced shut down when an error occurs. To update the service:

1. Log into the SSH console of the EC2 instance.
2. `sudo systemctl stop edx.service` to stop the current edx service.
3. `sudo systemctl daemon-reload` to reload the service.
4. `sudo systemctl start edx.service` to start the current edx service again.
5. `sudo systemctl status edx.service` to check the status of edx service. The status should be "active".

The systemd service utilize 2 files: a systemd service file and a .sh script file. The service file is located in "/lib/systemd/system/edx.service" (to edit the file, right after logging into the SSH console, do `vim ../../lib/systemd/system/edx.service`). the script file is located in "~/mobius_server/edx-server/startEDX.sh" ("/home/ubuntu/edx.service", to edit the file, right after logging into the SSH console, do `vim mobius_server/edx-server/startEDX.sh`). After editing either of these files, the systemd service needs to be updated, restart it as per above (stop edx.service, daemon-reload and start edx.service again).

#### Screen

Screen is another way of running the server. It is not currently used as it does not restarting the server when it is forced shut down due to error or automatically start the server when the ec2 instance is initialized.

1. Log into the SSH console of the EC2 instance.
2. navigate to ~mobius_server/edx-server.
3. `screen -ls` to check if there are any active screen. if there is one, `screen -r` to resume working on that screen; if there is none, `screen` to create a new screen
4. `python ref_pull_grader.py` to run the server code
5. CTRL-A then D to detach from the screen, allow the server to run on the screen even after we exit the console.
