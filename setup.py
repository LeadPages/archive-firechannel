from setuptools import setup

with open("firechannel/__init__.py", "r") as f:
    version_marker = "__version__ = "
    for line in f:
        if line.startswith(version_marker):
            _, version = line.split(version_marker)
            version = version.strip().strip('"')
            break
    else:
        raise RuntimeError("Version marker not found.")


def parse_dependencies(filename):
    with open(filename) as reqs:
        for line in reqs:
            if line.startswith("#"):
                continue

            yield line.strip()


dependencies = list(parse_dependencies("requirements.txt"))

setup(
    name="firechannel",
    description="An almost-dropin replacement for the GAE channels API using Firebase.",
    long_description="""For documentation and usage examples, see the project on GitHub_.

    .. _GitHub: https://github.com/leadpages/firechannel""",
    version=version,
    url="https://github.com/leadpages/firechannel",
    author="Leadpages",
    author_email="opensource@leadpages.net",
    license="MIT",
    packages=["firechannel"],
    install_requires=dependencies,
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
    ]
)
