import os
import sys

# Calculate the path to the projects root directory
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# Add the app/ directory to the Python path
app_path = os.path.join(project_root, "app")
sys.path.insert(0, app_path)

# set the environment to test
os.environ["ENVIRONMENT"] = "test"
