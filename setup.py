import setuptools

with open("README.md","r") as file:
    read_me = file.read()

setuptools.setup(
    name="ccbhc_measurements",
    version="2025.2.12",
    description="An easy way to calculate CCBHC measurements.",
    long_description=read_me,
    long_description_content_type="text/markdown",
    # url="github",
    author="Pesach Tikvah Doors of Hope Data Analytics",
    author_email="agursky@pesachtikvah.org",
    # license="",
    # project_urls={
        # "Source" : "github"
    # },
    classifiers=[
        "Intended Audience :: Healthcare Industry",
        "Intended Audience :: Developers",
        # "License :: ",
        "Programming Language :: Python :: 3.12"
    ],
    python_requires=">=3.12",
    install_requires=["pandas>=2.2.2"],
    packages=setuptools.find_packages(),
    include_package_data=True
)