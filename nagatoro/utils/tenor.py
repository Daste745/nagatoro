import requests
from json import loads


def get_gif(query: str, api_key: str) -> str:
    action = f"anime {query}".replace(" ", "+")
    request_url = f"https://api.tenor.com/v1/random?" \
                  f"q={action}&key={api_key}&limit=1&media_filter=basic" \
                  f"&contentfilter=low"
    response = requests.get(request_url)

    return loads(response.content)["results"][0]["media"][0]["gif"]["url"]
