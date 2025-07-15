# llog

`llog` is a simple command-line logging tool that lets you quickly jot down notes, thoughts, or logs, and later summarize them using OpenAI's API.

## Features

- Quickly log messages from the terminal
- Summarize your logs for a given day
- Stores logs locally in `~/.llog/logs`
- Simple setup and usage

## Setup

1. **Clone the repository** (if you haven't already):

   ```bash
   git clone <repo-url>
   cd <repo-directory>
   ```

2. **Run the setup script** to create a Python virtual environment, install dependencies, and set up the executable:

   ```bash
   ./setup.sh
   ```

3. **Set your OpenAI API key**  
   The summarization feature uses the OpenAI API. You need to set your API key as an environment variable.  
   Add the following line to your shell configuration file (e.g., `~/.bashrc`, `~/.zshrc`, etc.):

   ```bash
   export OPENAI_API_KEY=your_openai_api_key_here
   ```

   Then reload your shell configuration:

   ```bash
   source ~/.bashrc   # or source ~/.zshrc
   ```

## Usage

- **Log a message:**

  ```bash
  llog "This is my log message"
  ```

- **Summarize today's logs:**

  ```bash
  llog --summarize today
  ```

- **See all options:**

  ```bash
  llog --help
  ```

## Notes

- Logs are stored in `~/.llog/logs`.
- Make sure your OpenAI API key is set in your environment for summarization to work.

## License

MIT License
