import paramiko
import boto3
import datetime
import os
import time

# Global SSH credentials
USERNAME = "<>"
PASSWORD = "<>"
SFTP_PASSWORD = "<>"
PA-COMMAND = "scp export device-state to SCP-USER@SCP-IP:SCP-PATH"
CISCO-COMMAND = "show run"
JUNIPER-COMMAND = "<>"
CHECKPOINT-COMMAND ="<>"
FORTINET-COMMAND = "<>"
CUSTOM-COMMAND = "<Fill out in config web gui>" 
SCP-USER = "<self-username>"
SCP-IP = "<self-IP>"
SCP-PATH = <self-path>

# List of devices with custom commands
DEVICES = [
<Auto-Populated from Web GUI Config>
]

# AWS S3 Configuration
S3_BUCKET = "<Bucket_Name>"
S3_PREFIX = "<Folder In bucket>"
ACCESS_KEY = "<Access Key>"
SECRET_KEY = "<Secret Key>"

# AWS S3 Client
s3_client = boto3.client(
    "s3",
    aws_access_key_id=ACCESS_KEY,
    aws_secret_access_key=SECRET_KEY
)

# Process Each Device
for device in DEVICES:
    try:
        print(f"\nConnecting to {device['ip']} ({device['hostname']})...")
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(device["ip"], username=USERNAME, password=PASSWORD)

        timestamp = datetime.datetime.now().strftime("%Y-%m-%d")

        if "scp" in device["command"]:
            # Handle SCP command via shell
            shell = ssh.invoke_shell()
            shell.send(device["command"] + "\n")
            time.sleep(1)

            buffer = ""
            shell.settimeout(10)
            try:
                while True:
                    resp = shell.recv(1024).decode('utf-8', errors='ignore')
                    buffer += resp

                    if "password:" in resp.lower():
                        shell.send(SFTP_PASSWORD + "\n")
                        time.sleep(1)
                        continue

                    if "device_state_cfg.tgz" in resp or "100%" in resp or "Export completed" in resp:
                        break
                    time.sleep(1)
            except Exception as e:
                print(f"SCP shell timeout or complete: {e}")

            ssh.close()
            print(f"SCP Transfer Output for {device['ip']}:\n{buffer}")

            # Rename and upload the SCP file if it exists
            source_path = "/home/jclemmensen/auto-backup/device_state_cfg.tgz"
            local_filename = f"/home/jclemmensen/auto-backup/{device['hostname']}_{timestamp}.tgz"

            if os.path.exists(source_path):
                os.rename(source_path, local_filename)

                s3_client.upload_file(local_filename, S3_BUCKET, f"{S3_PREFIX}/{os.path.basename(local_filename)}")
                print(f"File {local_filename} uploaded successfully to s3://{S3_BUCKET}/{S3_PREFIX}/")

                os.remove(local_filename)
                print(f"Deleted local file: {local_filename}")
            else:
                print(f"Expected SCP file not found for {device['hostname']}")

        else:
            # Standard command execution
            stdin, stdout, stderr = ssh.exec_command(device["command"])
            stdout.channel.recv_exit_status()  # Wait for command to finish

            output = stdout.read().decode('utf-8', errors='ignore')
            error_output = stderr.read().decode('utf-8', errors='ignore')
            ssh.close()

            if error_output.strip():
                print(f"Command error from {device['ip']} ({device['hostname']}): {error_output}")

            filename = f"{device['hostname']}_{timestamp}.txt"
            with open(filename, "w") as file:
                file.write(output)

            s3_client.upload_file(filename, S3_BUCKET, f"{S3_PREFIX}/{filename}")
            print(f"File {filename} uploaded successfully from {device['ip']} to s3://{S3_BUCKET}/{S3_PREFIX}/{filename}")

    except Exception as e:
        print(f"Error processing {device['ip']} ({device['hostname']}): {e}")
