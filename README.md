# selenium-yaml-core
Selenium bots using YAML

## Running the CLI from source

As long as the dependencies are installed, and you're using Python>=3.6, the CLI can be run directly by using:

```python -m scripts.run_sally```

<sub><sup>Use the `--help` argument for details on the CLI!</sup></sub>


## Todos

- [x] Screenshots should be saved in a folder named for the bot. A bot should have a bot name
- [ ] Fields should be blurrable in screenshots; sensitivity array somehow?
- [x] YAML Cheat Sheet
- [ ] Borders in screenshots around fields being worked on (if any)
- [ ] Repeat Action for repeating steps until a condition is reached
- [ ] Suffix step names with a number if they appear multiple times instead of showing an error
- [ ] Add validation for titles not to have slashes in name since they cause directory saving issues