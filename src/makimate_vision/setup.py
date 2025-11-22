from setuptools import find_packages, setup

package_name = 'makimate_vision'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools', 'rclpy', 'sensor_msgs', 'cv_bridge', 'std_msgs'],
    zip_safe=True,
    maintainer='makimate',
    maintainer_email='makimate@todo.todo',
    description='TODO: Package description',
    license='TODO: License declaration',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'face_tracker = makimate_vision.face_tracker_node:main',
            'face_to_maki = makimate_vision.face_to_maki:main',
        ],
    },

)
