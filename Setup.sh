#!bin/bash
# This script sets up the environment for the project by installing necessary packages and dependencies.
# Update the package list
sudo apt-get update
# Install Python 3 and pip
sudo apt-get install -y python3 python3-pip
# Install virtualenv
sudo apt install -y python3-venv
# Install required Python packages
pip install -r requirements.txt --break-system-packages
# Set up cron job to run main.py once a week, sunday at 12:00 AM
(crontab -l ; echo "0 0 * * sun /home/$USER/auto-backup/main.py") | crontab -
echo "Environment setup complete. You can now start using the project."
# Install SFTP enable and configure it as needed to RUN   



