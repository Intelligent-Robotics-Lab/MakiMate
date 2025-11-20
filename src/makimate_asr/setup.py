from setuptools import setup

package_name = 'makimate_asr'

setup(
    name=package_name,
    version='0.0.1',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages',
         ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Bao',
    maintainer_email='you@example.com',
    description='ASR nodes for MakiMate using ReSpeaker USB Mic Array and Vosk.',
    license='MIT',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'respeaker_vosk_asr = makimate_asr.respeaker_vosk_asr:main',
            'simple_tts_node = makimate_asr.simple_tts_node:main',
            'asr_led_node = makimate_asr.asr_led_node:main',
            'asr_command_router = makimate_asr.asr_command_router:main',
        ],
    },



)
