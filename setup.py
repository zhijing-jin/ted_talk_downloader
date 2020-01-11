from setuptools import setup, find_packages

with open('README.md') as f:
    long_description = f.read()

setup(
    name='ted_talk_downloader',
    version='0.1',
    packages=find_packages(exclude=['tests*']),
    package_dir={'mypkg': 'ted_talk_downloader'},
    package_data={'mypkg': ['data/*.json']},
    license='MIT',
    description='A package to easily download TED talk transcripts',
    long_description=long_description,
    long_description_content_type='text/markdown',
    install_requires=['bs4', 'lxml', 'tqdm', 'efficiency'],
    url='https://github.com/zhijing-jin/ted_talk_downloader',
    author='Zhijing Jin',
    author_email='zhijing.jin@connect.hku.hk'
)
