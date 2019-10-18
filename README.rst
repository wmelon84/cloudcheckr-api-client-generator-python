.. image:: https://www.python.org/static/img/python-logo.png
  :alt: https://www.python.org/static/img/python-logo.png

CloudCheckr API client generator
================================

This is an unofficial CloudCheckr API client generator implemented in Python based on their own json definition.

Why?
----
There is no official or unofficial API client for CloudCheckr service in any programming language available,
and nowadays with the growth of the IaaS products, the third-party cost explorer services such as CloudCheckr take on importance.

While working directly with CloudCheckr's API I had to implement calls myself in Java,
and discover an endpoint to get the whole API definition, so I came up with the idea of a client generator based on it
so it is not necessary to implement new code to interact with new methods.

How?
----
At the same time, I was attending a Python training so the idea become a pet project to try and learn Python by coding.

What the generator basically does is read json response from https://api.cloudcheckr.com/api/help.json/get_all_api_endpoints?access_key=[access_key]
if an access key is provided as a parameter to the script of from local json if not, and generate Python source code for
actual CloudCheckr API client calls using https://pypi.org/project/requests/.