from distutils.core import setup

setup(
  name = 'livepng',         
  packages = ['livepng'],   
  version = '0.1.8',      
  license='GGPLv3',        
  description = 'LivePNG is a format to create avatars based on PNG images with lipsync support',
  long_description=open('README.md').read(),
  long_description_content_type='text/markdown',
  author = 'Francesco Caracciolo',
  author_email = 'francescocaracciolo78@gmail.com',
  url = 'https://github.com/francescocaracciolo/livepng',
  download_url = 'https://github.com/FrancescoCaracciolo/LivePNG/archive/refs/tags/0.1.8.tar.gz',
  keywords = ['avatar', 'png', 'lipsync', 'livepng', 'anime'],
  install_requires=[            
          'pydub',
          'pyaudio',
      ],
  classifiers=[
    'Development Status :: 5 - Production/Stable',
    'Intended Audience :: Developers',
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.8',
    'Programming Language :: Python :: 3.9',
    'Programming Language :: Python :: 3.10',
    'Programming Language :: Python :: 3.11',
    'Programming Language :: Python :: 3.12',
  ],
)
