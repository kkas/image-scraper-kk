import re
import requests
import json
import sys

from bs4 import BeautifulSoup

from flask import Flask, request, jsonify
app = Flask(__name__)


INSTAGRAM_URL_PREFIX = r'^https://www.instagram.com.*$'
SITE_INSTAGRAM = 'INSTAGRAM'


@app.route('/')
def hello():
    return 'hello'


@app.route('/instagram/url', methods=['POST'])
def instagram():
    """
    Retrieve the main picture from the url posted.
    The posted data must be in JSON format and contain "url".
        ex.
            {"url" : "https://www.instagram.com/p/FNfeaionfead/"}
    """
    # Ignore the content type. The request should contain application/json.
    json_obj = request.get_json(force=True)
    target_url = json_obj['url']

    # Check if the url is for instagram.
    if not is_instagram_url(target_url):
        return jsonify(original_url=target_url,
                       url=None,
                       status='FAILED')

    # Retrieve the contents by making GET request to the URL.
    content = do_get(target_url)

    # Parse the content and extract the json part.
    json_obj = extract_json_part(content)

    # Retrieve the image resources.
    image_resources = extract_image_resources(json_obj)

    print("image_resources(before): {}".format(image_resources), file=sys.stderr)

    # Modify the url to avoid Instagram's "URL signature expired" problem.
    # See the following post for more details.
    # https://stackoverflow.com/questions/47668014/instagram-feed-api-media-url-shows-url-signature-expired
    image_resources = make_permanent_urls(image_resources)

    print("image_resources(after): {}".format(image_resources), file=sys.stderr)

    return jsonify(original_url=target_url,
                   image_resources=image_resources,
                   status='SUCCESS')


def do_get(url):
    """Make a GET request to the url."""
    return requests.get(url).text


def make_permanent_urls(image_resources):
    for resource in image_resources:
        resource['src'] = make_permanent_url(resource['src'])
    return image_resources


def make_permanent_url(url):
    """Modify the original url of a picture on Instagram to avoid the 'URL signature expired' problem. """
    return re.sub(r'/vp.*\/.{32}\/.{8}\/', '/', url)


def extract_image_resources(json_obj):
    return json_obj['entry_data']['PostPage'][0]['graphql']['shortcode_media']['display_resources']


def is_instagram_url(url):
    return re.match(INSTAGRAM_URL_PREFIX, url)


def extract_json_part(content):
    soup = BeautifulSoup(content, "html.parser")

    # The Json part is embedded inside of the <script> tag.
    # The script declares a variable, '_sharedData' and sets the json data for it.
    script_text = soup.find('script', type='text/javascript', string=re.compile('_sharedData')).string

    # Remove any unnecessary parts and extract only the json part.
    json_text = re.sub(r'(?:window._sharedData = |;$)', "", script_text)

    return json.loads(json_text)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
