#!bin/bash
# This script sets up the environment for the project by installing necessary packages and dependencies.
# Update the package list
sudo apt-get update
# Install Python 3 and pip
sudo apt-get install -y python3 python3-pip
# Install virtualenv
sudo apt install -y python3-venv
# Create a virtual environment
python3 -m venv venv
# Activate the virtual environment
source venv/bin/activate
# Install required Python packages
pip install -r requirements.txt
# Set up cron job to run main.py once a week, sunday at 12:00 AM
(crontab -l ; echo "0 0 * * sun /home/$USER/Backup/main.py") | crontab -
echo "Environment setup complete. You can now start using the project."