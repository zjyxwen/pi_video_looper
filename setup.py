from setuptools import setup, find_packages

setup(
    name='pi_video_looper',
    version='2.0.0',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'video_looper = Adafruit_Video_Looper.video_looper:main'
        ]
    }
)

