
# Contributing to Request Logger

Thank you for considering contributing to the Request Logger project! Your contributions help make this project better.

## How Can You Contribute?

- **Report Bugs**: If you find a bug, please report it by opening an issue.
- **Suggest Features**: Have an idea for a new feature? We'd love to hear it.
- **Submit Pull Requests**: Fix bugs, add new features, improve documentation.
- **Improve Documentation**: Corrections, clarifications, and expansions are all welcome.
- **Write Tests**: Help improve the reliability of the project by writing tests.

## Getting Started

### 1. Fork the Repository

Create your own fork of the project by clicking the "Fork" button on GitHub.

### 2. Clone Your Fork

```bash
git clone https://github.com/ashishsubedi/request-logger.git
cd request-logger

3. Set Up the Development Environment

Create a virtual environment and install the necessary dependencies.

python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
pip install -e .

4. Create a New Branch

Always create a new branch for your work.

git checkout -b feature/your-feature-name

5. Make Your Changes

Edit the code, add new files, and make sure your changes align with the project's coding standards.
6. Write Tests

Ensure that your changes are covered by tests. Add new tests to the tests/ directory.
7. Run Tests

Run the test suite to make sure all tests pass.

pytest tests/

8. Commit Your Changes

Write clear and descriptive commit messages.

git add .
git commit -m "Add feature X to improve Y"

9. Push to Your Fork

git push origin feature/your-feature-name

10. Open a Pull Request

Go to the original repository and open a pull request from your fork.
Guidelines
Code Style

    Follow PEP 8 for Python code.
    Use meaningful variable and function names.
    Keep functions and methods small and focused.
    Write docstrings for public modules, classes, functions, and methods.

Testing

    Use pytest for writing tests.
    Place tests in the appropriate files in the tests/ directory.
    Write tests that cover various cases, including edge cases.

Documentation

    Update the README.md if your changes affect how users interact with the project.
    Add or update docstrings in the code where appropriate.

Commit Messages

    Use the present tense ("Add feature" not "Added feature").
    Use the imperative mood ("Move cursor to..." not "Moves cursor to...").
    Provide a clear and concise description of the changes.

Pull Request Process

    Ensure that your pull request includes a description of the changes and the motivation behind them.
    Reference any relevant issues using keywords (e.g., "Closes #123").
    Be responsive to feedback; you may be asked to make changes.

Code of Conduct

By participating in this project, you agree to abide by the Contributor Covenant Code of Conduct.
Contact

If you have any questions or need assistance, feel free to open an issue or reach out to the maintainers.

---

Feel free to customize these documents according to your project's specific details and needs. Let me know if you need any further assistance or modifications!