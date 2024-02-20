from setuptools import setup, find_packages

setup(
    name='keep_in_touch',
    version='0.1.1',
    description='Project of the development team "AngryRaccoons", project - "Keep In Touch"',
    author='Project_group_14 "AngryRaccoons"',
    license='MIT',
    packages=find_packages(),
    entry_points={
        'console_scripts':['keep_in_touch=keep_in_touch.main:main']
    },
    
    install_requires=['prompt_toolkit']    
)

