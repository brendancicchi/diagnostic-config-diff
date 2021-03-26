from setuptools import setup

setup(
    name="diagnostic-config-diff",
    version='0.2.1',
    author='Brendan Cicchi',
    description='Diff configuration files across multiple nodes',
    python_requires='>=3.8',
    install_requires=[
        'click==7.0',
        'colorama==0.4.3',
        'packaging==20.1',
        'pyyaml==5.3',
        'requests',
        'sortedcontainers==2.1.0',
        'tqdm==4.42.0'
    ],
    entry_points={
        'console_scripts': [
            'diag-diff = Diag:diagDiff',
            'yaml-diff-default = diff.yaml_diff:yaml_diff_default'
        ]
    }
)