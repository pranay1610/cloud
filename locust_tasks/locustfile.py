import os
import random
from locust import HttpUser, task, between
from requests.auth import HTTPBasicAuth
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NextcloudUser(HttpUser):
    auth = None
    user_name = None
    wait_time = between(2, 5)
    current_task = "1KB"

    def on_start(self):
        user_idx = random.randrange(0, 30)
        self.user_name = f'locust_user{user_idx}'
        self.auth = HTTPBasicAuth(self.user_name, 'test_password1234!')
        logger.info(f"Starting test for {self.user_name}")

    @task
    def test_files(self):
        if self.current_task == "1KB":
            self.run_test("1KB", "test_file_1024B")
            self.current_task = "1MB"
        elif self.current_task == "1MB":
            self.run_test("1MB", "test_file_1048576B")
            self.current_task = "1GB"
        elif self.current_task == "1GB":
            self.run_test("1GB", "test_file_1073741824B")
            self.current_task = "DONE"
        else:
            self.environment.runner.quit()  # Stop the test once all tasks are done

    def run_test(self, size, filename):
        remote_path = f"/remote.php/dav/files/{self.user_name}/{size}_file_{random.randrange(0, 10)}"
        
        # Upload file
        try:
            with open(f"/test_data/{filename}", "rb") as file:
                logger.info(f"Uploading {size} file to {remote_path}")
                r = self.client.put(remote_path, data=file, auth=self.auth)
                r.raise_for_status()
                logger.info(f"Upload {size} file {self.user_name} - Status: {r.status_code}")
        except Exception as e:
            logger.error(f"Upload {size} file {self.user_name} failed: {e}")
            return
        
        # Read file
        try:
            logger.info(f"Reading {size} file from {remote_path}")
            r = self.client.get(remote_path, auth=self.auth)
            r.raise_for_status()
            logger.info(f"Read {size} file {self.user_name} - Status: {r.status_code}")
        except Exception as e:
            logger.error(f"Read {size} file {self.user_name} failed: {e}")
        
        # Delete file
        try:
            logger.info(f"Deleting {size} file from {remote_path}")
            r = self.client.delete(remote_path, auth=self.auth)
            r.raise_for_status()
            logger.info(f"Deleted {size} file {self.user_name} - Status: {r.status_code}")
        except Exception as e:
            logger.error(f"Delete {size} file {self.user_name} failed: {e}")
        
        # Sleep to ensure sequential execution
        self.wait()
