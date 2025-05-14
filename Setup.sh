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
# Install SFTP enable and configure it as needed to RUN   
sudo apt-get install openssh-server
sudo systemctl start ssh
sudo systemctl enable ssh
sudo tee -a /etc/ssh/sshd_config <<EOF
# Subsystem for SFTP
Subsystem sftp internal-sftp

# Create a group for SFTP users
Match Group sftpusers
    ChrootDirectory /home/%u
    ForceCommand internal-sftp
    AllowTcpForwarding no
EOF

sudo systemctl restart ssh
sudo groupadd sftpusers
sudo adduser sftpuser
sudo usermod -aG sftpusers sftpuser
sudo mkdir /home/sftpuser
sudo chown root:root /home/sftpuser
sudo chmod 755 /home/sftpuser
sudo mkdir /home/sftpuser/uploads
sudo chown sftpuser:sftpusers /home/sftpuser/uploads
sudo systemctl restart ssh
sudo ufw allow OpenSSH
sudo firewall-cmd --zone=public --add-service=ssh --permanent
sudo firewall-cmd --reload
