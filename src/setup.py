from distutils.core import setup

setup(
  name = 'livepng',         
  packages = ['livepng'],   
  version = '0.1',      
  license='GPL3',        
  description = 'LivePNG is a format to create avatars based on PNG images with lipsync support',
  author = 'Francesco Caracciolo',
  author_email = 'francescocaracciolo78@gmail.com',
  url = 'https://github.com/francescocaracciolo/livepng',
  download_url = 'https://github.com/francescocaracciolo/livepng/archive/.tar.gz',
  keywords = ['avatar', 'png', 'lipsync', 'livepng', 'anime'],
  install_requires=[            
          'pydb',
          'pyaudio',
      ],
  classifiers=[
    'Development Status :: 5 - Production/Stable',
    'Intended Audience :: Developers',
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: GPL3 License',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.7',
    'Programming Language :: Python :: 3.8',
    'Programming Language :: Python :: 3.9',
    'Programming Language :: Python :: 3.10',
    'Programming Language :: Python :: 3.11',
    'Programming Language :: Python :: 3.12',
  ],
)