import requests
import random


class RotateUserAgent:
    def __init__(self, useragent_file="../useragent.txt"):
        with open(useragent_file) as f:
            self.useragent_list = []
            for useragent in f.readlines():
                self.useragent_list.append(useragent.replace("\n", ""))

    def get(self):
        return random.choice(self.useragent_list)


class RotateProxy:
    def __init__(self, proxy_file="../iproyal.txt", random=True):
        with open(proxy_file) as f:
            self.proxies_list = []
            for proxy in f.readlines():
                proxy = proxy.replace("\n", "")
                proxy = proxy.split(":")
                proxy = f"http://{proxy[2]}:{proxy[3]}@{proxy[0]}:{proxy[1]}"
                self.proxies_list.append(proxy)
            self.random = random
            self.proxy = 0

    def get(self):
        if self.random:
            return random.choice(self.proxies_list)
        else:
            proxy = self.proxies_list[self.proxy]
            self.proxy += 1
            if self.proxy >= len(self.proxies_list):
                self.proxy = 0
            return proxy


class Proxy:
    def __init__(
        self, proxy_file="iproyal.txt", user_agent_file="useragent.txt", retry=3
    ):
        self.retry = retry
        self.proxy = RotateProxy(proxy_file)
        self.use_agent = RotateUserAgent(user_agent_file)

    def make_request(self, url):
        attempts = 0
        while attempts <= self.retry:
            attempts += 1
            proxies = self.proxy.get_proxy()
            useragent = self.use_agent.get_user_agent()
            headers = {"User-Agent": useragent}
            try:
                response = requests.get(
                    url, headers=headers, proxies=proxies, timeout=10
                )
                print(response.status_code)
                if response.status_code == 200:
                    return response
            except Exception as e:
                print("failed", e)


if __name__ == "__main__":
    proxy = Proxy("10proxies.txt")
    for x in range(5):
        proxy.make_request("https://google.com")
