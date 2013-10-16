from distutils.core import setup

setup(
    name='renrenpy',
    version='1.3',
    description='Renren API and OAuth 2 Python SDK',
    long_description=open('README', 'r').read(),
    author='Mozhi Zhang',
    author_email='zhangmozhi@gmail.com',
    url='https://github.com/rellik6/renrenpy',
    download_url='https://github.com/rellik6/renrenpy',
    license='Apache',
    platforms='any',
    py_modules=['renren'],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ]
)
