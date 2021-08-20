from setuptools import setup, find_packages
import pathlib


here = pathlib.Path(__file__).parent.resolve()
long_description = (here / 'README.md').read_text(encoding='utf-8')
setup(
    name='pychology',
    version='0.1a0',
    description='Game AI algorithms in pure Python',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/TheCheapestPixels/pychology',
    author='TheCheapestPixels',
    author_email='TheCheapestPixels@gmail.com',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
    ],
    keywords='behavior tree',
    packages=find_packages(exclude=['tests', 'examples']),
    python_requires='>=3.6, <4',
    install_requires=[],
    project_urls={
        'Source': 'https://github.com/TheCheapestPixels/pychology',
    },
)
