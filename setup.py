from distutils.core import setup

setup(
    name='pyHueISY',
    version='0.9.0',
    packages=['pyHueISY', 'pyHueISY.ISY', 'pyHueISY.phue'],
    package_dir={'pyHueISY.ISY': 'ISYlib-python/ISY', 'pyHueISY.phue': 'phue'},
    url='',
    license='',
    author='robert',
    author_email='',
    description=''
)
