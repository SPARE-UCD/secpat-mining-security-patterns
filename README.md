# SecPat: A Tool for Mining Security Patterns from Library Usages in Software Projects

## Quick Start

### Prerequisites
1. Tidelift Account and create API Token: To access the Tidelift (now Sonar) LibrariesIO API, you need to create an account on [Tidelift](https://tidelift.com/). Sign up for a free account if you don't have one already. After creating an account, navigate to your account settings to generate an API token. This token will be used to authenticate your requests to the LibrariesIO APIs.
2. Github PAT token: For working with GitCrawler submodule, you need to create a Personal Access Token (PAT) on GitHub. Follow these steps to create a PAT:
   - Go to your GitHub account settings.
   - Navigate to "Developer settings" > "Personal access tokens".
   - Click on "Generate new token", provide a name, select the necessary scopes (e.g., `repo`, `read:org`), and generate the token.
   - Copy the generated token and store it securely, as you will need it to authenticate API requests made by the GitCrawler submodule.
3. Docker and Docker Compose: Make sure you have [Docker engine](https://docs.docker.com/engine/) and [Docker Compose](https://docs.docker.com/compose/install/) installed to run independent submodules from SecPat successfully, including Zoekt for code search.

### Installation
To install SecPat, clone the repository and its submodule Zoekt:

```bash
git clone https://github.com/SPARE-UCD/secpat-mining-security-patterns.git
git submodule update --init --recursive
```
Navigate then to the project directory and create a `.env` file based on the provided `.env.example` file:
```bash 
cd secpat-mining-security-patterns
touch .env
cp .env.example .env
```
Put your newly created Tidelift API token in the environment variable `LIBRARIES_IO_API_KEY` in the `.env` file. Also, add your GitHub username and PAT's token in the `GIT_USERNAME` and `GIT_PASSWORD` fields, respectively.
```bash
LIBRARIES_IO_API_KEY=your_libraries_io_api_key_here
GIT_USERNAME=your_git_username_here
GIT_PASSWORD=your_git_password_here
```

### Running and building SecPat
0.
1. The first step to run SecPat is to mine the mutual dependencies metadata from Tidelift (now Sonar) LibrariesIO [API](https://libraries.io/api#project-dependents-repositories). 
```bash
docker compose up --build --force-recreate security_pattern_miner
```