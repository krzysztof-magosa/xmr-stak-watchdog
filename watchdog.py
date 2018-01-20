import urllib2
import yaml
import json
import time
import subprocess


HASHRATE_PERIODS = ["10s", "60s", "15m"]

with open("config.yaml") as handle:
    config = yaml.load(handle)

for miner_name, miner in config["miners"].items():
    if "username" in miner["connection"] and "password" in miner["connection"]:
        auth_handler = urllib2.HTTPBasicAuthHandler()
        auth_handler.add_password(
            realm=miner_name,
            uri=miner["connection"]["url"],
            user=miner["connection"]["username"],
            passwd=miner["connection"]["password"]
        )
        opener = urllib2.build_opener(auth_handler)
        urllib2.install_opener(opener)

while True:
    for miner_name, miner in config["miners"].items():
        api_responded = False
        fail = False

        for x in range(miner["thresholds"]["connect"]["retries"]):
            try:
                url_handle = urllib2.urlopen(
                    miner["connection"]["url"],
                    None,
                    miner["thresholds"]["connect"]["timeout"]
                )
                api_data = json.loads(url_handle.read())
                api_responded = True
                break
            except:
                pass

        if api_responded:
            index = HASHRATE_PERIODS.index(
                miner["thresholds"]["hashrate"]["period"]
            )
            hashrate = int(
                api_data["hashrate"]["total"][index]
            )

            if hashrate < miner["thresholds"]["hashrate"]["value"]:
                fail = True
        else:
            fail = True

        if fail:
            subprocess.call(miner["action"], shell=True)
            time.sleep(int(miner["wait"]))

    time.sleep(5)
