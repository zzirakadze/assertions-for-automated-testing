from setuptools import setup


def readme():
    with open("README.md") as f:
        return f.read()


setup(
    name="python assertions",
    version="0.0.1",
    description="Foo demo project the II",
    long_description=readme(),
    long_description_content_type="text/markdown",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.9",
        "Operating System :: OS Independent",
    ],
    url="https://github.com/zzirakadze/assertions-for-automated-testing.git",
    author="Zura Zirakadze",
    author_email="zirakadzez@gmail.com",
    keywords="assertions, python",
    license="MIT",
    packages=['zzassertions'],
    install_requires=[],
    include_package_data=True,
)
