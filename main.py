import paramiko
import boto3
from datetime import datetime

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

def upload_to_s3(file_content, bucket_name, file_name):
    s3 = boto3.client('s3')
    s3.put_object(Bucket=bucket_name, Key=file_name, Body=file_content)

def main():
    # List of devices
    devices = [
        Device('cisco_device_ip', 'cisco_username', 'cisco_password', 'show running-config'),
        Device('palo_alto_device_ip', 'palo_alto_username', 'palo_alto_password', 'export config to /path/to/exported/file', '/path/to/exported/file'),
        # Add more devices as needed
    ]

    # AWS S3 details
    bucket_name = 'your_s3_bucket_name'

    # Backup and upload for each device
    for device in devices:
        if device.export_file_path:
            # Handle file export
            local_file_path = f'exported_{device.hostname}_{datetime.now().strftime("%Y%m%d%H%M%S")}.txt'
            device.download_exported_file(local_file_path)
            with open(local_file_path, 'rb') as file:
                upload_to_s3(file.read(), bucket_name, local_file_path)
        else:
            # Handle command output
            backup_content = device.backup()
            file_name = f'backup_{device.hostname}_{datetime.now().strftime("%Y%m%d%H%M%S")}.txt'
            upload_to_s3(backup_content, bucket_name, file_name)

if __name__ == "__main__":
    main()

