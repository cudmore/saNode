from setuptools import setup, find_packages

exec (open('sanode/version.py').read())

setup(
    name='sanode',
    version=__version__,
    description='Image volume and time series analysis',
    url='http://github.com/cudmore/saNode',
    author='Robert H Cudmore',
    author_email='robert.cudmore@gmail.com',
    license='GNU GPLv3',
    #packages = find_packages(),
    #packages = find_packages(exclude=['version']),
    #packages=[
    #    'pymapmanager',
    #    'pymapmanager.mmio'
    #],
    setup_requires=[
        #"numpy>1.18",
        'pyqt5',
    ],
    install_requires=[
        'pandas',
        'napari',
        'pyqt5',
        'tifffile',
		'matplotlib',
    ]
)
