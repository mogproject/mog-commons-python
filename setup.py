from setuptools import setup, find_packages

SRC_DIR = 'src'


def get_version():
    import sys

    sys.path[:0] = [SRC_DIR]
    return __import__('mog_commons').__version__


def get_additional_dependencies():
    import sys

    ret = []
    if sys.version_info < (2, 7):
        ret.append('unittest2')
    if (3, ) <= sys.version_info < (3, 3):
        ret.append('jinja2 == 2.6')  # specify library version to support Python 3.2
    else:
        ret.append('jinja2')
    return ret


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
    ] + get_additional_dependencies(),
    tests_require=[
    ],
    package_dir={'': SRC_DIR},
    packages=find_packages(SRC_DIR),
    include_package_data=True,
    test_suite='tests',
)
