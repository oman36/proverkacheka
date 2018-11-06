from setuptools import setup

setup(name='proverkacheka',
    version='0.1.1',
    description='Api for proverkacheka.nalog.ru',
    url='https://github.com/oman36/proverkacheka',
    author='Petrov Vladimir',
    author_email='neoman36@gmail.com',
    license='MIT',
    packages=['proverkacheka'],
    install_requires=[
        'requests==2.20.0',
    ],
    zip_safe=False)