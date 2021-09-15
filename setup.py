import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name='awsume-saml-plugin',
    version='0.1.0',
    entry_points={
        'awsume': [
            'saml = saml'
        ]
    },
    author='Timo Schmidt',
    author_email='bsc.timo.schmidt@gmail.com',
    py_modules=['saml'],
    description='Plugin for awsume assuming AWS roles with SAML federation.',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Timboo89/awsume-saml-plugin",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache License 2.0",
        "Operating System :: OS Independent",
    ],
)