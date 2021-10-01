import speedtest


def check_speed():
    servers = []
    # If you want to test against a specific server
    # servers = [1234]

    threads = None
    # If you want to use a single threaded test
    # threads = 1

    s = speedtest.Speedtest()
    s.get_servers(servers)
    s.get_best_server()
    s.download(threads=threads)
    s.upload(threads=threads)
    s.results.share()

    return s.results.dict()


def get_speed():
    msg = ""
    speed = check_speed()
    up_mbps = speed['upload'] / 1000000
    down_mbps = speed['download'] / 1000000
    msg += "Humans are so competitive."
    msg += "```"
    msg += f"Download: {down_mbps:.2f} Mbps\n" \
           f"Upload: {up_mbps:.2f} Mbps\n" \
           f"Ping: {speed['ping']}\n" \
           f"```\n" \
           f"{speed['share']}"
    return msg


if __name__ == '__main__':
    print(get_speed())
