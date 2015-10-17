from setuptools import setup, find_packages

SRC_DIR = 'src'


def get_version():
    import sys

    sys.path[:0] = [SRC_DIR]
    return __import__('mog_commons').__version__


setup(
    name='mog-commons',
    version=get_version(),
    description='Common utility library for Python',
    author='mogproject',
    author_email='mogproj@gmail.com',
    license='Apache 2.0 License',
    url='https://github.com/mogproject/mog-commons-python',
    install_requires=[
        'six',
        'unittest2',
    ],
    tests_require=[
    ],
    package_dir={'': SRC_DIR},
    packages=find_packages(SRC_DIR),
    include_package_data=True,
    test_suite='tests',
)
