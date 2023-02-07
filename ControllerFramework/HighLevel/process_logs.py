import os

def delete_logs():
    os.system("rm -r ./Logs/*")

if __name__ == "__main__":
    delete_logs()