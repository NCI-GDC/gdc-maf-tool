from setuptools import setup, find_packages
from gdc_maf_tool import __version__

setup(
    name="gdc-maf-tool",
    version=__version__,
    description="GDC MAF Tool",
    license="Apache",
    packages=find_packages(),
    entry_points={"console_scripts": ["gdc-maf-tool=gdc_maf_tool.cli:main"]},
    install_requires=[
        "requests>=2.22.0,<3",
        "defusedcsv>=1.0.0,<2.0.0",
        "cdislogging@git+https://github.com/uc-cdis/cdislogging.git@0.0.2",
        "aliquot_level_maf@git+https://github.com/NCI-GDC/aliquot-level-maf.git@0.2.1",
    ],
)
