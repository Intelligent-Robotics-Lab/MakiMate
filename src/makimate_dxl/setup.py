from setuptools import setup

package_name = 'makimate_dxl'

setup(
    name=package_name,
    version='0.0.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='makimate',
    maintainer_email='you@example.com',
    description='Dynamixel control for MakiMate (6 DOF head).',
    license='BSD-3-Clause',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            # name that ros2 run uses  = python_module.python_file:function
            'maki_dxl_6 = makimate_dxl.maki_dxl_6:main',
            'maki_expressions = makimate_dxl.maki_expressions:main',
            'maki_behavior = makimate_dxl.maki_behavior:main',
        ],
    },
)
