import setuptools

with open("README.md","r") as file:
    read_me = file.read()

setuptools.setup(
    name="ccbhc_measurements",
    version="2025.6.1",
    description="An easy way to calculate CCBHC measurements.",
    long_description=read_me,
    long_description_content_type="text/markdown",
    url="https://github.com/Pesach-Tikvah-Hope-Development-Inc/CCBHC_Measurements",
    author="Pesach Tikvah Hope Development Inc.",
    author_email="agursky@pesachtikvah.org",
    maintainer="Alex Gursky, Max Friedman, Yisroel Len",
    maintainer_email="agursky@pesachtikvah.org, mfriedman@pesachtikvah.org, ylen@pesachtikvah.org",
    license="CC BY-NC-SA 4.0",
    project_urls={
        "Source" : "https://github.com/Pesach-Tikvah-Hope-Development-Inc/CCBHC_Measurements"
    },
    classifiers=[
        "Intended Audience :: Healthcare Industry",
        "Intended Audience :: Developers",
        "License :: Free for non-commercial use",
        "Programming Language :: Python :: 3.12"
    ],
    python_requires=">=3.12",
    install_requires=["pandas>=2.2.2","tzdata>=2022.7"],
    packages=setuptools.find_packages(),
    include_package_data=True
)