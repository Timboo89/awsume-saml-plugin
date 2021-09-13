from setuptools import setup

setup(
    name='awsume-saml-plugin',
    version='0.1.0',
    entry_points={
        'awsume': [
            'saml = saml'
        ]
    },
    author='Timo Schmidt',
    author_email='bsc.timo.schmitd@gmail.com',
    py_modules=['saml'],
)