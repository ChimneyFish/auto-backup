import paramiko
import boto3
import datetime
import os
import time

# Global SSH credentials
USERNAME = "Username"
PASSWORD = "Password"

# List of devices with custom commands
DEVICES = [
    {"ip": "IP/Hostname", "command": "<Command based on device to pull the backup config>"},
]

# AWS S3 Configuration
S3_BUCKET = "S3 Bucket"
S3_PREFIX = "Folder inside buckert if applicable"
ACCESS_KEY = "your-access-key"
SECRET_KEY = "your-secret-key"

# AWS S3 Client
s3_client = boto3.client(
    "s3",
    aws_access_key_id=ACCESS_KEY,
    aws_secret_access_key=SECRET_KEY
)

# Process Each Device
for device in DEVICES:
    try:
        print(f"\nConnecting to {device['ip']}...")
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(device["ip"], username=USERNAME, password=PASSWORD)

        if "scp" in device["command"]:
            # Handle SCP command via shell
            shell = ssh.invoke_shell()
            shell.send(device["command"] + "\n")
            time.sleep(1)

            buffer = ""
            shell.settimeout(5)
            try:
                while True:
                    resp = shell.recv(1024).decode('utf-8', errors='ignore')
                    buffer += resp
                    if "device_state_cfg.tgz" in resp or "100%" in resp or "Export completed" in resp:
                        break
                    time.sleep(1)
            except Exception as e:
                print(f"SCP shell timeout or complete: {e}")

            ssh.close()
            print(f"SCP Transfer Output for {device['ip']}:\n{buffer}")

            # Rename downloaded file if it exists
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            source_path = "/home/sftpuser/uploads/device_state_cfg.tgz"
            local_filename = f"/home/sftpuser/uploads/{device['ip']}_{timestamp}.tgz"

            if os.path.exists(source_path):
                os.rename(source_path, local_filename)

                # Upload to S3
                s3_client.upload_file(local_filename, S3_BUCKET, f"{S3_PREFIX}/{os.path.basename(local_filename)}")
                print(f"File {local_filename} uploaded successfully to s3://{S3_BUCKET}/{S3_PREFIX}/")
            else:
                print(f"Expected SCP file not found for {device['ip']}")

        else:
            # Handle standard command via exec_command
            stdin, stdout, stderr = ssh.exec_command(device["command"])
            stdout.channel.recv_exit_status()  # Wait for command to finish

            output = stdout.read().decode('utf-8', errors='ignore')
            error_output = stderr.read().decode('utf-8', errors='ignore')
            ssh.close()

            if error_output.strip():
                print(f"Command error from {device['ip']}: {error_output}")

            # Save output to file
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d")
            filename = f"{device['ip']}_{timestamp}.txt"
            with open(filename, "w") as file:
                file.write(output)

            # Upload to S3
            s3_client.upload_file(filename, S3_BUCKET, f"{S3_PREFIX}/{filename}")
            print(f"File {filename} uploaded successfully from {device['ip']} to s3://{S3_BUCKET}/{S3_PREFIX}/{filename}")

    except Exception as e:
        print(f"Error processing {device['ip']}: {e}")
