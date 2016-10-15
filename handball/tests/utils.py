# coding: utf-8
import json
import os

from scrapy.http import HtmlResponse, Request


def fake_response_from_file(file_name, url=None):
    """
    Create a Scrapy fake HTTP response from a HTML file
    @param file_name: The relative filename from the responses directory,
                      but absolute paths are also accepted.
    @param url: The URL of the response.
    returns: A scrapy HTTP response which can be used for unittesting.

    From Stackoverflow: http://stackoverflow.com/a/12741030/277015
    """
    if not url:
        url = 'http://www.example.com'

    request = Request(url=url)
    if not file_name[0] == '/':
        test_dir = os.path.dirname(os.path.realpath(__file__))
        file_path = os.path.join(test_dir, file_name)
    else:
        file_path = file_name

    file_content = open(file_path, 'r').read()

    response = HtmlResponse(
        url=url,
        request=request,
        body=file_content,
        encoding='iso-8859-1')
    return response


def json_fixture(filename):
    """
    A helper function to load a json fixture from our fixture directory. Placed
    here to keep the test methods cleaner.
    """
    fixture_path = os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        "fixtures")
    return json.load(open(os.path.join(fixture_path, filename), "r"))
