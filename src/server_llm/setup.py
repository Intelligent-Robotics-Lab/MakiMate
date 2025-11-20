from setuptools import setup

package_name = 'server_llm'

setup(
    name=package_name,
    version='0.0.1',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages',
         ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/launch', ['launch/llm_bridge.launch.py']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='MakiMate',
    maintainer_email='you@example.com',
    description='ROS2 node that bridges prompts to an external LLM HTTP server and streams tokens back.',
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'llm_bridge = server_llm.llm_bridge_node:main',
            'llm_say = server_llm.say:main',
            'llm_tty = server_llm.tty:main',   # <--- add this line
        ],
    },

)
