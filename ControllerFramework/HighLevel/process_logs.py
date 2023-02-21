import os

def delete_logs():
    os.system("rm -r ./Logs/*")

def parse_colors():
    pass

if __name__ == "__main__":
    delete_logs()