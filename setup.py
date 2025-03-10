from setuptools import setup, find_packages

setup(
    name='crypto-quant-trading',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[
        'requests>=2.28.0',
        'pandas>=1.5.0',
        'numpy>=1.23.0',
        'matplotlib>=3.5.0',
        'seaborn>=0.12.0',
        'scikit-learn>=1.1.0',
        'pytest>=7.0.0',
        'python-dotenv>=0.20.0',
        'ccxt>=2.0.0',
        'ta>=0.10.0',
    ],
    author='Devin AI',
    author_email='devin-ai-integration[bot]@users.noreply.github.com',
    description='A multi-factor quantitative trading strategy for crypto markets',
)

