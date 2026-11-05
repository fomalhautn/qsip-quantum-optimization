# Optional IQM hardware execution in VS Code

The notebooks run in Binder without credentials. For real IQM hardware, use the **same notebook locally**.

1. Extract `downloads/QSIP-local-starter.zip` on your computer and open the folder in VS Code. Install the Microsoft Python and Jupyter extensions.
2. In a Python 3.11 or 3.12 environment, install `python -m pip install -r requirements-hardware.txt`.
3. Open a challenge notebook, select its Python environment as the kernel and run the simulator cells first.
4. In the final hardware section, set `RUN_ON_IQM = True`, choose your authorized processor (`garnet`, for example), and enter your personal IQM token via the hidden prompt.
5. Inspect transpilation. Set `CONFIRM_QPU_SUBMISSION = True` only when ready to submit a potentially billable QPU job.

Never enter personal API tokens in public Binder, code cells or Git commits. Hardware connectivity, entitlements and charges depend on your IQM account.
