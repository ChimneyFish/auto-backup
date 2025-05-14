import paramiko
import boto3
from datetime import datetime
import socket

class Device:
    def __init__(self, hostname, username, password, command, export_file_path=None):
        self.hostname = hostname
        self.username = username
        self.password = password
        self.command = command
        self.export_file_path = export_file_path

    def backup(self):
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(self.hostname, username=self.username, password=self.password)
        stdin, stdout, stderr = ssh.exec_command(self.command)
        output = stdout.read().decode()
        ssh.close()
        return output

    def download_exported_file(self, local_path):
        if not self.export_file_path:
            raise ValueError("Export file path not specified for this device.")

        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(self.hostname, username=self.username, password=self.password)
        
        sftp = ssh.open_sftp()
        sftp.get(self.export_file_path, local_path)
        sftp.close()
        ssh.close()

def upload_to_s3(file_content, bucket_name, file_name, access_key, secret_key):
    s3 = boto3.client('s3', aws_access_key_id=access_key, aws_secret_access_key=secret_key)
    s3.put_object(Bucket=bucket_name, Key=file_name, Body=file_content)

def main():
    # Get the local machine's IP address
    local_ip = socket.gethostbyname(socket.gethostname())

    # Cisco device details
    cisco_device = Device(
        hostname='192.168.15.253',
        username='jimbo13',
        password='makoma13',
        command='show running-config'
    )
 
    # Palo Alto device details
    palo_alto_device = Device(
        hostname='192.168.15.65',
        username='jcakmehoff',
        password='makoma13',
        command=f'scp export device-state to sftpuser@{local_ip}:/home/sftpuser/uploads',  # Adjust the local path as needed
        export_file_path='/home/sftpuser/uploads'  # Local path where the file will be saved
    )
    # Add Wireless
    WLC_device = Device(
        hostname='192.168.15.200', 
        username='admin',
        password='admin',
        command='debug' \
        'save-config sftp://jackmehoff:makoma13@192.168.15.19/WLC_config.txt',
        export_file_path='/home/sftpuser/uploads'  # Local path where the file will be saved
    )
    # Add more devices as needed
    # AWS S3 details
    bucket_name = 'thissucksyoufuckingfagot'
    access_key = 'AKIA5OD3AFMLPSYFWS67'
    secret_key = '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'
    s3_uri = 's3://thissucksyoufuckingfagot/Backups/'

    # Backup and upload for each device
    devices = [cisco_device, palo_alto_device, WLC_device]
    for device in devices:
        if device.export_file_path:
            # Handle file export
            local_file_path = f'exported_{device.hostname}_{datetime.now().strftime("%Y%m%d%H%M%S")}.txt'
            device.download_exported_file(local_file_path)
            with open(local_file_path, 'rb') as file:
                upload_to_s3(file.read(), bucket_name, local_file_path, access_key, secret_key)
        else:
            # Handle command output
            backup_content = device.backup()
            file_name = f'Backups/backup_{device.hostname}_{datetime.now().strftime("%Y%m%d%H%M%S")}.txt'
            upload_to_s3(backup_content, bucket_name, file_name, access_key, secret_key)

if __name__ == "__main__":
    main()
