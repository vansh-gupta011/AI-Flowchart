# run_api.py
import os
import subprocess

def main():
    print("Starting FastAPI server...")
    subprocess.run(["uvicorn", "api:app", "--reload", "--host", "0.0.0.0", "--port", "8000"])

if __name__ == "__main__":
    main()

# -------------------------------------------

# run_streamlit.py
import os
import subprocess

def main():
    print("Starting Streamlit app...")
    subprocess.run(["streamlit", "run", "app.py"])

if __name__ == "__main__":
    main()
