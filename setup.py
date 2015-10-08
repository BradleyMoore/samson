from setuptools import setup

setup(name='Samson',
      version='1.0',
      description='Samson Society website',
      author='Bradley Moore',
      author_email='BradleyMooreFTW@gmail.com',
      url='www.samsonsociety.tk',
      install_requires=[
        'Flask>=0.10.1',
        'requests',
        'flask-pymongo',
        'flask-login',
        'flask-wtf'
        ],
     )
