# coding: utf-8
# 爬取leetcode刷题记录

import os
import json
import requests
import time


def parse_submissions(leetcode_session):
    url = "https://leetcode-cn.com/api/submissions/"
    headers = {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "accept-language": "zh,en;q=0.9,zh-CN;q=0.8",
        "cache-control": "max-age=0",
        "sec-ch-ua": "\" Not A;Brand\";v=\"99\", \"Chromium\";v=\"101\", \"Google Chrome\";v=\"101\"",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "\"macOS\"",
        "sec-fetch-dest": "document",
        "sec-fetch-mode": "navigate",
        "sec-fetch-site": "none",
        "sec-fetch-user": "?1",
        "upgrade-insecure-requests": "1",
        "cookie": f"LEETCODE_SESSION={leetcode_session}",
    }
    limit, offset = 100, 0
    submissions = []
    with requests.Session() as session:
        while True:
            resp = session.get(url, headers=headers, params={'limit': limit, 'offset': offset})
            if resp.status_code != 200:
                print(f"Get submissions from leetcode-cn failed: {resp.content.decode()}")
                break
            data = resp.json()
            submissions += data['submissions_dump']
            if not data['has_next']:
                print("Finished requests")
                break
            offset += limit
            print(f"parsing next, offset = {offset}")
            time.sleep(1)

    if not submissions:
        print("no submissions to dump to file.")
        return
    # filter submissions
    _submissions = []
    exists = set()
    for sub in submissions:
        key = (sub['title'], sub['lang'])
        if sub['status_display'] != 'Accepted' or key in exists:
            continue
        exists.add(key)
        _submissions.append(sub)
    print(f"All done, total {len(submissions)} submissions fetched.")
    # output data to json
    with open('leetcode-submissions.json', 'w') as f:
        json.dump(_submissions, f)


def main():
    leetcode_session = os.environ.get("LEETCODE_SESSION")
    if not leetcode_session:
        print("leetcode session not set.")
        return
    parse_submissions(leetcode_session)
    

if __name__ == '__main__':
    main()
