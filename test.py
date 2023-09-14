import subprocess

def main():

    out = subprocess.run("pwd",capture_output=True, text = True)
    print("im operating from directory path: +",out.stdout.strip())
    
    try:
        #result = subprocess.run(cmd, capture_output=True, text=True, check=True, shell = True)
        link = subprocess.run("python3 /Users/khawar/demoWebsite/drive_upload.py /Users/khawar/demoWebsite/test.txt", shell = True)
    except subprocess.CalledProcessError as e:
        print("Command returned non-zero exit status:", e.returncode)

if __name__ == "__main__":
    main()