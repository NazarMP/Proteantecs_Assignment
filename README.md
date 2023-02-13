# Python/Github Assignment

The target of this assignment is to create a small POC using the Github API and the Github actions capabilities.

## Usage
I have configured GitHub actions with repository secrets.
#### Repository secrets should include:  
* TOKEN_GITHUB variable

__I used here the bearer token (Fine-grained personal access tokens granded to view private repos)__


Also, you could modify the repository URL inside the __.github/workflows/main.yml__ file
on the last line:
```
run: python github_stats.py --repo https://github.com/python/cpython --token ${{ secrets.TOKEN_GITHUB }} --format table

or

run: python github_stats.py -r https://github.com/python/cpython -t ${{ secrets.TOKEN_GITHUB }} -f table
```
Change the __--repo__ argument with repository url you want.

And __--format__ with one of existing format styles:
* json
* table

After that action will be scheduled to run the program once a day, at 10:25 AM. Or you could run it manually according to workflow_dispatch.

### If you'd like to run it on your machine or extend some code.
In the project, I used a lot of abstractions. There are 2 files. In the file __shemas.py__ we have pydantic Models for simply serializing and validating data. In the file __github_stats.py__ you could find all logic connected.

#### Code explaining

```python
res = GithubRepository(
    args.repo,
    fetcher=GithubFetcher(
        api_client=GithubRESTClient(
            api_token=os.environ['GITHUB_TOKEN']
        )
    )
).format_as("table")
```
.format_as("table") method calls TableFormat(...).represent()

The first argument in __GithubRepository__ class it's a repository URL. 
After the actual creating an GithubRepository object you should call method format_as with one of existing formats.
Or you could call list(GithubRepository(...).get_data()) and get the list of pydantic objects that is pretty easy to serialize.

## License

[MIT](https://choosealicense.com/licenses/mit/)
