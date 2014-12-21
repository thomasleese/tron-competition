import time

def log(colour, tag, *msg):
    timestamp = "[" + time.strftime("%H:%M:%S") + "]"
    
    msg = " ".join([ str(m) for m in msg ])
    gap = " ".join([ "" for x in range(22 - len(timestamp) - len(tag)) ])
    print(colour + timestamp + " " + tag + "\033[0m" + gap + msg)

def purple(tag, *msg):
    log("\033[95m", tag, *msg)

def blue(tag, *msg):
    log("\033[94m", tag, *msg)

def green(tag, *msg):
    log("\033[92m", tag, *msg)

def yellow(tag, *msg):
    log("\033[93m", tag, *msg)

def red(tag, *msg):
    log("\033[91m", tag, *msg)
