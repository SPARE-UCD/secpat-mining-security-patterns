# SecPat: A Tool for Mining Security Patterns from Library Usages in Software Projects

This repository contains SecPat, a tool designed to mine security patterns from library usages in open-source software projects. The overall goal is to automatically map [abstract security patterns](https://securitypatterns.distrinet-research.be/patterns/) to concrete code examples, via searching for security library usage patterns in large codebases.
## Prerequisites
1. Tidelift Account and create API Token: To access the Tidelift (now Sonar) LibrariesIO API, you need to create an account on [Tidelift](https://tidelift.com/). Sign up for a free account if you don't have one already. After creating an account, navigate to your account settings to generate an API token. This token will be used to authenticate your requests to the LibrariesIO APIs.
2. Github PAT token: For working with GitCrawler submodule, you need to create a Personal Access Token (PAT) on GitHub. Follow these steps to create a PAT:
   - Go to your GitHub account settings.
   - Navigate to "Developer settings" > "Personal access tokens".
   - Click on "Generate new token", provide a name, select the necessary scopes (e.g., `repo`, `read:org`), and generate the token.
   - Copy the generated token and store it securely, as you will need it to authenticate API requests made by the GitCrawler submodule.
3. Docker and Docker Compose: Make sure you have [Docker engine](https://docs.docker.com/engine/) and [Docker Compose](https://docs.docker.com/compose/install/) installed to run independent submodules from SecPat successfully, including Zoekt for code search.

## Installation
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

## Running and building SecPat
This section describes how to run the two main functionalities of SecPat: mining mutual dependent repositories and extracting library-usage patterns. These functionalities are implemented as separate services in the `docker-compose.yml` file. 
### Mine Mutual Dependent Repositories
Start with a target security pattern you want to mine, for example,[ password-based authentication](https://securitypatterns.distrinet-research.be/patterns/01_01_002__authentication_pwd/), [session-based access control](https://securitypatterns.distrinet-research.be/patterns/01_01_006__session_based_access_control/), etc. One of the two main functionalities of SecPat is to mine mutual dependent repositories for a given set of libraries corresponding to the  target security pattern.
It is denoted as the `security_pattern_miner` service in the `docker-compose.yml` file.
To run this functionality, follow these steps:
```bash
docker compose up --build --force-recreate security_pattern_miner
```
This command will build and start the `security_pattern_miner` service, which will do the following:
1. Use the LibrariesIO API to find mutual dependent repositories' metadata for the specified security libraries. The libraries named can be modified via the `dependencies` field in the corresponding `./src/context_retriever/queries_library/python/fastapi/patterns/{pattern_name}.yaml` YAML file, for example:
```yaml
dependencies:
  - fastapi
  - passlib
  - bcrypt
```
1. Clone the identified repositories using the GitCrawler submodule.
The cloned repositories will be stored in the `build/volumes/data/cloned_repos` directory. While the metadata from LibrariesIO will be stored in the `build/volumes/data/dependent_repos_info` directory, stored in a JSONL file named `{language}_{package_manager}_mutual_dependent_{package#1}_{package#2}.jsonl`.
### Index Cloned Repositories
Before extracting library-usage patterns, you need to index the cloned repositories using Zoekt.
To do this, run the following command:
```bash
docker compose up --build zoekt_indexer
```
This command will build and start the `zoekt_indexer` service, which will index the cloned repositories stored in the `build/volumes/data/cloned_repos` directory.
The built Zoekt index will be stored in the `build/volumes/data/zoekt/index_data` directory.
1. After indexing is complete, you can start the web server to interact with the Zoekt index:
```bash
docker compose up --build zoekt_webserver
```
This command will build and start the `zoekt_webserver` service, which provides a web interface for interacting with the Zoekt index, accessible at `http://localhost:6070`.
A `/search` endpoint is also available for programmatic access to the Zoekt index, which will be required for the next step of extracting library-usage patterns.

### Extract Library-Usage Patterns
The second main functionality of SecPat is to extract library-usage patterns from an indexed set of repositories.
To run this functionality, follow these steps:
```bash
docker compose up --build --force-recreate security_pattern_extractor
```
This command will build and start the `security_pattern_extractor` service, which will do the following:
1. Use the module `QueriesLoader` to load a pre-defined set of code search queries for the specified security libraries, corresponding to their implementation of security patterns. These queries are stored in the same YAML files used in the previous step, which represent particular rule of implementation for each component role composing the target security pattern.
For example, with the `password-based authentication` pattern, the queries might include:
```yaml
roles:
  enforcer:
    description: "Ensures the requested action is only performed if the Subject is successfully authenticated"
    queries:
      - query: "HTTPBasic Depends HTTPBasicCredentials"
        description: "Files implementing HTTP Basic authentication"

  verification_manager:
    description: "Responsible to collect inputs necessary to verify a Subject's password"
    queries:
      - query: "CryptContext verify"
        description: "Files with password verification context"
      - query: "pwd_context verify plain_password  hashed_password "
        description: "Direct password verification calls"
      - query: "bcrypt checkpw password encode"
        description: "Bcrypt password checking"
```
2. Execute the loaded queries against the Zoekt index via its `/search` endpoint to find code snippets that match the queries, as well as their surrounding context.
3. Aggregate and store the extracted code snippets and their metadata in the `build/volumes/data/search_results` directory, stored in a JSONL file named `{pattern_name}_{web_framework}_search_results.jsonl`, with each line representing a set of code snippet matching a specific query for a specific role in the target security pattern.

### Results
After running both the `security_pattern_miner` and `security_pattern_extractor` services, you will have:
1. A set of cloned repositories that are mutual dependent on the specified security libraries, stored in the `build/volumes/data/cloned_repos` directory.
2. A set of extracted library-usage patterns corresponding to the specified security pattern, stored in the `build/volumes/data/search_results` directory.
3. Metadata about the mutual dependent repositories, stored in the `build/volumes/data/dependent_repos_info` directory.

The searched contexts can be further analyzed, via runing sample notebooks provided in the `notebooks/`. A working example has been provided in the `notebooks/analyze_results.ipynb` notebook, which answers the questions on how  `password-based authentication` and `verifiable token-based authentication` patterns are fully or partly implemented in practice across mined projects, by measuring the number of successful code search results associated with each role. See the table below:

| Patterns | Role | Count |
|----------|------|-------|
| Password-based authentication | registrar | 47 |
| | hasher | 39 |
| | verification_manager | 37 |
| | comparator | 32 |
| | password_store | 29 |
| | srng | 29 |
| | password_policy | 15 |
| | enforcer | 5 |
| | resetter | 5 |
| | encrypter | 3 |
| Verifiable Token-based Authentication | verifier | 184 |
| | registrar | 143 |
| | token_generator | 123 |
| | enforcer | 74 |
| | cryptography_manager | 61 |
| | key_manager | 13 |

## Contributing
Contributions to SecPat are welcome! If you have any suggestions, bug reports, or feature requests, please open an issue or submit a pull request on this GitHub repository.
We are open to extension of the current set of supported security patterns, programming languages, and package managers. Please refer to the existing code structure and documentation for guidance on how to contribute effectively. Start by adding new YAML query files in the `./src/context_retriever/queries_library/` directory for new security patterns or modifying existing ones.

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details