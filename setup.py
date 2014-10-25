from distutils.core import setup

setup(
    name='pyHueISY',
    version='0.9.0',
    packages=['pyHueISY', 'ISY', 'phue'],
    package_dir={'ISY': 'ISYlib-python/ISY', 'phue': 'phue', 'pyHueISY': 'pyHueISY'},
    include_package_data=True,
    package_data={
        'pyHueISY': [
            'static/*.css',
            'static/*.gif',
            'static/*.js',
            'static/*.png',
            'templates/*.html'
        ]
    },
    data_files=[
        ('var/pyHueISY-instance', ['instance/Readme'])
    ],
    scripts=[
        'pyHueISYServer.py'
    ],
    url='http://github.com/open-sw/pyHueISY',
    license='',
    author='robert',
    author_email='robertn@the-nelsons.org',
    description='Controlling Software for Universal Device\'s ISY 994i and Philips\' Hue',
    install_requires=['flask']
)
