from setuptools import setup, find_packages

setup(
    name="gdc-maf-tool",
    version='0.0.1',
    description="GDC MAF Tool",
    license="Apache",
    packages=find_packages(),
    entry_points={
        'console_scripts': ['gdc-maf-tool=gdc_maf_tool.__main__:main']
    },
)
