#! /usr/bin/env python
# -*- coding: utf-8 -*-

import setuptools

long_description = open('README.rst', 'rb').read().decode('utf-8')

install_requires = ["requests<=2.22.0"]

setuptools.setup(
    name="cloudcheckr-api-client-generator-python",
    version="1.0.0",
    url="https://github.com/wmelon84/cloudcheckr-api-client-generator-python",
    download_url="https://github.com/wmelon84/cloudcheckr-api-client-generator-python.git",
    author="wmelon84",
    author_email="wmelon84@gmail.com",
    description="Dynamic CloudCheckr API client generator in Python",
    packages=[],
    install_requires=install_requires,
    license='MIT License',
    include_package_data=True,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.7',
    ],
)
