### Install New Environment
To install a new Anaconda environment, open Terminal and run:\
`bash "new_env.sh"`\
If using windows, open git bash and run the above line.

* To create a new environment without the default packages set by the `.condarc` file, run:\
`conda create --name <env_name> --no-default-packages`

* To remove the environment, run:\
`conda remove --name <env_name> --all`

Then, restart PyCharm and change the PyCharm Python interpreter in Settings > Project > 
Python Interpreter > Add Interpreter > Conda Environment > Use Existing Environment > "MYENV" > Apply.

### pip
Get version requirements from `pip_requirements_in.txt` and save them to `pip_requirements.txt` using pip-tools:\
`pip-compile pip_requirements_in.txt --max-rounds 100 --output-file pip_requirements.txt`

Create a new virtual environment:\
`python -m venv "myvenv"`

Activate the virtual environment:\
`source "myvenv/bin/activate"` (Linux/Mac)\
`"myvenv\Scripts\activate.bat"` (Windows)


To install using pip, run:\
`pip install -r "pip_requirements.txt" -U --progress-bar on`


To save the `requirements` file, run:\
`pip freeze => "pip_requirements.txt"`

### Free up space
To clear the cache, run:\
`conda clean --all -y`\
`pip cache purge`

To roll back an environment to its initial state, run:\
`conda install --rev 0`